from django.db.models import Q
from rest_framework import mixins, viewsets, exceptions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from cb_backend.eye.api.serializers import EventSessionSerializer, ApplicationSessionSerializer
from cb_backend.eye.models import Application, ApplicationSession, Session


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


class ApplicationSessionGetOrCreateView(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint that allows event sessions to be created.
    """
    serializer_class = ApplicationSessionSerializer
    authentication_classes = (TokenAppAuth,)

    def create(self, request, *args, **kwargs):
        app = self.request.auth
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app_session = ApplicationSession.objects.filter(
            session__session_data=serializer.data["session_data"],
        ).filter(
            Q(
                Q(application=app) | Q(application__group_id=app.group_id)
            )
        ).select_related("session").first()
        headers = self.get_success_headers(serializer.data)
        created = False
        session = None
        if not app_session:
            session = Session.objects.create(
                session_data=serializer.data["session_data"],
                created_by=app
            )
            created = True
        if (app_session and str(app_session.application_id) != str(app.id)) or created:
            app_session = ApplicationSession.objects.create(
                application=app,
                session=app_session.session if not created else session
            )
        return Response(
            {
                "session_id": app_session.session_id
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            headers=headers
        )


