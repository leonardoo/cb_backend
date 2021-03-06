import uuid

from django.conf import settings
from django.db import models

from cb_backend.eye.validators import Validator


class ApplicationGroup(models.Model):
    """
    This model is used to group applications. so this can share sessions or other data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Application(models.Model):
    """
    This model is used to store application details
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='applications', on_delete=models.CASCADE)
    group = models.ForeignKey(ApplicationGroup, related_name='applications', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Application, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.id)


class ApplicationSession(models.Model):
    """
    This model is used to store application session details
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, related_name='sessions', on_delete=models.CASCADE)
    session = models.ForeignKey('Session', related_name='applications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class CategoryEvent(models.Model):
    """
    This model is used to store category events
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    """
    This model is used had the the validation of an user event
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(CategoryEvent, related_name='events', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validators = models.JSONField()

    def __str__(self):
        return str(self.id)


class EventSessionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VALIDATED = 'VALIDATED', 'Validated'
    REJECTED = 'REJECTED', 'Rejected'


class EventSession(models.Model):
    """
    This model is used to store event session details
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)
    session = models.ForeignKey(Session, related_name='events', on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name='events', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payload = models.JSONField()
    timestamp = models.DateTimeField()
    status = models.CharField(max_length=10, choices=EventSessionStatus.choices, default=EventSessionStatus.PENDING)
    payload_error = models.JSONField(null=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return str(self.id)

    def validate_event(self):
        """
        This method is used to call the validators in the event, allow to know if the event was
        validated correctly or has been rejected
        """
        if not self.event.validators:
            self.status = EventSessionStatus.REJECTED
            self.payload_error = ['No validators defined']
            return False
        response = Validator.get_validator(self.event, self.payload).validate()
        if response:
            self.status = EventSessionStatus.REJECTED
            self.payload_error = response
            return False
        self.status = EventSessionStatus.VALIDATED
        return True

