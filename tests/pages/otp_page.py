"""
Page Object Model – OTP Verification Page
"""

from tests.utils.test_data import OTP_URL


class OtpPage:
    """Encapsulates locators and actions for the OTP verification page."""

    def __init__(self, page):
        self.page = page

        # Locators
        self.otp_input = page.locator("#otp")
        self.submit_btn = page.locator("#otpBtn")
        self.alert = page.locator("#alert")
        self.signup_link = page.locator("a[href='signup.html']")

    def navigate(self):
        """Navigate to the OTP page."""
        self.page.goto(OTP_URL)
        self.page.wait_for_load_state("networkidle")

    def fill_otp(self, otp: str):
        """Fill in the OTP field."""
        self.otp_input.fill(otp)

    def submit(self):
        """Click the verify button."""
        self.submit_btn.click()

    def verify(self, otp: str):
        """Complete OTP flow: fill and submit."""
        self.fill_otp(otp)
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
        """Check if the OTP page is fully loaded."""
        return self.otp_input.is_visible() and self.submit_btn.is_visible()
