"""
test_api_auth.py – Direct HTTP-level tests for the authentication API endpoints.

These tests use `requests` to hit the Node.js test server directly,
covering all branches in authController.js (signup, verifyOtp, login).
"""

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
import requests

from tests.utils.test_data import BASE_URL, VERIFIED_USER, NEW_USER

API = f"{BASE_URL}/api/auth"


@pytest.mark.api
class TestApiSignup:
    """API tests for POST /api/auth/signup."""

    def test_signup_success(self, mock_db):
        """Valid signup should return 200 and OTP message."""
        res = requests.post(f"{API}/signup", json={
            "name": "API Test User",
            "email": "apiuser@example.com",
            "password": "secure123",
        })
        assert res.status_code == 200
        data = res.json()
        assert "otp" in data["message"].lower() or "verify" in data["message"].lower()

    def test_signup_missing_name(self, mock_db):
        """Signup without name should return 400."""
        res = requests.post(f"{API}/signup", json={
            "email": "noname@example.com",
            "password": "secure123",
        })
        assert res.status_code == 400
        assert "required" in res.json()["error"].lower()

    def test_signup_missing_email(self, mock_db):
        """Signup without email should return 400."""
        res = requests.post(f"{API}/signup", json={
            "name": "No Email",
            "password": "secure123",
        })
        assert res.status_code == 400
        assert "required" in res.json()["error"].lower()

    def test_signup_missing_password(self, mock_db):
        """Signup without password should return 400."""
        res = requests.post(f"{API}/signup", json={
            "name": "No Password",
            "email": "nopw@example.com",
        })
        assert res.status_code == 400
        assert "required" in res.json()["error"].lower()

    def test_signup_invalid_email_format(self, mock_db):
        """Signup with malformed email should return 400."""
        res = requests.post(f"{API}/signup", json={
            "name": "Bad Email",
            "email": "not-an-email",
            "password": "secure123",
        })
        assert res.status_code == 400
        assert "email" in res.json()["error"].lower()

    def test_signup_short_password(self, mock_db):
        """Signup with password < 6 chars should return 400."""
        res = requests.post(f"{API}/signup", json={
            "name": "Short Pass",
            "email": "short@example.com",
            "password": "abc",
        })
        assert res.status_code == 400
        assert "6 characters" in res.json()["error"].lower()

    def test_signup_duplicate_verified_email(self, mock_db):
        """Signup with already-verified email should return 409."""
        res = requests.post(f"{API}/signup", json={
            "name": VERIFIED_USER["name"],
            "email": VERIFIED_USER["email"],
            "password": VERIFIED_USER["password"],
        })
        assert res.status_code == 409
        assert "already" in res.json()["error"].lower()

    def test_signup_unverified_email_updates(self, mock_db):
        """Re-signing up with an unverified email should update user and return 200."""
        # First signup (creates unverified user)
        requests.post(f"{API}/signup", json={
            "name": "First Try",
            "email": "retry@example.com",
            "password": "pass123456",
        })
        # Second signup with same email should succeed (update)
        res = requests.post(f"{API}/signup", json={
            "name": "Second Try",
            "email": "retry@example.com",
            "password": "pass789012",
        })
        assert res.status_code == 200


@pytest.mark.api
class TestApiVerifyOtp:
    """API tests for POST /api/auth/verify-otp."""

    def test_verify_otp_success(self, mock_db):
        """Correct OTP should verify user and return 200."""
        email = "otptest@example.com"
        otp_code = "123456"
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

        conn = sqlite3.connect(mock_db)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("OTP User", email, "dummyhash"),
        )
        cur.execute(
            "INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)",
            (email, otp_code, expires_at),
        )
        conn.commit()
        conn.close()

        res = requests.post(f"{API}/verify-otp", json={"email": email, "otp": otp_code})
        assert res.status_code == 200
        assert "verified" in res.json()["message"].lower()

    def test_verify_otp_invalid_code(self, mock_db):
        """Wrong OTP should return 400."""
        email = "otpbad@example.com"
        otp_code = "123456"
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

        conn = sqlite3.connect(mock_db)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("OTP Bad", email, "dummyhash"),
        )
        cur.execute(
            "INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)",
            (email, otp_code, expires_at),
        )
        conn.commit()
        conn.close()

        res = requests.post(f"{API}/verify-otp", json={"email": email, "otp": "999999"})
        assert res.status_code == 400
        assert "invalid" in res.json()["error"].lower()

    def test_verify_otp_expired(self, mock_db):
        """Expired OTP should return 400."""
        email = "otpexpired@example.com"
        otp_code = "654321"
        expires_at = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()

        conn = sqlite3.connect(mock_db)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("OTP Expired", email, "dummyhash"),
        )
        cur.execute(
            "INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)",
            (email, otp_code, expires_at),
        )
        conn.commit()
        conn.close()

        res = requests.post(f"{API}/verify-otp", json={"email": email, "otp": otp_code})
        assert res.status_code == 400
        assert "expired" in res.json()["error"].lower()

    def test_verify_otp_no_record(self, mock_db):
        """OTP for unknown email should return 400."""
        res = requests.post(f"{API}/verify-otp", json={
            "email": "ghost@example.com",
            "otp": "111111",
        })
        assert res.status_code == 400
        assert "no otp" in res.json()["error"].lower()

    def test_verify_otp_missing_fields(self, mock_db):
        """Missing email or OTP should return 400."""
        res = requests.post(f"{API}/verify-otp", json={"email": "x@x.com"})
        assert res.status_code == 400
        assert "required" in res.json()["error"].lower()

        res2 = requests.post(f"{API}/verify-otp", json={"otp": "123456"})
        assert res2.status_code == 400


@pytest.mark.api
class TestApiLogin:
    """API tests for POST /api/auth/login."""

    def test_login_success(self, mock_db):
        """Login with verified user should return 200 + JWT token."""
        res = requests.post(f"{API}/login", json={
            "email": VERIFIED_USER["email"],
            "password": VERIFIED_USER["password"],
        })
        assert res.status_code == 200
        data = res.json()
        assert "token" in data
        assert data["user"]["email"] == VERIFIED_USER["email"]

    def test_login_invalid_email(self, mock_db):
        """Login with unknown email should return 401."""
        res = requests.post(f"{API}/login", json={
            "email": "nobody@example.com",
            "password": "whatever",
        })
        assert res.status_code == 401
        assert "invalid" in res.json()["error"].lower()

    def test_login_wrong_password(self, mock_db):
        """Login with wrong password should return 401."""
        res = requests.post(f"{API}/login", json={
            "email": VERIFIED_USER["email"],
            "password": "totally_wrong",
        })
        assert res.status_code == 401
        assert "invalid" in res.json()["error"].lower()

    def test_login_missing_fields(self, mock_db):
        """Login without email or password should return 400."""
        res = requests.post(f"{API}/login", json={"email": "x@x.com"})
        assert res.status_code == 400
        assert "required" in res.json()["error"].lower()

        res2 = requests.post(f"{API}/login", json={"password": "abc"})
        assert res2.status_code == 400

    def test_login_unverified_user(self, mock_db):
        """Login with unverified account should return 403."""
        # Create an unverified user via signup
        requests.post(f"{API}/signup", json={
            "name": "Unverified",
            "email": "unverified@example.com",
            "password": "pass123456",
        })

        res = requests.post(f"{API}/login", json={
            "email": "unverified@example.com",
            "password": "pass123456",
        })
        assert res.status_code == 403
        assert "not verified" in res.json()["error"].lower()
