import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime

from .models import InterestSubmission


class InterestSubmissionTable(tables.Table):
    submitted = tables.DateTimeColumn(
        accessor="created_at",
        verbose_name="Submitted",
        orderable=True
    )

    name = tables.Column(
        empty_values=(),
        verbose_name="Name",
        orderable=True,
        linkify=lambda record: reverse("connect_inbox_detail", args=[record.pk]),
    )
    email = tables.EmailColumn(verbose_name="Email", orderable=True)
    phone = tables.Column(verbose_name="Phone", orderable=False)

    interests = tables.Column(empty_values=(), verbose_name="Interests", orderable=False)

    contacted = tables.Column(verbose_name="Contacted", orderable=True)
    contacted_at = tables.DateTimeColumn(
        verbose_name="Contacted At",
        orderable=True
    )

    actions = tables.Column(empty_values=(), verbose_name="", orderable=False)

    class Meta:
        model = InterestSubmission
        template_name = "django_tables2/bootstrap4.html"  # swap to bootstrap5 if needed
        fields = (
            "name",
            "email",
            "phone",
            "submitted",
            "interests",
            "contacted",
            "contacted_at",
        )
        attrs = {"class": "table table-striped table-hover align-middle"}
        empty_text = "No intake records found."

    def render_submitted(self, value):
        dt = localtime(value)
        return dt.strftime("%b %d, %Y")

    def render_name(self, record):
        if record.last_name:
            return f"{record.first_name} {record.last_name}"
        return record.first_name

    def render_interests(self, record):
        count = record.interests.count()
        if count == 0:
            return "0"
        return str(count)

    def render_contacted(self, value):
        if value:
            return mark_safe('<span class="badge bg-success">Yes</span>')
        return mark_safe('<span class="badge bg-warning text-dark">No</span>')

    def render_contacted_at(self, value):
        if not value:
            return mark_safe('<span class="text-muted">—</span>')
        dt = localtime(value)
        return dt.strftime("%b %d, %Y")

    def render_actions(self, record):
        if record.contacted:
            return ""
        url = reverse("connect_inbox_contact", args=[record.pk])
        return format_html(
            '<a class="btn btn-sm btn-outline-success" href="{}">Contacted</a>',
            url
        )
