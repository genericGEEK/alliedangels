from django.contrib import admin
from .models import SiteSettings, ImageAttachment


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Basics", {"fields": ("site_name", "tagline")}),
        ("Contact", {"fields": ("email", "phone",
                                "address_line1", "address_line2", "city", "state", "postal_code")}),
        ("Social", {"fields": ("facebook_url", "x_url", "instagram_url", "linkedin_url", "youtube_url")}),
        #("Branding", {"fields": ("logo_light", "logo_dark", "favicon")}),
    )

    def has_add_permission(self, request):
        # prevent multiple settings objects
        return not SiteSettings.objects.exists()


@admin.register(ImageAttachment)
class ImageAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "content_type", "object_id", "image", "updated_at")
    list_filter = ("content_type",)
    search_fields = ("object_id", "alt_text", "caption")
