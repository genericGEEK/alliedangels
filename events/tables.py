import calendar
import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Event, EventCategory, EventSeries


class EventSeriesTable(tables.Table):
    title = tables.Column(linkify=("series_detail", {"slug": tables.A("slug")}))
    start = tables.Column(empty_values=(), orderable=True, verbose_name="Start")
    recurrence = tables.Column(empty_values=(), orderable=True)
    weekday = tables.Column(empty_values=(), orderable=True)
    category = tables.Column()
    is_active = tables.BooleanColumn(verbose_name="Active")
    actions = tables.Column(
        empty_values=(),
        orderable=False,
        verbose_name="",
        attrs={
            "td": {"class": "text-end"},
            "th": {"class": "text-end"},
        },
    )

    class Meta:
        model = EventSeries
        template_name = "django_tables2/bootstrap5.html"
        fields = ("title", "start", "recurrence", "weekday", "category", "is_active")
        attrs = {"class": "table table-striped table-hover align-middle"}

    def render_start(self, record):
        # Example: 2026-01-22 @ 7:30 PM (America/Denver isn't in model, so just date + time)
        return f"{record.start_date:%b %-d, %Y} {record.start_time.strftime('%-I:%M %p')}"

    def render_recurrence(self, record):
        """
        Uses the choices label when possible, but enhances it with week-of-month info.
        Examples:
          Weekly
          Biweekly
          Monthly (2nd)
          Monthly (last)
        """
        base = getattr(record, "get_recurrence_display", None)
        label = base() if callable(base) else (record.recurrence or "")

        if record.week_of_month:
            wom_map = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "last"}
            suffix = wom_map.get(record.week_of_month, str(record.week_of_month))
            # Only append for patterns where week_of_month is meaningful (monthly rules etc.)
            return f"{label} ({suffix})"

        return label

    def render_weekday(self, record):
        """
        Human readable weekday and monthly pattern.
        Examples:
          Monday
          Tuesday
          (blank) → —
          1st Monday
          last Friday
        """
        if record.weekday is None:
            return "—"

        day_name = calendar.day_name[int(record.weekday)]  # 0=Monday ... 6=Sunday

        if record.week_of_month:
            wom_map = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "last"}
            prefix = wom_map.get(record.week_of_month, str(record.week_of_month))
            return f"{prefix} {day_name}"

        return day_name

    def render_actions(self, record):
        edit_url = reverse("series_edit", kwargs={"slug": record.slug})
        delete_url = reverse("series_delete", kwargs={"slug": record.slug})

        return format_html(
            """
            <a class="btn btn-sm btn-all-warning" href="{}">Edit</a>
            <a class="btn btn-sm btn-all-danger" href="{}">Delete</a>
            """,
            edit_url,
            delete_url,
        )


class EventTable(tables.Table):
    title = tables.Column(
        verbose_name="Title",
        linkify=lambda record: reverse("event_manage_detail", args=[record.slug]),
    )

    start = tables.DateTimeColumn(format="M j, Y g:i A", verbose_name="Start")
    status = tables.Column(verbose_name="Status")
    visibility = tables.Column(verbose_name="Visibility")

    series = tables.Column(verbose_name="Series")
    category = tables.Column(verbose_name="Category")

    actions = tables.Column(
        empty_values=(),
        orderable=False,
        verbose_name="",
        attrs={
            "td": {"class": "text-end"},
            "th": {"class": "text-end"},
        },
    )

    class Meta:
        model = Event
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "title",
            "start",
            "status",
            "visibility",
            "series",
            "category",
        )
        attrs = {"class": "table table-striped table-hover align-middle"}
        empty_text = "No events found."

    def render_status(self, record):
        # Adjust badge colors to match your theme
        if record.status == "published":
            cls = "badge bg-success"
        elif record.status == "draft":
            cls = "badge bg-secondary"
        elif record.status == "cancelled":
            cls = "badge bg-danger"
        else:
            cls = "badge bg-warning text-dark"
        return format_html('<span class="{}">{}</span>', cls, record.get_status_display())

    def render_visibility(self, record):
        if record.visibility == "PUBLIC":
            cls = "badge bg-all-primary"
        else:
            cls = "badge bg-light text-dark border"
        return format_html('<span class="{}">{}</span>', cls, record.get_visibility_display())

    def render_actions(self, record):
        edit_url = reverse('event_manage_edit', args=[record.slug])
        delete_url = reverse('event_manage_delete', args=[record.slug])
        return format_html(
            """
            <a class="btn btn-sm btn-all-warning" href="{}">Edit</a>
            <a class="btn btn-sm btn-all-danger" href="{}">Delete</a>
            """,
            edit_url,
            delete_url,
        )


class EventCategoryTable(tables.Table):
    name = tables.Column(
        verbose_name="Category"
    )
    slug = tables.Column(verbose_name="Slug")
    actions = tables.Column(
        empty_values=(),
        orderable=False,
        verbose_name="",
        attrs={
            "td": {"class": "text-end"},
            "th": {"class": "text-end"},
        },
    )

    class Meta:
        model = EventCategory
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "slug")
        attrs = {"class": "table table-striped table-hover align-middle"}
        empty_text = "No categories found."

    def render_actions(self, record):
        edit_url = reverse("category_edit", args=[record.slug])
        delete_url = reverse("category_delete", args=[record.slug])

        return format_html(
            """
            <a class="btn btn-sm btn-all-warning me-1" href="{}">Edit</a>
            <a class="btn btn-sm btn-all-danger" href="{}">Delete</a>
            """,
            edit_url,
            delete_url,
        )