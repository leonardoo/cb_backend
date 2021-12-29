from datetime import datetime

import pytest

from cb_backend.eye.models import Event, Session, EventSession


@pytest.mark.django_db
def test_create_basic_event(client, create_app_session, create_event):
    event: Event = create_event()
    session: Session = create_app_session.session
    response = client.post(
        '/api/v1/event_session/', data={
            "session_id": str(session.id),
            "category": event.category.name,
            "name": event.name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }, content_type='application/json',
        **{'HTTP_AUTHORIZATION': f'Token {session.created_by.token}'}
    )
    assert response.status_code == 201
    assert EventSession.objects.count() == 1
    event_session = EventSession.objects.first()
    assert event_session.session_id == session.id
    assert event_session.event.category_id == event.category.id
    assert event_session.event_id == event.id


@pytest.mark.django_db
def test_create_event_call_celery_task(client, create_app_session, create_event, mocker):
    task_exec = mocker.patch('cb_backend.eye.tasks.validate_event.delay')
    event: Event = create_event()
    session: Session = create_app_session.session
    response = client.post(
        '/api/v1/event_session/', data={
            "session_id": str(session.id),
            "category": event.category.name,
            "name": event.name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }, content_type='application/json',
        **{'HTTP_AUTHORIZATION': f'Token {session.created_by.token}'}
    )
    assert response.status_code == 201
    assert EventSession.objects.count() == 1
    assert task_exec.called_once


@pytest.mark.django_db
def test_dont_allow_to_user_a_session_from_other_app(client, create_session, create_event, create_application):
    event: Event = create_event()
    session: Session = create_session
    app = create_application()
    response = client.post(
        '/api/v1/event_session/', data={
            "session_id": str(session.id),
            "category": event.category.name,
            "name": event.name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }, content_type='application/json',
        **{'HTTP_AUTHORIZATION': f'Token {app.token}'}
    )
    assert response.status_code == 403
    assert EventSession.objects.count() == 0
