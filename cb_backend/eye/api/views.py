from rest_framework import mixins, viewsets, permissions, exceptions
from rest_framework.authentication import BaseAuthentication, TokenAuthentication

from cb_backend.eye.api.serializers import EventSessionSerializer
from cb_backend.eye.models import Application


class TokenAppAuth(TokenAuthentication):

    model = Application

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.owner.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        return (token.owner, token)


class EventSessionViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """
    API endpoint that allows event sessions to be created.
    """
    serializer_class = EventSessionSerializer
    authentication_classes = (TokenAppAuth,)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        serializer.application = self.request.auth
        return serializer
