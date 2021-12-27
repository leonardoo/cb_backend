import pytest
from cb_backend.eye.models import Application, Session, CategoryEvent, EventSession, Event
from cb_backend.users.models import User


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    cache.clear()


@pytest.fixture
def create_user(faker):
    return User.objects.create(
        username=faker.name(),
        email=faker.email(),
        password=faker.password(),
        is_staff=True,
        is_superuser=True,
    )

@pytest.fixture
def create_application(faker, create_user):
    return Application.objects.create(
        name=faker.name(),
        description=faker.text(),
        owner=create_user,
    )


@pytest.fixture
def create_session(faker, create_application):
    return Session.objects.create(
        application=create_application,
    )


@pytest.fixture
def create_category(faker):
    return CategoryEvent.objects.create(
        name=faker.name(),
        description=faker.text(),
    )


@pytest.fixture
def create_event(faker, create_category):
    return Event.objects.create(
        category=create_category,
        name=faker.name(),
        validators=[]
    )


@pytest.fixture
def create_event_with_session(faker, create_session, create_event):
    def get_event(data):
        return EventSession.objects.create(
            session=create_session,
            event=create_event,
            payload=data,
            timestamp=faker.date_time(),

        )
    return get_event
