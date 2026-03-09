"""
test_authentication.py – Tests for authentication guards and session handling.
"""

import pytest
from tests.pages.login_page import LoginPage
from tests.pages.dashboard_page import DashboardPage
from tests.utils.test_data import VERIFIED_USER, DASHBOARD_URL, LOGIN_URL


@pytest.mark.auth
class TestAuthentication:
    """Authentication guard test suite."""

    def test_unauthenticated_dashboard_redirects_to_login(self, page):
        """
        Accessing the dashboard without a token should redirect to login.
        The JS auth guard in habits.js checks for a token in localStorage
        and redirects if missing.
        """
        page.goto(DASHBOARD_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # Should have been redirected to login
        assert "login" in page.url.lower(), \
            f"Expected redirect to login, but URL is {page.url}"

    def test_logout_clears_session(self, page):
        """
        Logging in and then clicking logout should redirect to login and
        clear the stored token.
        """
        # Login first
        login = LoginPage(page)
        login.navigate()
        login.login(VERIFIED_USER["email"], VERIFIED_USER["password"])
        page.wait_for_url("**/dashboard.html*", timeout=5000)

        # Now logout
        dashboard = DashboardPage(page)
        dashboard.logout()

        # Should be on login page
        page.wait_for_load_state("networkidle")
        assert "login" in page.url.lower()

        # Token should be cleared
        token = page.evaluate("() => localStorage.getItem('token')")
        assert token is None, "Token was not cleared after logout"

    def test_token_persists_across_navigation(self, page):
        """
        After login, navigating directly to the dashboard URL should still
        work — the token in localStorage should keep the user authenticated.
        """
        # Login
        login = LoginPage(page)
        login.navigate()
        login.login(VERIFIED_USER["email"], VERIFIED_USER["password"])
        page.wait_for_url("**/dashboard.html*", timeout=5000)

        # Navigate directly to dashboard again
        page.goto(DASHBOARD_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(500)

        # Should still be on dashboard (not redirected to login)
        assert "dashboard" in page.url.lower()

        dashboard = DashboardPage(page)
        assert dashboard.is_loaded()

    def test_invalid_token_redirects_to_login(self, page):
        """
        Setting a bogus token and accessing the dashboard should redirect
        to login when the API returns 401.
        """
        page.goto(LOGIN_URL)
        page.wait_for_load_state("networkidle")

        # Inject a fake token
        page.evaluate("() => localStorage.setItem('token', 'invalid.jwt.token')")
        page.evaluate("() => localStorage.setItem('user', JSON.stringify({name:'Fake'}))")

        page.goto(DASHBOARD_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # The habits.js fetch will get a 401 and redirect to login
        assert "login" in page.url.lower(), \
            f"Expected redirect to login with invalid token, but URL is {page.url}"
