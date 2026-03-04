from fastapi.testclient import TestClient
from src.app import app, activities
import copy
import pytest

client = TestClient(app)
initial_state = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange — restore the in-memory activities before each test
    activities.clear()
    activities.update(copy.deepcopy(initial_state))
    yield


def test_get_activities():
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    assert resp.json() == initial_state


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "new@mergington.edu"
    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = initial_state[activity]["participants"][0]
    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity():
    # Act
    resp = client.post("/activities/NonExistent/signup", params={"email": "someone"})
    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"


def test_unregister_success():
    # Arrange
    activity = "Chess Club"
    email = initial_state[activity]["participants"][0]
    # Act
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_registered():
    # Arrange
    activity = "Chess Club"
    email = "not@mergington.edu"
    # Act
    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student not registered for this activity"


def test_unregister_missing_activity():
    # Act
    resp = client.post("/activities/NonExistent/unregister", params={"email": "someone"})
    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"
