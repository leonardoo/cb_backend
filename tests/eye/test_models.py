import json
from pathlib import Path

import pytest

from cb_backend.eye.models import EventSessionStatus


@pytest.mark.django_db
def test_validate_event_session(create_event_with_session):
    fixture_json = open(Path(__file__).parent / "fixtures/schema.json", "r")
    fixture_schema = json.loads(fixture_json.read())
    event_session = create_event_with_session({
        "host": "www.consumeraffairs.com",
        "path": "/",
        "element": "chat bubble"
    }, fixture_schema)
    assert event_session.validate_event() is True
    assert event_session.status == EventSessionStatus.VALIDATED
