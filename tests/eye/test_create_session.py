import pytest

from cb_backend.eye.models import Session, ApplicationSession


@pytest.fixture
def applications_with_group(create_application_group, create_application, create_session_from_app):
    def get_configuration(session_data=None):
        app = create_application(group=create_application_group)
        app_2 = create_application(group=create_application_group)
        app_session = ApplicationSession.objects.create(
            application=app,
            session=create_session_from_app(app, session_data)
        )
        return {
            'group': create_application_group,
            "apps": [app, app_2],
            "session": app_session.session,
        }
    return get_configuration


@pytest.mark.django_db
def test_create_session(client, create_application):
    app = create_application()
    response = client.post(
        '/api/v1/create_session/', data={
            "session_data": {
                "user_name": "test_user",
                "id": "test_id",
            },
        }, content_type='application/json',
        **{'HTTP_AUTHORIZATION': f'Token {app.token}'}
    )
    assert response.status_code == 201
    assert Session.objects.count() == 1
    assert ApplicationSession.objects.count() == 1
    session = Session.objects.first()
    assert str(response.data['session_id']) == str(session.id)


@pytest.mark.django_db
def test_get_session_when_another_app_same_group_request_same_data(client, applications_with_group):
    session_data = {
        "user_name": "test_user",
        "id": "test_id",
    }
    configurations = applications_with_group(session_data=session_data)
    session = configurations['session']
    app = configurations['apps'][-1]
    response = client.post(
        '/api/v1/create_session/', data={
            "session_data": session_data
        },
        content_type='application/json',
        **{'HTTP_AUTHORIZATION': f'Token {app.token}'}
    )
    assert response.status_code == 200
    assert Session.objects.count() == 1
    assert ApplicationSession.objects.count() == 2
    session = Session.objects.first()
    assert str(response.data['session_id']) == str(session.id)


@pytest.mark.django_db
def test_create_new_session_when_app_not_in_group(client, applications_with_group, create_application):
    session_data = {
        "user_name": "test_user",
        "id": "test_id",
    }
    configurations = applications_with_group(session_data=session_data)
    app = create_application()
    response = client.post(
        '/api/v1/create_session/', data={
            "session_data": session_data
        },
        content_type='application/json',
        **{'HTTP_AUTHORIZATION': f'Token {app.token}'}
    )
    assert response.status_code == 201
    assert Session.objects.count() == 2
    assert ApplicationSession.objects.count() == 2
    session = Session.objects.filter(created_by=app).first()
    assert str(response.data['session_id']) == str(session.id)


@pytest.mark.django_db
def test_create_new_session_when_session_data_change(client, applications_with_group, create_application):
    session_data = {
        "user_name": "test_user",
        "id": "test_id",
    }
    configurations = applications_with_group(session_data=session_data)
    app = configurations['apps'][0]
    session_data['new_data'] = 'new_data_session'
    response = client.post(
        '/api/v1/create_session/', data={
            "session_data": session_data
        },
        content_type='application/json',
        **{'HTTP_AUTHORIZATION': f'Token {app.token}'}
    )
    assert response.status_code == 201
    assert Session.objects.count() == 2
    assert ApplicationSession.objects.count() == 2
    session = Session.objects.filter(created_by=app, session_data=session_data).first()
    assert str(response.data['session_id']) == str(session.id)
