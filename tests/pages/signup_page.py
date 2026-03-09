"""
Page Object Model – Signup Page
"""

from tests.utils.test_data import SIGNUP_URL


class SignupPage:
    """Encapsulates locators and actions for the signup page."""

    def __init__(self, page):
        self.page = page

        # Locators
        self.name_input = page.locator("#name")
        self.email_input = page.locator("#email")
        self.password_input = page.locator("#password")
        self.submit_btn = page.locator("#signupBtn")
        self.alert = page.locator("#alert")
        self.login_link = page.locator("a[href='login.html']")

    def navigate(self):
        """Navigate to the signup page."""
        self.page.goto(SIGNUP_URL)
        self.page.wait_for_load_state("networkidle")

    def fill_form(self, name: str, email: str, password: str):
        """Fill in all signup form fields."""
        self.name_input.fill(name)
        self.email_input.fill(email)
        self.password_input.fill(password)

    def submit(self):
        """Click the signup button."""
        self.submit_btn.click()

    def signup(self, name: str, email: str, password: str):
        """Complete signup flow: fill form and submit."""
        self.fill_form(name, email, password)
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
        """Check if the signup page is fully loaded."""
        return self.name_input.is_visible() and self.submit_btn.is_visible()
