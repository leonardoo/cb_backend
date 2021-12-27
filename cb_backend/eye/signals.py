from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EventSession
from .tasks import validate_event


@receiver(post_save, sender=EventSession)
def my_handler(sender, instance, created, **kwargs):
    if created:
        validate_event.delay(str(instance.id))
