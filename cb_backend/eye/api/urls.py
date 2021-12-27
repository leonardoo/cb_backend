from .views import EventSessionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'event_session', EventSessionViewSet, basename='event_session')
urlpatterns = router.urls
