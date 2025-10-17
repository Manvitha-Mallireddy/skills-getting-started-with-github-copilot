from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # create a shallow copy of participants to restore after each test
    original = {k: v.copy() for k, v in activities.items()}
    yield
    # restore participants lists
    activities.clear()
    activities.update(original)


def test_get_activities():
    client = TestClient(app)
    res = client.get('/activities')
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert 'Chess Club' in data


def test_signup_success_and_duplicate():
    client = TestClient(app)
    email = 'tester@mergington.edu'
    activity = 'Chess Club'

    # Ensure email not already in participants
    assert email not in activities[activity]['participants']

    # Signup should succeed
    res = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert res.status_code == 200
    body = res.json()
    assert 'Signed up' in body.get('message', '')
    assert email in activities[activity]['participants']

    # Duplicate signup should fail with 400
    res2 = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert res2.status_code == 400
    err = res2.json()
    assert 'already signed up' in err.get('detail', '')
