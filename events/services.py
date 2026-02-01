from datetime import date, datetime, timedelta
from django.utils import timezone

from .choices import Recurrence
from .models import Event
from .utils import nth_weekday_of_month


def generate_weekly_events(series, from_date, to_date):
    current = from_date

    while current <= to_date:
        if current.weekday() == series.weekday:
            start_dt = timezone.make_aware(
                datetime.combine(current, series.start_time)
            )

            Event.objects.get_or_create(
                series=series,
                start=start_dt,
                defaults={
                    "title": series.title,
                    "summary": series.description,
                    "content": series.content,
                    "end": start_dt + timedelta(minutes=series.default_duration_minutes),
                    "location_name": series.default_location,
                    "address": series.default_address,
                    "category": series.category,
                    "status": "published",
                    "visibility": series.visibility,
                    "image": series.image,
                },
            )

        current += timedelta(days=1)


def generate_monthly_events(series, from_date, to_date):
    """
    Generates one event per month using:
    - series.weekday (0=Mon..6=Sun)
    - series.week_of_month (1..4, 5=last)
    """
    if series.weekday is None or series.week_of_month is None:
        return  # nothing to generate

    year, month = from_date.year, from_date.month

    # loop months until we pass to_date
    while date(year, month, 1) <= to_date:
        event_day = nth_weekday_of_month(year, month, series.weekday, series.week_of_month)

        if event_day and from_date <= event_day <= to_date:
            start_dt = timezone.make_aware(datetime.combine(event_day, series.start_time))

            Event.objects.get_or_create(
                series=series,
                start=start_dt,
                defaults={
                    "title": series.title,
                    "summary": series.description,
                    "content": series.content,
                    "end": start_dt + timedelta(minutes=series.default_duration_minutes),
                    "location_name": series.default_location,
                    "address": series.default_address,
                    "category": series.category,
                    "status": "published",
                    "visibility": series.visibility,
                    "image": series.image,
                },
            )

        # advance month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1


def get_generation_start_date(series):
    last_event = (
        series.events
        .order_by("-start")
        .first()
    )

    if last_event:
        return last_event.start.date() + timedelta(days=1)

    return series.start_date


def generate_next_90_days(series, days=90):
    """
    Generates occurrences from the proper start date through the next `days`.
    Safe to call multiple times because generators use get_or_create.
    """
    from_date = get_generation_start_date(series)
    to_date = from_date + timedelta(days=days)

    if series.recurrence == Recurrence.REC_WEEKLY:
        generate_weekly_events(series, from_date, to_date)

    elif series.recurrence == Recurrence.REC_MONTHLY:
        generate_monthly_events(series, from_date, to_date)


def apply_series_defaults_to_future_events(series, *, sync_image=False):
    update_kwargs = dict(
        category=series.category,
        location_name=series.default_location,
        address=series.default_address,
        visibility=series.visibility,
        content=series.content,

    )

    if sync_image:
        update_kwargs["image"] = series.image  # can be set or cleared

    return series.events.filter(start__gte=timezone.now()).update(**update_kwargs)