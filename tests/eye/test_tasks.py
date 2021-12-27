import json
from pathlib import Path

import pytest

from cb_backend.eye.models import EventSessionStatus
from cb_backend.eye.tasks import validate_event

@pytest.mark.django_db
def test_send_event_session_to_task(create_event_with_session):
    fixture_json = open(Path(__file__).parent / "fixtures/schema.json", "r")
    fixture_schema = json.loads(fixture_json.read())
    event_session = create_event_with_session({
        "host": "www.consumeraffairs.com",
        "path": "/",
        "element": "chat bubble"
    }, fixture_schema)
    validate_event(str(event_session.id))
    event_session.refresh_from_db()
    assert event_session.status == EventSessionStatus.VALIDATED
