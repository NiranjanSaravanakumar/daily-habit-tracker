"""
test_login.py – Tests for the login flow.
"""

import pytest
from tests.pages.login_page import LoginPage
from tests.utils.test_data import VERIFIED_USER, INVALID_USER, DASHBOARD_URL


@pytest.mark.login
class TestLogin:
    """Login page test suite."""

    def test_login_page_loads(self, page):
        """Login page should render with email, password, and submit button."""
        login = LoginPage(page)
        login.navigate()

        assert login.is_loaded(), "Login page did not load correctly"
        assert login.email_input.is_visible()
        assert login.password_input.is_visible()
        assert login.submit_btn.is_visible()

    def test_login_page_title(self, page):
        """Page title should indicate login."""
        login = LoginPage(page)
        login.navigate()

        assert "Log In" in page.title()

    def test_successful_login_redirects_to_dashboard(self, page):
        """
        Logging in with the pre-seeded verified user should show a success
        message and redirect to the dashboard.
        """
        login = LoginPage(page)
        login.navigate()
        login.login(VERIFIED_USER["email"], VERIFIED_USER["password"])

        # Wait for success alert
        alert_text = login.get_alert_text()
        assert "successful" in alert_text.lower()
        assert login.get_alert_type() == "success"

        # Should redirect to dashboard
        page.wait_for_url(f"**/{DASHBOARD_URL.split('/')[-1]}*", timeout=5000)
        assert "dashboard" in page.url.lower()

    def test_login_invalid_email(self, page):
        """Logging in with an unregistered email should show an error."""
        login = LoginPage(page)
        login.navigate()
        login.login(INVALID_USER["email"], INVALID_USER["password"])

        alert_text = login.get_alert_text()
        assert "invalid" in alert_text.lower()
        assert login.get_alert_type() == "error"

    def test_login_wrong_password(self, page):
        """Logging in with a wrong password should show an error."""
        login = LoginPage(page)
        login.navigate()
        login.login(VERIFIED_USER["email"], "totally_wrong_password")

        alert_text = login.get_alert_text()
        assert "invalid" in alert_text.lower()
        assert login.get_alert_type() == "error"

    def test_login_has_signup_link(self, page):
        """Login page should have a link to the signup page."""
        login = LoginPage(page)
        login.navigate()

        assert login.signup_link.is_visible()
        assert login.signup_link.get_attribute("href") == "signup.html"
