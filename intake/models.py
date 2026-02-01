from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from .choices import InterestGroup
from extras.models import TimeStampedModel


class InterestTag(TimeStampedModel):
    """
    Admin-managed interest options (like categories).
    """
    name = models.CharField(max_length=70)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    is_active = models.BooleanField(default=True)

    group = models.CharField(
        max_length=80,
        choices=InterestGroup.INTEREST_CHOICES,
        default=InterestGroup.CONNECT
    )

    class Meta:
        ordering = ["group", "name"]

    def __str__(self):
        return f"{self.get_group_display()}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class InterestSubmission(TimeStampedModel):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80, blank=True)

    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)

    interests = models.ManyToManyField(
        InterestTag,
        blank=True,
        related_name="submissions",
    )

    message = models.TextField(blank=True)

    contacted = models.BooleanField(default=False)
    contacted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.get_full_name()

