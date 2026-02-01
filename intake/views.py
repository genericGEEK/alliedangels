from django_tables2 import SingleTableView

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, TemplateView, FormView, View, DetailView
from .forms import InterestForm
from .models import InterestSubmission
from .tables import InterestSubmissionTable
from extras.mixins import PageMetaMixin


class ConnectView(PageMetaMixin, FormView):
    form_class = InterestForm
    template_name = "intake/connect.html"
    is_current = "connect"
    page_title = "Connect"

    def get_success_url(self):
        return reverse("connect_thanks")

    def form_valid(self, form):
        # 1) Save to DB
        submission = form.save(commit=True)

        # 2) Build context for emails
        interests_list = list(submission.interests.values_list("name", flat=True))
        context = {
            "first_name": submission.first_name,
            "last_name": submission.last_name,
            "email": submission.email,
            "phone": submission.phone,
            "interests": interests_list,
            "interests_display": ", ".join(interests_list) if interests_list else "None selected",
            "message": submission.message,
            "submitted_at": submission.created_at,
        }

        # 3) Render internal notification email (admin)
        admin_html = render_to_string("intake/emails/intake_notification.html", context)
        admin_text = render_to_string("intake/emails/intake_notification.txt", context)

        # 4) Render user confirmation email (user)
        user_html = render_to_string("intake/emails/intake_confirmation.html", context)
        user_text = render_to_string("intake/emails/intake_confirmation.txt", context)

        # 5) Send emails (admin + user)
        try:
            # Admin notification (optional but recommended)
            admin_to = getattr(settings, "DEFAULT_EMAIL_ADDRESS", None)
            if admin_to:
                admin_email = EmailMultiAlternatives(
                    subject=f"New ALL Intake: {submission.first_name} {submission.last_name or ''}".strip(),
                    body=admin_text,
                    from_email=None,  # uses DEFAULT_FROM_EMAIL
                    to=[admin_to],
                    reply_to=[submission.email],
                )
                admin_email.attach_alternative(admin_html, "text/html")
                admin_email.send(fail_silently=False)

            # User confirmation
            user_email = EmailMultiAlternatives(
                subject="We received your message",
                body=user_text,
                from_email=None,  # uses DEFAULT_FROM_EMAIL
                to=[submission.email],
            )
            user_email.attach_alternative(user_html, "text/html")
            user_email.send(fail_silently=False)

            #messages.success(self.request, "Thanks for reaching out. We will review what you shared and follow up with next steps based on the interests you selected.")
        except Exception:
            # Optional: you can choose whether to keep the DB record or delete it on failure.
            # If you want rollback behavior, tell me and I’ll show the clean way.
            messages.error(self.request, "There was an error submitting your form. Please try again later.")
            return self.form_invalid(form)

        return super().form_valid(form)


class ConnectThanksView(PageMetaMixin, TemplateView):
    template_name = "intake/connect_thanks.html"
    is_current = 'connect'
    page_title = 'Thanks'


@method_decorator(staff_member_required, name='dispatch')
class InterestSubmissionListView(PageMetaMixin, SingleTableView):
    model = InterestSubmission
    table_class = InterestSubmissionTable
    template_name = 'intake/submission_list.html'
    is_current = 'connect'
    page_title = 'Connect Inbox'
    paginate_by = 25

    def get_queryset(self):
        # Newest first
        return (
            InterestSubmission.objects
            .all()
            .order_by('-created_at')
            .prefetch_related('interests')
        )


class InterestSubmissionDetailView(PageMetaMixin, DetailView):
    model = InterestSubmission
    template_name = 'intake/submission_detail.html'
    context_object_name = 'record'
    is_current = 'connect'
    #page_title = 'Intake Detail'

    def get_queryset(self):
        # So interests are available without extra queries
        return super().get_queryset().prefetch_related("interests")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.get_full_name()
        context["breadcrumbs"] = [
            {"label": "Connect Inbox", "url": reverse("connect_inbox")},
            {"label": self.object.get_full_name(), "url": None},
        ]
        return context



class InterestSubmissionConfirmView(PageMetaMixin, TemplateView):
    template_name = 'intake/contacted_confirm.html'
    is_current = 'connect'
    page_title = 'Confirm Contacted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # this triggers PageMetaMixin
        context["record"] = get_object_or_404(InterestSubmission, pk=self.kwargs["pk"])
        return context

    def post(self, request, pk):
        record = get_object_or_404(InterestSubmission, pk=pk)

        # Idempotent: if already contacted, do nothing and return
        if not record.contacted:
            record.contacted = True
            record.contacted_at = timezone.now()
            record.save(update_fields=["contacted", "contacted_at"])
            messages.success(request, f"{record} marked as contacted.")
        else:
            messages.info(request, f"{record} was already marked as contacted.")

        return redirect("connect_inbox")  # change to your inbox list route name

