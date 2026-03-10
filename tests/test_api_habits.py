"""
test_api_habits.py – Direct HTTP-level tests for the habit management API endpoints.

These tests use `requests` to hit the Node.js test server directly,
covering all branches in habitController.js and authMiddleware.js.
"""

import pytest
import requests

from tests.utils.test_data import BASE_URL, VERIFIED_USER

API_AUTH = f"{BASE_URL}/api/auth"
API_HABITS = f"{BASE_URL}/api/habits"


def _get_auth_token() -> str:
    """Login with the seeded verified user and return the JWT token."""
    res = requests.post(f"{API_AUTH}/login", json={
        "email": VERIFIED_USER["email"],
        "password": VERIFIED_USER["password"],
    })
    return res.json()["token"]


def _auth_headers(token: str) -> dict:
    """Return headers with Bearer token."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


@pytest.mark.api
class TestHabitAuthGuard:
    """Tests for authMiddleware.js protecting habit endpoints."""

    def test_get_habits_no_token(self, mock_db):
        """Accessing habits without token should return 401."""
        res = requests.get(API_HABITS)
        assert res.status_code == 401
        assert "no token" in res.json()["error"].lower() or "denied" in res.json()["error"].lower()

    def test_get_habits_invalid_token(self, mock_db):
        """Accessing habits with bogus token should return 401."""
        res = requests.get(API_HABITS, headers={
            "Authorization": "Bearer invalid.jwt.token",
        })
        assert res.status_code == 401
        assert "invalid" in res.json()["error"].lower() or "expired" in res.json()["error"].lower()

    def test_get_habits_malformed_auth_header(self, mock_db):
        """Auth header without 'Bearer ' prefix should return 401."""
        res = requests.get(API_HABITS, headers={
            "Authorization": "Token abcdef",
        })
        assert res.status_code == 401


@pytest.mark.api
class TestApiGetHabits:
    """API tests for GET /api/habits."""

    def test_get_habits_success(self, mock_db):
        """Should return seeded habits for the authenticated user."""
        token = _get_auth_token()
        res = requests.get(API_HABITS, headers=_auth_headers(token))
        assert res.status_code == 200
        habits = res.json()["habits"]
        assert len(habits) == 3
        names = [h["habit_name"] for h in habits]
        assert "Exercise" in names
        assert "Reading" in names
        assert "Drink Water" in names


@pytest.mark.api
class TestApiAddHabit:
    """API tests for POST /api/habits."""

    def test_add_habit_success(self, mock_db):
        """Adding a habit should return 201 with the new habit."""
        token = _get_auth_token()
        res = requests.post(API_HABITS, headers=_auth_headers(token), json={
            "habit_name": "Meditate",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["habit"]["habit_name"] == "Meditate"
        assert "id" in data["habit"]

    def test_add_habit_empty_name(self, mock_db):
        """Empty habit name should return 400."""
        token = _get_auth_token()
        res = requests.post(API_HABITS, headers=_auth_headers(token), json={
            "habit_name": "",
        })
        assert res.status_code == 400
        assert "required" in res.json()["error"].lower()

    def test_add_habit_whitespace_name(self, mock_db):
        """Whitespace-only habit name should return 400."""
        token = _get_auth_token()
        res = requests.post(API_HABITS, headers=_auth_headers(token), json={
            "habit_name": "   ",
        })
        assert res.status_code == 400

    def test_add_habit_no_body(self, mock_db):
        """Missing habit_name field should return 400."""
        token = _get_auth_token()
        res = requests.post(API_HABITS, headers=_auth_headers(token), json={})
        assert res.status_code == 400


@pytest.mark.api
class TestApiDeleteHabit:
    """API tests for DELETE /api/habits/:id."""

    def test_delete_habit_success(self, mock_db):
        """Deleting an owned habit should return 200."""
        token = _get_auth_token()
        # Get habit IDs first
        habits = requests.get(API_HABITS, headers=_auth_headers(token)).json()["habits"]
        habit_id = habits[0]["id"]

        res = requests.delete(f"{API_HABITS}/{habit_id}", headers=_auth_headers(token))
        assert res.status_code == 200
        assert "deleted" in res.json()["message"].lower()

        # Verify it's gone
        remaining = requests.get(API_HABITS, headers=_auth_headers(token)).json()["habits"]
        assert len(remaining) == len(habits) - 1

    def test_delete_habit_not_found(self, mock_db):
        """Deleting a nonexistent habit should return 404."""
        token = _get_auth_token()
        res = requests.delete(f"{API_HABITS}/99999", headers=_auth_headers(token))
        assert res.status_code == 404
        assert "not found" in res.json()["error"].lower()


@pytest.mark.api
class TestApiCompleteHabit:
    """API tests for POST /api/habits/:id/complete."""

    def test_complete_habit_toggle_on(self, mock_db):
        """Completing a habit should return completed=true."""
        token = _get_auth_token()
        habits = requests.get(API_HABITS, headers=_auth_headers(token)).json()["habits"]
        habit_id = habits[0]["id"]

        res = requests.post(f"{API_HABITS}/{habit_id}/complete", headers=_auth_headers(token))
        assert res.status_code == 200
        assert res.json()["completed"] is True

    def test_complete_habit_toggle_off(self, mock_db):
        """Completing a habit twice should toggle it off."""
        token = _get_auth_token()
        habits = requests.get(API_HABITS, headers=_auth_headers(token)).json()["habits"]
        habit_id = habits[0]["id"]

        # Toggle on
        requests.post(f"{API_HABITS}/{habit_id}/complete", headers=_auth_headers(token))
        # Toggle off
        res = requests.post(f"{API_HABITS}/{habit_id}/complete", headers=_auth_headers(token))
        assert res.status_code == 200
        assert res.json()["completed"] is False

    def test_complete_habit_not_found(self, mock_db):
        """Completing a nonexistent habit should return 404."""
        token = _get_auth_token()
        res = requests.post(f"{API_HABITS}/99999/complete", headers=_auth_headers(token))
        assert res.status_code == 404


@pytest.mark.api
class TestApiProgress:
    """API tests for GET /api/habits/progress."""

    def test_progress_initial(self, mock_db):
        """Progress with no completions should show 0%."""
        token = _get_auth_token()
        res = requests.get(f"{API_HABITS}/progress", headers=_auth_headers(token))
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 3
        assert data["completed"] == 0
        assert data["percentage"] == 0

    def test_progress_after_completion(self, mock_db):
        """Completing one out of three habits should show 33%."""
        token = _get_auth_token()
        habits = requests.get(API_HABITS, headers=_auth_headers(token)).json()["habits"]
        habit_id = habits[0]["id"]

        # Mark one as complete
        requests.post(f"{API_HABITS}/{habit_id}/complete", headers=_auth_headers(token))

        res = requests.get(f"{API_HABITS}/progress", headers=_auth_headers(token))
        data = res.json()
        assert data["completed"] == 1
        assert data["percentage"] == 33
