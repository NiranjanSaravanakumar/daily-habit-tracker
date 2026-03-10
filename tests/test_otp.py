"""
test_otp.py – Tests for the OTP verification page and flow.
"""

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from tests.pages.otp_page import OtpPage
from tests.pages.signup_page import SignupPage
from tests.utils.test_data import OTP_URL, SIGNUP_URL, LOGIN_URL, NEW_USER


@pytest.mark.otp
class TestOtpPage:
    """OTP page test suite."""

    def test_otp_page_loads_with_email(self, page):
        """OTP page should render with OTP input and verify button when email is set."""
        # Set otp_email in localStorage so the page doesn't redirect
        page.goto(SIGNUP_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("() => localStorage.setItem('otp_email', 'test@example.com')")

        page.goto(OTP_URL)
        page.wait_for_load_state("networkidle")

        otp = OtpPage(page)
        assert otp.is_loaded(), "OTP page did not load correctly"
        assert otp.otp_input.is_visible()
        assert otp.submit_btn.is_visible()

    def test_otp_page_title(self, page):
        """Page title should indicate OTP verification."""
        page.goto(SIGNUP_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("() => localStorage.setItem('otp_email', 'test@example.com')")

        page.goto(OTP_URL)
        page.wait_for_load_state("networkidle")

        assert "Verify OTP" in page.title() or "OTP" in page.title()

    def test_otp_no_email_redirects_to_signup(self, page):
        """If no otp_email in localStorage, should redirect to signup."""
        # Make sure localStorage is clean
        page.goto(SIGNUP_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("() => localStorage.removeItem('otp_email')")

        page.goto(OTP_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        assert "signup" in page.url.lower(), \
            f"Expected redirect to signup, but URL is {page.url}"

    def test_otp_invalid_code_shows_error(self, page, mock_db):
        """Submitting an invalid OTP should show an error message."""
        email = "otpui@example.com"
        otp_code = "111111"
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

        # Seed user + OTP in DB
        conn = sqlite3.connect(mock_db)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("OTP UI User", email, "dummyhash"),
        )
        cur.execute(
            "INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)",
            (email, otp_code, expires_at),
        )
        conn.commit()
        conn.close()

        # Navigate and set email in localStorage
        page.goto(SIGNUP_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate(f"() => localStorage.setItem('otp_email', '{email}')")

        page.goto(OTP_URL)
        page.wait_for_load_state("networkidle")

        otp = OtpPage(page)
        otp.verify("999999")  # wrong code

        alert_text = otp.get_alert_text()
        assert "invalid" in alert_text.lower(), f"Expected error about invalid OTP, got: {alert_text}"
        assert otp.get_alert_type() == "error"

    def test_otp_success_redirects_to_login(self, page, mock_db):
        """Submitting the correct OTP should verify email and redirect to login."""
        email = "otpgood@example.com"
        otp_code = "654321"
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()

        conn = sqlite3.connect(mock_db)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("OTP Good User", email, "dummyhash"),
        )
        cur.execute(
            "INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)",
            (email, otp_code, expires_at),
        )
        conn.commit()
        conn.close()

        page.goto(SIGNUP_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate(f"() => localStorage.setItem('otp_email', '{email}')")

        page.goto(OTP_URL)
        page.wait_for_load_state("networkidle")

        otp = OtpPage(page)
        otp.verify(otp_code)

        alert_text = otp.get_alert_text()
        assert "verified" in alert_text.lower() or "success" in alert_text.lower()
        assert otp.get_alert_type() == "success"

        # Should redirect to login
        page.wait_for_url("**/login.html*", timeout=5000)
        assert "login" in page.url.lower()

    def test_otp_has_signup_link(self, page):
        """OTP page should have a link back to signup."""
        page.goto(SIGNUP_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate("() => localStorage.setItem('otp_email', 'test@example.com')")

        page.goto(OTP_URL)
        page.wait_for_load_state("networkidle")

        otp = OtpPage(page)
        assert otp.signup_link.is_visible()
        assert otp.signup_link.get_attribute("href") == "signup.html"
