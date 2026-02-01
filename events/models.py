from ckeditor.fields import RichTextField

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .choices import EventStatus, EventVisibility, Recurrence, Weekday, WeekOfMonth
from extras.models import TimeStampedModel, ImageAttachment


#
# Event Category
#

class EventCategory(TimeStampedModel):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_list")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


#
# Event Series
#

class EventSeries(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.CharField(max_length=300, blank=True)
    content = RichTextField(blank=True, null=True)
    image = models.ForeignKey(
        ImageAttachment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='event_series',
    )
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="series",
    )
    visibility = models.CharField(
        max_length=20,
        choices=EventVisibility.VISIBILITY_CHOICES,
        default=EventVisibility.VIS_PRIVATE,
    )

    # Defaults that can be used by generated occurrences
    default_location = models.CharField(max_length=300, blank=True)
    default_address = models.CharField(max_length=300, blank=True)
    default_duration_minutes = models.PositiveIntegerField(default=60)

    # Scheduling / recurrence
    start_date = models.DateField(help_text="First date the series can occur on")
    end_date = models.DateField(blank=True, null=True, help_text="Optional end date")
    start_time = models.TimeField(help_text="Start time for each occurrence")

    recurrence = models.CharField(
        max_length=20,
        choices=Recurrence.REC_CHOICES,
        default= Recurrence.REC_WEEKLY
    )

    # If you need “every Monday”, “1st Tuesday”, etc, add a day-of-week field:
    # 0=Monday ... 6=Sunday
    weekday = models.PositiveSmallIntegerField(
        choices=Weekday.WEEKDAY_CHOICES,
        blank=True,
        null=True,
        help_text="0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun",
    )
    week_of_month = models.PositiveSmallIntegerField(
        choices=WeekOfMonth.WEEK_OF_MONTH_CHOICES,
        blank=True,
        null=True,
        help_text="1=first, 2=second, 3=third, 4=fourth, 5=last"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)



#
# Event Occurrence
#

class Event(TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.CharField(max_length=300, blank=True)
    content = RichTextField(null=True, blank=True)

    image = models.ForeignKey(
        ImageAttachment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='event',
    )

    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)

    timezone = models.CharField(max_length=64, default="America/Denver")

    location_name = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=300, blank=True)

    is_online = models.BooleanField(default=False)
    meeting_url = models.URLField(blank=True)

    registration_url = models.URLField(blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices= EventStatus.STATUS_CHOICES,
        default= EventStatus.STATUS_DRAFT,
        db_index=True,
    )
    visibility = models.CharField(
        max_length=20,
        choices= EventVisibility.VISIBILITY_CHOICES,
        default= EventVisibility.VIS_PRIVATE,
        db_index=True,
    )
    series = models.ForeignKey(
        EventSeries,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="events",
        help_text="If set, this event is an occurence generated from a series",
    )
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_posts"
    )
    is_featured = models.BooleanField(default=False)
    requires_registration = models.BooleanField(
        default=False,
        help_text="Check if attendees must register to attend."
    )
    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last date/time attendees can register"
    )

    class Meta:
        ordering = ["start"]
        indexes = [
            models.Index(fields=["status", "start"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.start:%Y-%m-%d})"

    def save(self, *args, **kwargs):
        regenerate_slug = False

        if self.pk:
            # Existing object — check if title changed
            old = Event.objects.filter(pk=self.pk).values("title").first()
            if old and old["title"] != self.title:
                regenerate_slug = True
        else:
            # New object
            regenerate_slug = True

        if regenerate_slug:
            base = slugify(self.title)[:200] or "event"
            slug = base
            i = 2
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def is_upcoming(self) -> bool:
        return self.start >= timezone.now()

    def get_absolute_url(self):
        return reverse("aa_event_detail", kwargs={"slug": self.slug})