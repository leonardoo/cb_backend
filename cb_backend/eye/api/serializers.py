from django.core.cache import cache
from rest_framework import serializers

from ..constants import (
    SESSION_CACHE_KEY, SESSION_CACHE_TIMEOUT, CATEGORY_CACHE_KEY, CATEGORY_CACHE_TIMEOUT, EVENT_CACHE_KEY,
    EVENT_CACHE_TIMEOUT
)
from ..models import CategoryEvent, Event, EventSession, Session


class EventSessionSerializer(serializers.Serializer):
    """
    Serializer for handling data that the app send to the application and create a new EventSession
    if all is ok.
    """

    session_id = serializers.UUIDField()
    category = serializers.CharField()
    name = serializers.CharField()
    data = serializers.JSONField()
    timestamp = serializers.DateTimeField()

    def validate_session_id(self, value):
        """
        Check if the session_id exists in the database. and if exists save in the cache for future use.
        """
        key = f"{SESSION_CACHE_KEY}_{str(value).replace(' ', '_')}"
        if cache.get(key):
            return value
        session = Session.objects.filter(pk=value).first()
        if not session:
            raise serializers.ValidationError("Session does not exist")
        cache.set(key, value, SESSION_CACHE_TIMEOUT)
        return value

    def validate_category(self, value):
        """
        Check if the category exists in the database. and if exists save in the cache for future use.
        """
        key = f"{CATEGORY_CACHE_KEY}_{value.replace(' ', '_')}"
        if category_id := cache.get(key):
            self.category_id = category_id
            return value
        category = CategoryEvent.objects.filter(name=value).first()
        if not category:
            raise serializers.ValidationError("Category does not exist")
        self.category_id = category.id
        cache.set(key, str(self.category_id), CATEGORY_CACHE_TIMEOUT)
        return value

    def validate(self, data):
        """
        Validate than the basic event data are correct. and if exists save in the cache for future use.
        """
        data = super().validate(data)
        event_name = data.get("name")
        category = data.get("category")
        key = f"{EVENT_CACHE_KEY}_{event_name.replace(' ', '_')}_{category.replace(' ', '_')}"
        if event_id := cache.get(key):
            self.event_id = event_id
            return data
        event = Event.objects.filter(name=event_name, category_id=self.category_id).first()
        if not event:
            raise serializers.ValidationError({"event": "Event does not exist"})
        self.event_id = event.id
        cache.set(key, str(self.event_id), EVENT_CACHE_TIMEOUT)
        return data

    def create(self, validated_data):
        """
        Create a new EventSession and save it in the database.
        """
        event_session = EventSession.objects.create(
            session_id=validated_data.get("session_id"),
            event_id=self.event_id,
            payload=validated_data.get("data"),
            timestamp=validated_data.get("timestamp")
        )
        return validated_data


class ApplicationSessionSerializer(serializers.Serializer):
    """
    Serializer for handle the session data
    """
    session_data = serializers.JSONField()


