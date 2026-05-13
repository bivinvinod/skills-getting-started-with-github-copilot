"""
Test suite for the High School Management System API

Tests use the Arrange-Act-Assert pattern and reset the global activity state
between tests.
"""

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activity_names = set(INITIAL_ACTIVITIES.keys())

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert set(response.json().keys()) == expected_activity_names

    def test_get_activities_contains_activity_details(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")
        activities_data = response.json()

        # Assert
        assert response.status_code == 200
        assert activities_data[activity_name]["description"] == "Learn strategies and compete in chess tournaments"
        assert activities_data[activity_name]["max_participants"] == 12
        assert "michael@mergington.edu" in activities_data[activity_name]["participants"]


class TestSignupForActivity:
    def test_signup_for_activity_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_duplicate_student(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    def test_remove_participant_success(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_remove_nonexistent_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "missing@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"

    def test_remove_from_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
