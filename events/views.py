from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView, DeleteView, CreateView, View, DetailView
from django_tables2 import SingleTableView

from .forms import EventCategoryForm, EventForm, EventSeriesForm
from .models import Event, EventSeries, EventCategory
from .services import generate_next_90_days, apply_series_defaults_to_future_events
from .tables import EventTable, EventCategoryTable, EventSeriesTable
from extras.mixins import PageMetaMixin, NextUrlMixin


#
# Event List Public View
#

class EventListView(PageMetaMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    is_current = 'event'
    page_title = 'Community Events'
    context_object_name = 'single_events'
    paginate_by = 2

    def get_queryset(self):
        # One-time events (no series), upcoming
        return (
            Event.objects
            .filter(series__isnull=True, start__gte=timezone.now())
            .order_by("start")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        upcoming_series_events = (
            Event.objects
            .filter(start__gte=timezone.now())
            .order_by("start")
        )

        series_qs = (
            EventSeries.objects
            .filter(is_active=True)
            .prefetch_related(
                Prefetch("events", queryset=upcoming_series_events, to_attr="upcoming_events")
            )
            .order_by("title")
        )

        # Build a list of (series, next_event) pairs
        recurring_next = []
        for series in series_qs:
            next_event = series.upcoming_events[0] if series.upcoming_events else None
            if next_event:
                recurring_next.append((series, next_event))

        context["recurring_next"] = recurring_next
        return context


class EventView(PageMetaMixin, DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'
    is_current = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.title
        context["breadcrumbs"] = [
            {"label": "Community Events", "url": reverse("event_list")},
            {"label": self.object.title, "url": None},
        ]
        return context

#
# Categories
#

class CategoryListView(PageMetaMixin, SingleTableView):
    model = EventCategory
    table_class = EventCategoryTable
    template_name = 'events/category_list.html'
    is_current = 'events'
    page_title = 'Categories'
    paginate_by = 25


class CategoryAddView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, CreateView):
    model = EventCategory
    template_name = 'events/category_add.html'
    form_class = EventCategoryForm
    is_current = 'events'
    page_title = 'New Category'
    default_success_url_name = "category_list"
    success_message = 'Category "%(name)s" was created successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Categories", "url": reverse("category_list")},
            {"label": self.page_title, "url": None},
        ]
        return context


class CategoryEditView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, UpdateView):
    model = EventCategory
    template_name = 'events/category_add.html'
    form_class = EventCategoryForm
    is_current = 'events'
    page_title = 'Edit Category'
    default_success_url_name = "category_list"
    success_message = 'Category "%(name)s" was updated successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Categories", "url": reverse("category_list")},
            {"label": self.page_title, "url": None},
        ]
        return context


class CategoryDeleteView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, DeleteView):
    model = EventCategory
    template_name = 'events/category_confirm_delete.html'
    is_current = 'events'
    page_title = 'Delete Category'
    default_success_url_name = "category_list"
    success_message = 'Category was deleted successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Related objects that will be set to NULL after delete
        events_qs = (
            Event.objects
            .filter(category=self.object)
            .only('id', 'title', 'slug', 'start')
            .order_by('-start')
        )

        series_qs = (
            EventSeries.objects
            .filter(category=self.object)
            .only('id', 'title', 'slug', 'start_date')
            .order_by('title')
        )

        context['related_events_count'] = events_qs.count()
        context['related_events_count'] = series_qs.count()

        #don't dump 500 rows on the page
        context['related_events'] = events_qs[:20]
        context['related_series'] = series_qs[:20]

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Categories", "url": reverse("category_list")},
            {"label": self.page_title, "url": None},
        ]
        return context


#
# Event Management
#

class EventManageListView(PageMetaMixin, SingleTableView):
    model = Event
    table_class = EventTable
    template_name = "events/event_manage_list.html"
    is_current = "events"
    page_title = "Manage Events"
    paginate_by = 25

    def get_queryset(self):
        qs = (
            Event.objects.all()
            .select_related("series", "category", "author")
        )

        # Example: show upcoming first, then past
        # Change ordering if you prefer newest created first instead
        return qs.order_by("start")


class EventManageDetailView(PageMetaMixin, DetailView):
    model = Event
    template_name = 'events/event_manage_detail.html'
    context_object_name = 'event'
    is_current = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.title
        context["breadcrumbs"] = [
            {"label": "Manage Events", "url": reverse("event_manage_list")},
            {"label": self.object.title, "url": None},
        ]
        return context


class EventManageAddView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    is_current = 'events'
    page_title = 'Add Event'
    default_success_url_name = "event_manage_list"
    success_message = 'Event "%(title)s" was created successfully.'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Only prefill on create, not edit
        if not form.instance.pk:
            form.fields["author"].initial = self.request.user

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Manage Events", "url": reverse("event_manage_list")},
            {"label": self.page_title, "url": None},
        ]
        return context


class EventManageEditView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    is_current = 'events'
    page_title = 'Edit Event'
    default_success_url_name = "event_manage_list"
    success_message = 'Event "%(title)s" was updated successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Manage Events", "url": reverse("event_manage_list")},
            {"label": self.page_title, "url": None},
        ]
        return context


class EventManageDeleteView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, DeleteView):
    model = Event
    template_name = "events/event_manage_confirm_delete.html"
    context_object_name = "event"
    is_current = "events"
    page_title = 'Delete Event'
    default_success_url_name = "event_manage_list"
    success_message = 'Event was deleted successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Manage Events", "url": reverse("event_manage_list")},
            {"label": self.page_title, "url": None},
        ]
        return context


#
# Event Series
#

class SeriesListView(PageMetaMixin, SingleTableView):
    model = EventSeries
    table_class = EventSeriesTable
    template_name = "events/event_series_list.html"
    paginate_by = 25
    is_current = 'events'
    page_title = 'Manage Event Series'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by("title")


class SeriesView(PageMetaMixin, DetailView):
    model = EventSeries
    template_name = "events/series_detail.html"
    context_object_name = "series"
    is_current = 'events'
    page_title = 'Edit Event Series'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.object.title
        context["breadcrumbs"] = [
            {"label": "Event Series", "url": reverse("series_list")},
            {"label": self.object.title, "url": None},
        ]
        return context


class SeriesAddView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, CreateView):
    model = EventSeries
    form_class = EventSeriesForm
    template_name = 'events/series_form.html'
    is_current = 'events'
    page_title = 'Add Event Series'
    default_success_url_name = "series_list"
    #success_message = 'Event series "%(title)s" was created successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Manage Event Series", "url": reverse("series_list")},
            {"label": self.page_title, "url": None},
        ]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        generate_next_90_days(self.object, days=90)
        messages.success(self.request, "Series created and events generated for the next 90 days.")
        return response


class SeriesEditView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, UpdateView):
    model = EventSeries
    form_class = EventSeriesForm
    template_name = "events/series_form.html"
    is_current = 'events'
    page_title = 'Edit Event Series'
    default_success_url_name = "series_list"
    success_message = 'Event series "%(title)s" was updated successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Manage Event Series", "url": reverse("series_list")},
            {"label": self.page_title, "url": None},
        ]
        return context

    def form_valid(self, form):
        old_image_id = self.object.image_id
        response = super().form_valid(form)
        sync_image = old_image_id != self.object.image_id
        apply_series_defaults_to_future_events(self.object, sync_image=sync_image)
        messages.success(self.request, "Series updated and future events were synced.")

        return response


class SeriesDeleteView(SuccessMessageMixin, NextUrlMixin, PageMetaMixin, DeleteView):
    model = EventSeries
    template_name = "events/series_confirm_delete.html"
    context_object_name = "series"
    is_current = "events"
    page_title = 'Delete Event Series'
    default_success_url_name = "series_list"
    success_message = 'Event series was deleted successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context["breadcrumbs"] = [
            {"label": "Manage Event Series", "url": reverse("series_list")},
            {"label": self.page_title, "url": None},
        ]
        return context