# signals.py
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
from .models import EventSeries, Event
from extras.models import ImageAttachment


@receiver(pre_delete, sender=EventSeries)
def series_pre_delete(sender, instance, **kwargs):
    # remove references from events in this series
    instance.events.update(image=None)

@receiver(post_delete, sender=EventSeries)
def series_post_delete(sender, instance, **kwargs):
    img = instance.image
    if img and img.is_orphan():
        img.delete()


@receiver(post_delete, sender=Event)
def event_post_delete(sender, instance: Event, **kwargs):
    # If event is part of a series, never delete shared series image
    if instance.series_id:
        return

    # Standalone event: delete its image if orphaned
    if instance.image and instance.image.is_orphan():
        instance.image.delete()
