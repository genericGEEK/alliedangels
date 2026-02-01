from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import EventCategory, Event, EventSeries
from extras.models import ImageAttachment



class EventCategoryForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Example: Fundraiser",
        })


class EventForm(forms.ModelForm):
    image_file = forms.ImageField(
        required=False,
        label='Image'
    )
    clear_image = forms.BooleanField(
        required=False,
        label='Remove existing image'
    )

    class Meta:
        model = Event
        fields = [
            # Basics
            "title",
            "slug",
            "summary",
            "content",
            "image_file",

            # Schedule
            "start",
            "end",
            "timezone",

            # Location
            "is_online",
            "location_name",
            "address",
            "meeting_url",

            # Registration
            "requires_registration",
            "registration_url",
            "capacity",
            "registration_deadline",

            # Organization
            "category",
            "series",

            # Publishing
            "status",
            "visibility",
            "is_featured",
            "author",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "summary": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),

            "start": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "registration_deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),

            "timezone": forms.TextInput(attrs={"class": "form-control"}),
            "location_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),

            "meeting_url": forms.URLInput(attrs={"class": "form-control"}),
            "registration_url": forms.URLInput(attrs={"class": "form-control"}),

            "capacity": forms.NumberInput(attrs={"class": "form-control"}),

            "status": forms.Select(attrs={"class": "form-select"}),
            "visibility": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "series": forms.Select(attrs={"class": "form-select"}),
            "author": forms.Select(attrs={"class": "form-select"}),

            "is_online": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "requires_registration": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        title = self.cleaned_data.get("title")

        if not slug and title:
            slug = slugify(title)

        return slug

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing AND image exists, allow clearing
        if self.instance.pk and self.instance.image_id:
            self.show_clear_image = True
        else:
            self.show_clear_image = False
            # Prevent validation noise if you only render clear_image conditionally
            self.fields.pop("clear_image", None)

    def save(self, commit=True):
        instance = super().save(commit=commit)

        image_file = self.cleaned_data.get("image_file")
        clear_image = self.cleaned_data.get("clear_image")

        old_image = None

        if image_file:
            if instance.image_id:
                old_image = instance.image

            ct = ContentType.objects.get_for_model(Event)
            img = ImageAttachment(
                image=image_file,
                content_type=ct,
                object_id=instance.pk,
            )
            try:
                img.full_clean()  # ✅ runs ImageField validators + ImageAttachment.clean()
                img.save()
            except ValidationError as e:
                # attach to the upload field on THIS form
                messages = []
                if hasattr(e, 'message_dict'):
                    messages = e.message_dict.get('image') or e.message_dict.get("__all__") or []
                else:
                    messages = e.messages
                for msg in messages:
                    self.add_error("image_file", msg)
                # stop the save cycle cleanly
                raise forms.ValidationError("Please fix the errors below.")

            instance.image = img
            if commit:
                instance.save(update_fields=["image"])

        elif clear_image:
            if instance.image_id:
                old_image = instance.image
                instance.image = None
                if commit:
                    instance.save(update_fields=["image"])

        if commit and old_image:
            if hasattr(old_image, "is_orphan") and old_image.is_orphan():
                old_image.delete()

        return instance


class EventSeriesForm(forms.ModelForm):
    image_file = forms.ImageField(required=False)
    clear_image = forms.BooleanField(required=False)

    class Meta:
        model = EventSeries
        exclude = ('image',)
        fields = "__all__"  # or list explicitly

        widgets = {
            # ===================== BASICS =====================
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"rows": 2, "class": "form-control"}
            ),

            # ===================== CATEGORY =====================
            "category": forms.Select(attrs={"class": "form-select"}),
            "visibility": forms.Select(attrs={"class": "form-select"}),

            # ===================== DEFAULTS =====================
            "default_location": forms.TextInput(attrs={"class": "form-control"}),
            "default_address": forms.TextInput(attrs={"class": "form-control"}),
            "default_duration_minutes": forms.NumberInput(
                attrs={"class": "form-control", "min": 1}
            ),

            # ===================== SCHEDULING =====================
            # IMPORTANT: these are DateField + TimeField (not datetime)
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "start_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),

            "recurrence": forms.Select(attrs={"class": "form-select"}),

            "weekday": forms.Select(
                attrs={"class": "form-select"}
            ),
            "week_of_month": forms.Select(
                attrs={"class": "form-select"}
            ),

            # ===================== STATUS =====================
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional: placeholders if you have these fields
        if "title" in self.fields:
            self.fields["title"].widget.attrs.setdefault("placeholder", "Series title")
        if "summary" in self.fields:
            self.fields["summary"].widget.attrs.setdefault("placeholder", "Short summary")

        # If editing AND image exists, allow clearing
        if self.instance.pk and self.instance.image:
            self.show_clear_image = True
        else:
            self.show_clear_image = False
            self.fields.pop("clear_image", None)

        # If you DO NOT want the dropdown selector at all, uncomment:
        # self.fields.pop("image", None)

    def save(self, commit=True):
        instance = super().save(commit=commit)

        image_file = self.cleaned_data.get("image_file")
        clear_image = self.cleaned_data.get("clear_image")

        old_image = None

        if image_file:
            if instance.image_id:
                old_image = instance.image

            ct = ContentType.objects.get_for_model(EventSeries)
            img = ImageAttachment.objects.create(
                image=image_file,
                content_type=ct,
                object_id=instance.pk,
            )
            instance.image = img
            if commit:
                instance.save(update_fields=["image"])

        elif clear_image:
            if instance.image_id:
                old_image = instance.image
                instance.image = None
                if commit:
                    instance.save(update_fields=["image"])

        if commit and old_image:
            if hasattr(old_image, "is_orphan") and old_image.is_orphan():
                old_image.delete()

        return instance
