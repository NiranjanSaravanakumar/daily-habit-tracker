"""
test_signup.py – Tests for the signup flow.
"""

import pytest
from tests.pages.signup_page import SignupPage
from tests.utils.test_data import NEW_USER, VERIFIED_USER, OTP_URL


@pytest.mark.signup
class TestSignup:
    """Signup page test suite."""

    def test_signup_page_loads(self, page):
        """Signup page should render with all form fields."""
        signup = SignupPage(page)
        signup.navigate()

        assert signup.is_loaded(), "Signup page did not load correctly"
        assert signup.name_input.is_visible()
        assert signup.email_input.is_visible()
        assert signup.password_input.is_visible()
        assert signup.submit_btn.is_visible()

    def test_signup_page_title(self, page):
        """Page title should indicate signup."""
        signup = SignupPage(page)
        signup.navigate()

        assert "Sign Up" in page.title()

    def test_successful_signup_redirects_to_otp(self, page):
        """
        Filling in valid details and submitting should show a success
        message and redirect to the OTP verification page.
        """
        signup = SignupPage(page)
        signup.navigate()
        signup.signup(NEW_USER["name"], NEW_USER["email"], NEW_USER["password"])

        # Wait for success alert
        alert_text = signup.get_alert_text()
        assert "OTP" in alert_text or "verify" in alert_text.lower()
        assert signup.get_alert_type() == "success"

        # Should redirect to OTP page
        page.wait_for_url(f"**/{OTP_URL.split('/')[-1]}*", timeout=5000)
        assert "otp" in page.url.lower()

    def test_signup_duplicate_verified_email(self, page):
        """Signing up with an already-verified email should show an error."""
        signup = SignupPage(page)
        signup.navigate()
        signup.signup(
            VERIFIED_USER["name"],
            VERIFIED_USER["email"],
            VERIFIED_USER["password"],
        )

        alert_text = signup.get_alert_text()
        assert "already registered" in alert_text.lower() or "already" in alert_text.lower()
        assert signup.get_alert_type() == "error"

    def test_signup_missing_fields(self, page):
        """Submitting with empty fields should not proceed (HTML validation)."""
        signup = SignupPage(page)
        signup.navigate()

        # Leave fields empty and click submit
        signup.submit()

        # Browser should block due to HTML required attributes —
        # the URL should not change
        assert "signup" in page.url.lower()

    def test_signup_has_login_link(self, page):
        """Signup page should have a link to the login page."""
        signup = SignupPage(page)
        signup.navigate()

        assert signup.login_link.is_visible()
        assert signup.login_link.get_attribute("href") == "login.html"
