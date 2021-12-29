from .views import EventSessionViewSet, ApplicationSessionGetOrCreateView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'event_session', EventSessionViewSet, basename='event_session')
router.register(r'create_session', ApplicationSessionGetOrCreateView, basename='create_session')
urlpatterns = router.urls
