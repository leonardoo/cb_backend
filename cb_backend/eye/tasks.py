from celery.app import shared_task

from cb_backend.eye.models import EventSession, EventSessionStatus


@shared_task
def validate_event(event_id):
    """
    Get an event_id, get it and try to validate it.
    """
    event = EventSession.objects.select_related("event").filter(pk=event_id).first()
    if not event:
        return
    if event.status != EventSessionStatus.PENDING:
        return
    event.validate_event()
    event.save()

