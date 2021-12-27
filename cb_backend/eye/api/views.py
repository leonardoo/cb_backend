from rest_framework import mixins, viewsets

from cb_backend.eye.api.serializers import EventSessionSerializer


class EventSessionViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """
    API endpoint that allows event sessions to be created.
    """
    serializer_class = EventSessionSerializer
    permission_classes = []
