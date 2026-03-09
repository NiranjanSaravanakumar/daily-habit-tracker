"""
Page Object Model – Dashboard Page
"""

from tests.utils.test_data import DASHBOARD_URL


class DashboardPage:
    """Encapsulates locators and actions for the dashboard page."""

    def __init__(self, page):
        self.page = page

        # Locators
        self.habit_input = page.locator("#habitInput")
        self.add_btn = page.locator("#addHabitBtn")
        self.habits_list = page.locator("#habitsList")
        self.empty_state = page.locator("#emptyState")
        self.progress_bar = page.locator("#progressBar")
        self.progress_text = page.locator("#progressText")
        self.progress_pct = page.locator("#progressPercentage")
        self.logout_btn = page.locator("#logoutBtn")
        self.greeting = page.locator("#greeting")
        self.alert = page.locator("#alert")

    def navigate(self):
        """Navigate to the dashboard page."""
        self.page.goto(DASHBOARD_URL)
        self.page.wait_for_load_state("networkidle")

    def is_loaded(self) -> bool:
        """Check if the dashboard rendered (habit input visible)."""
        return self.habit_input.is_visible()

    # ── Habit Actions ────────────────────────────────────────────────────

    def add_habit(self, name: str):
        """Type a habit name and click Add."""
        self.habit_input.fill(name)
        self.add_btn.click()
        # Wait for the list to update
        self.page.wait_for_timeout(800)

    def get_habit_cards(self):
        """Return all habit card elements."""
        return self.habits_list.locator(".habit-card").all()

    def get_habit_names(self) -> list[str]:
        """Return a list of habit name strings currently displayed."""
        cards = self.get_habit_cards()
        return [card.locator(".habit-name").text_content().strip() for card in cards]

    def get_habit_card_by_name(self, name: str):
        """Return the habit card element matching the given name."""
        cards = self.get_habit_cards()
        for card in cards:
            if card.locator(".habit-name").text_content().strip() == name:
                return card
        return None

    def toggle_habit_complete(self, name: str):
        """Click the checkbox on a habit card to toggle completion."""
        card = self.get_habit_card_by_name(name)
        if card:
            card.locator("input[type='checkbox']").click()
            self.page.wait_for_timeout(800)

    def is_habit_completed(self, name: str) -> bool:
        """Check if a habit card has the 'completed' class."""
        card = self.get_habit_card_by_name(name)
        if card:
            classes = card.get_attribute("class") or ""
            return "completed" in classes
        return False

    def delete_habit(self, name: str):
        """Click the delete button on a habit card."""
        card = self.get_habit_card_by_name(name)
        if card:
            # Hover to reveal delete button
            card.hover()
            card.locator(".btn-delete").click()
            self.page.wait_for_timeout(800)

    # ── Progress ─────────────────────────────────────────────────────────

    def get_progress_percentage_text(self) -> str:
        """Return the percentage text (e.g. '33%')."""
        return self.progress_pct.text_content().strip()

    def get_progress_text(self) -> str:
        """Return the progress description (e.g. '1 of 3 completed')."""
        return self.progress_text.text_content().strip()

    # ── Auth ─────────────────────────────────────────────────────────────

    def logout(self):
        """Click the logout button."""
        self.logout_btn.click()
        self.page.wait_for_load_state("networkidle")
