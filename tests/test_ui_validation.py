"""
test_ui_validation.py – Additional frontend UI tests for form validation,
error message display, navigation, and dashboard interactions.
"""

import pytest

from tests.pages.login_page import LoginPage
from tests.pages.signup_page import SignupPage
from tests.pages.dashboard_page import DashboardPage
from tests.utils.test_data import (
    VERIFIED_USER, SEEDED_HABITS,
    SIGNUP_URL, LOGIN_URL, DASHBOARD_URL,
)


def _login_and_go_to_dashboard(page) -> DashboardPage:
    """Helper: log in with the seeded user and navigate to the dashboard."""
    login = LoginPage(page)
    login.navigate()
    login.login(VERIFIED_USER["email"], VERIFIED_USER["password"])
    page.wait_for_url("**/dashboard.html*", timeout=5000)
    page.wait_for_load_state("networkidle")
    return DashboardPage(page)


@pytest.mark.ui
class TestSignupValidation:
    """UI validation tests for the signup page."""

    def test_signup_short_password_shows_error(self, page):
        """
        Submitting a password shorter than 6 characters should show
        a client-side validation error (auth.js checks before API call).
        """
        signup = SignupPage(page)
        signup.navigate()

        # Remove HTML5 minlength so the form actually submits to JS handler
        page.evaluate("() => document.getElementById('password').removeAttribute('minlength')")

        signup.signup("Short Pass User", "short@example.com", "abc")

        alert_text = signup.get_alert_text()
        assert "6 characters" in alert_text.lower(), \
            f"Expected short-password error, got: {alert_text}"
        assert signup.get_alert_type() == "error"

    def test_signup_form_retains_state_on_error(self, page):
        """After an error, user should still be on the signup page."""
        signup = SignupPage(page)
        signup.navigate()
        signup.signup(
            VERIFIED_USER["name"],
            VERIFIED_USER["email"],
            VERIFIED_USER["password"],
        )

        # Wait for error
        signup.get_alert_text()
        assert "signup" in page.url.lower()


@pytest.mark.ui
class TestLoginValidation:
    """UI validation tests for the login page."""

    def test_login_error_message_display(self, page):
        """
        Logging in with wrong credentials should display a visible
        error alert with the correct styling.
        """
        login = LoginPage(page)
        login.navigate()
        login.login("nobody@example.com", "wrongpass")

        alert_text = login.get_alert_text()
        assert "invalid" in alert_text.lower()
        assert login.get_alert_type() == "error"

        # Alert should be visible
        assert login.alert.is_visible()
        classes = login.alert.get_attribute("class")
        assert "alert-error" in classes

    def test_login_form_retains_state_on_error(self, page):
        """After login failure, user should still be on login page."""
        login = LoginPage(page)
        login.navigate()
        login.login(VERIFIED_USER["email"], "wrong_password")

        login.get_alert_text()
        assert "login" in page.url.lower()


@pytest.mark.ui
class TestNavigation:
    """Tests for navigation links between pages."""

    def test_signup_to_login_navigation(self, page):
        """Clicking 'Log in' link on signup page should navigate to login."""
        signup = SignupPage(page)
        signup.navigate()

        signup.login_link.click()
        page.wait_for_load_state("networkidle")

        assert "login" in page.url.lower()
        login = LoginPage(page)
        assert login.is_loaded()

    def test_login_to_signup_navigation(self, page):
        """Clicking 'Sign up' link on login page should navigate to signup."""
        login = LoginPage(page)
        login.navigate()

        login.signup_link.click()
        page.wait_for_load_state("networkidle")

        assert "signup" in page.url.lower()
        signup = SignupPage(page)
        assert signup.is_loaded()

    def test_root_redirects_to_login(self, page):
        """Hitting the root URL should redirect to login page."""
        page.goto("http://localhost:3001/")
        page.wait_for_load_state("networkidle")
        assert "login" in page.url.lower()


@pytest.mark.ui
class TestDashboardUI:
    """Additional UI tests for the dashboard."""

    def test_dashboard_greeting_visible(self, page):
        """After login, the greeting should display the user's name."""
        dashboard = _login_and_go_to_dashboard(page)

        greeting_text = dashboard.greeting.text_content()
        assert VERIFIED_USER["name"] in greeting_text or "Good" in greeting_text

    def test_dashboard_empty_state(self, page, mock_db):
        """Deleting all habits should show the empty state message."""
        dashboard = _login_and_go_to_dashboard(page)

        # Delete all seeded habits
        for habit_name in SEEDED_HABITS:
            dashboard.delete_habit(habit_name)

        # Empty state should be visible
        page.wait_for_timeout(500)
        assert dashboard.empty_state.is_visible()

    def test_dashboard_add_habit_via_enter_key(self, page):
        """Pressing Enter in the habit input should add the habit."""
        dashboard = _login_and_go_to_dashboard(page)

        initial_count = len(dashboard.get_habit_cards())
        dashboard.habit_input.fill("Yoga")
        dashboard.habit_input.press("Enter")
        page.wait_for_timeout(800)

        names = dashboard.get_habit_names()
        assert "Yoga" in names
        assert len(dashboard.get_habit_cards()) == initial_count + 1

    def test_dashboard_progress_bar_width_updates(self, page):
        """Completing a habit should update the progress bar width."""
        dashboard = _login_and_go_to_dashboard(page)

        # Initial progress bar should be 0%
        initial_width = dashboard.progress_bar.evaluate("el => el.style.width")
        assert initial_width == "0%"

        # Complete one habit
        dashboard.toggle_habit_complete(SEEDED_HABITS[0])

        new_width = dashboard.progress_bar.evaluate("el => el.style.width")
        assert new_width == "33%"

    def test_dashboard_logout_button_visible(self, page):
        """Dashboard should display a visible logout button."""
        dashboard = _login_and_go_to_dashboard(page)
        assert dashboard.logout_btn.is_visible()
