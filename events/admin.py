from datetime import timedelta

from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .choices import Recurrence
from .models import EventCategory, EventSeries, Event
from .services import generate_next_90_days
from extras.models import ImageAttachment


class ImageAttachmentInline(GenericStackedInline):
    model = ImageAttachment
    extra = 0
    max_num = 1
    can_delete = True
    fields = ("image", "alt_text", "caption")


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(EventSeries)
class EventSeriesAdmin(admin.ModelAdmin):
    inlines = [ImageAttachmentInline]
    list_display = (
        "title",
        "recurrence",
        "weekday",
        "start_date",
        "end_date",
        "start_time",
        "default_duration_minutes",
        "is_active",
        "category",
        "created_at",
        "updated_at",
    )
    list_filter = ("recurrence", "is_active", "category", "weekday")
    search_fields = ("title", "slug", "description", "default_location")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("title",)
    fieldsets = (
        ("Basics", {"fields": ("title", "slug", "description", "content", "category", "is_active")}),
        ("Defaults for generated events", {"fields": ("default_location", "default_duration_minutes")}),
        ("Schedule", {"fields": ("start_date", "end_date", "start_time", "recurrence", "weekday")}),
    )


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            generate_next_90_days(obj, days=90)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [ImageAttachmentInline]
    date_hierarchy = "start"
    list_display = (
        "title",
        "start",
        "end",
        "status",
        "visibility",
        "category",
        "series",
        "is_featured",
        "author",
    )
    list_filter = ("status", "visibility", "category", "series", "is_featured", "is_online")
    search_fields = ("title", "slug", "summary", "location_name", "address")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-start",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # After the Event exists, stamp ownership onto the attachment
        if obj.image:
            ct = ContentType.objects.get_for_model(obj.__class__)
            needs_update = (obj.image.content_type_id != ct.id) or (obj.image.object_id != obj.id)
            if needs_update:
                obj.image.content_type = ct
                obj.image.object_id = obj.id
                obj.image.save(update_fields=["content_type", "object_id"])
