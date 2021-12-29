import pytest
from cb_backend.eye.models import Application, Session, CategoryEvent, EventSession, Event, ApplicationGroup, \
    ApplicationSession
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
def create_application_group(faker, create_user):
    return ApplicationGroup.objects.create(
        name=faker.name(),
        description=faker.text(),
        owner=create_user,
    )

@pytest.fixture
def create_application(faker, create_user):
    def get_app(group=None):
        return Application.objects.create(
            name=faker.name(),
            description=faker.text(),
            owner=create_user,
            group=group,
        )
    return get_app


@pytest.fixture
def create_session(create_application):
    return Session.objects.create(
        created_by=create_application(),
        session_data={},
    )

@pytest.fixture
def create_app_session(create_session):
    session = create_session
    return ApplicationSession.objects.create(
        session=session,
        application=session.created_by,
    )


@pytest.fixture
def create_session_from_app(create_application):
    def get_session(app=None, session_data=None):
        return Session.objects.create(
            created_by=create_application() if not app else app,
            session_data={} if not session_data else session_data,
        )
    return get_session


@pytest.fixture
def create_category(faker):
    return CategoryEvent.objects.create(
        name=faker.name(),
        description=faker.text(),
    )


@pytest.fixture
def create_event(faker, create_category):
    def add_schema(schema=None):
        event = Event.objects.create(
            category=create_category,
            name=faker.name(),
            validators=[] if schema is None else schema,
        )
        return event
    return add_schema


@pytest.fixture
def create_event_with_session(faker, create_session, create_event):
    def get_event(data, schema=None):
        return EventSession.objects.create(
            session=create_session,
            event=create_event(schema),
            payload=data,
            timestamp=faker.date_time(),
        )
    return get_event
