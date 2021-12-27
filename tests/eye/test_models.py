import json
from pathlib import Path

import pytest

from cb_backend.eye.models import EventSessionStatus


@pytest.fixture(scope="module")
def load_schemas():
    schemas = []
    for file_name in ["fixtures/schema.json", "fixtures/schema_2.json"]:
        fixture_json = open(Path(__file__).parent / file_name, "r")
        fixture_schema = json.loads(fixture_json.read())
        schemas.append(fixture_schema)
    return schemas


@pytest.mark.django_db
def test_validate_event_session(create_event_with_session, load_schemas):
    schema = load_schemas[0]
    event_session = create_event_with_session({
        "host": "www.consumeraffairs.com",
        "path": "/",
        "element": "chat bubble"
    }, schema)
    assert event_session.validate_event() is True
    assert event_session.status == EventSessionStatus.VALIDATED

@pytest.mark.django_db
def test_fail_invalid_data_event_session(create_event_with_session, load_schemas):
    schema = load_schemas[0]
    event_session = create_event_with_session({
        "host": "www.consumeraffairs.com",
        "path": "/",
        "element_1": "chat bubble"
    }, schema)
    assert event_session.validate_event() is False
    assert event_session.status == EventSessionStatus.REJECTED


@pytest.mark.django_db
def test_validate_event_session_multiple_schema(create_event_with_session, load_schemas):
    event_session = create_event_with_session({
        "host": "www.consumeraffairs.com",
        "path": "/",
        "form": {
          "first_name": "John",
          "last_name": "Doe"
        }
    }, load_schemas)
    assert event_session.validate_event() is True
    assert event_session.status == EventSessionStatus.VALIDATED
    assert event_session.payload_error is None
