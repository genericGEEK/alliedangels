from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import InterestTag, InterestSubmission


@admin.register(InterestTag)
class InterestTagAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "is_active", "slug")
    list_filter = ("group", "is_active")
    search_fields = ("name", "slug")
    ordering = ("group", "name")
    prepopulated_fields = {"slug": ("name",)}  # safe if slug is blank=True

    fieldsets = (
        (None, {"fields": ("name", "group", "is_active")}),
        ("Slug", {"fields": ("slug",), "classes": ("collapse",)}),
    )


@admin.register(InterestSubmission)
class InterestSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "contacted",
        "created_at",
        "interest_summary",
    )
    list_filter = (
        "contacted",
        "created_at",
        "interests__group",
        "interests",
    )
    search_fields = ("first_name", "last_name", "email", "phone", "message", "notes")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    # Better M2M selector UI
    filter_horizontal = ("interests",)

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Contact info", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("Interests", {"fields": ("interests", "message")}),
        ("Internal tracking", {"fields": ("contacted", "contacted_at", "notes")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def interest_summary(self, obj):
        """
        Compact summary for the changelist.
        """
        tags = obj.interests.select_related(None).all()
        if not tags:
            return "—"
        # Keep it short to avoid a messy list_display
        names = [t.name for t in tags[:3]]
        extra = tags.count() - len(names)
        suffix = f" +{extra}" if extra > 0 else ""
        return ", ".join(names) + suffix

    interest_summary.short_description = "Interests"

    def save_model(self, request, obj, form, change):
        contacted_changed = "contacted" in form.changed_data

        if contacted_changed:
            if obj.contacted and not obj.contacted_at:
                obj.contacted_at = timezone.now()
            if not obj.contacted:
                obj.contacted_at = None

        super().save_model(request, obj, form, change)