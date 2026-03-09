"""
Page Object Model – Login Page
"""

from tests.utils.test_data import LOGIN_URL


class LoginPage:
    """Encapsulates locators and actions for the login page."""

    def __init__(self, page):
        self.page = page

        # Locators
        self.email_input = page.locator("#email")
        self.password_input = page.locator("#password")
        self.submit_btn = page.locator("#loginBtn")
        self.alert = page.locator("#alert")
        self.signup_link = page.locator("a[href='signup.html']")

    def navigate(self):
        """Navigate to the login page."""
        self.page.goto(LOGIN_URL)
        self.page.wait_for_load_state("networkidle")

    def fill_form(self, email: str, password: str):
        """Fill in email and password fields."""
        self.email_input.fill(email)
        self.password_input.fill(password)

    def submit(self):
        """Click the login button."""
        self.submit_btn.click()

    def login(self, email: str, password: str):
        """Complete login flow: fill form and submit."""
        self.fill_form(email, password)
        self.submit()

    def get_alert_text(self) -> str:
        """Return the alert message text, waiting for it to appear."""
        self.alert.wait_for(state="visible", timeout=10000)
        return self.alert.text_content()

    def get_alert_type(self) -> str:
        """Return 'success' or 'error' based on the alert's CSS class."""
        self.alert.wait_for(state="visible", timeout=10000)
        classes = self.alert.get_attribute("class") or ""
        if "alert-success" in classes:
            return "success"
        return "error"

    def is_loaded(self) -> bool:
        """Check if the login page is fully loaded."""
        return self.email_input.is_visible() and self.submit_btn.is_visible()
