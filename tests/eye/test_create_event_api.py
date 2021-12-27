from datetime import datetime

import pytest

from cb_backend.eye.models import Event, Session, EventSession


@pytest.mark.django_db
def test_create_basic_event(client, create_session, create_event):
    event: Event = create_event
    session: Session = create_session
    response = client.post(
        '/api/v1/event_session/', data={
            "session_id": str(session.id),
            "category": event.category.name,
            "name": event.name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }, content_type='application/json'
    )
    assert response.status_code == 201
    assert EventSession.objects.count() == 1
    event_session = EventSession.objects.first()
    assert event_session.session_id == session.id
    assert event_session.event.category_id == event.category.id
    assert event_session.event_id == event.id

