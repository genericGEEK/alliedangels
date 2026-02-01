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

    """def get_breadcrumbs(self):
        return [
            {"label": "Event Details", "url": reverse("programs:list")},
            {"label": "Next item in", "url": None},
        ]"""

class DonatePageView(PageMetaMixin, TemplateView):
    template_name = 'core/donate.html'
    is_current = 'dontations'
    page_title = 'Donations'