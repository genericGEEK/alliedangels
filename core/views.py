from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, TemplateView
from extras.mixins import PageMetaMixin


class HomePageView(PageMetaMixin, TemplateView):
    template_name = 'core/home.html'
    is_current = 'home'
    page_title = 'Home'


class AboutPageView(PageMetaMixin, TemplateView):
    template_name = 'core/about.html'
    is_current = 'about'
    page_title = 'About Us'


class ProgramPageView(PageMetaMixin, TemplateView):
    template_name = 'core/program.html'
    is_current = 'program'
    page_title = 'Programs'


class SupportPageView(PageMetaMixin, TemplateView):
    template_name = 'core/donate.html'
    is_current = 'support'
    page_title = 'Support'


class SupportThanksPageView(PageMetaMixin, TemplateView):
    template_name = 'core/support_thanks.html'
    is_current = 'support'
    page_title = 'Thank You'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Support", "url": reverse("support")},
            {"label": self.page_title, "url": None},
        ]
        return context


class SupportCancelPageView(PageMetaMixin, TemplateView):
    template_name = 'core/support_cancel.html'
    is_current = 'support'
    page_title = 'No Worries'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Support", "url": reverse("support")},
            {"label": self.page_title, "url": None},
        ]
        return context