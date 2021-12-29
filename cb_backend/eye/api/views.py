from django.core.cache import cache
from django.db.models import Q
from rest_framework import mixins, viewsets, exceptions, status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from cb_backend.eye.api.serializers import EventSessionSerializer, ApplicationSessionSerializer
from cb_backend.eye.constants import SESSION_APP_CACHE_KEY, SESSION_APP_CACHE_TIMEOUT
from cb_backend.eye.models import Application, ApplicationSession, Session


class TokenAppAuth(TokenAuthentication):

    """
    Custom TokenAuthentication class to allow for application authentication
    """

    model = Application

    def authenticate_credentials(self, key):
        """
        Override the default authenticate_credentials method to allow for use the application token
        as authentication
        """
        model = self.get_model()
        try:
            token = model.objects.get(token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.owner.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        return (token.owner, token)


class SessionAppPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Check if the app has permission to use the session to save events
        """
        if not hasattr(request, "auth") or not isinstance(request.auth, Application):
            return False
        session_id = request.data.get("session_id")
        if not session_id:
            return False
        key = f"{SESSION_APP_CACHE_KEY}_{str(request.auth.id)}_{str(session_id).replace(' ', '_')}"
        if value := cache.get(key) is not None:
            return value
        filter_q = Q(Q(application=request.auth))
        if request.auth.group_id:
            filter_q.add(Q(group=request.auth.group_id), Q.OR)
        app_session = ApplicationSession.objects.filter(
            session_id=session_id,
        ).filter(
            filter_q
        ).select_related("session").first()
        approved = app_session is not None
        cache.set(key, approved, SESSION_APP_CACHE_TIMEOUT)
        return approved


class EventSessionViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """
    API endpoint that allows event sessions to be created.
    """
    serializer_class = EventSessionSerializer
    authentication_classes = (TokenAppAuth,)
    permission_classes = (SessionAppPermission,)

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        serializer.application = self.request.auth
        return serializer


class ApplicationSessionGetOrCreateView(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint that allows event sessions to be created or be reuse by another app, when the
    session data exists.
    """
    serializer_class = ApplicationSessionSerializer
    authentication_classes = (TokenAppAuth,)

    def create(self, request, *args, **kwargs):
        """
        Create a session if the session data dont exists, otherwise reuse the session
        if the application is allow to use it
        this will return the session_id
        """
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


