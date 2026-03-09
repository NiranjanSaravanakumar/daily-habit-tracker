"""
test_habits.py – Tests for habit management on the dashboard.
"""

import pytest
from tests.pages.login_page import LoginPage
from tests.pages.dashboard_page import DashboardPage
from tests.utils.test_data import VERIFIED_USER, SEEDED_HABITS, NEW_HABIT


def _login_and_go_to_dashboard(page) -> DashboardPage:
    """Helper: log in with the seeded user and navigate to the dashboard."""
    login = LoginPage(page)
    login.navigate()
    login.login(VERIFIED_USER["email"], VERIFIED_USER["password"])
    page.wait_for_url("**/dashboard.html*", timeout=5000)
    page.wait_for_load_state("networkidle")
    dashboard = DashboardPage(page)
    return dashboard


@pytest.mark.habits
class TestHabits:
    """Habit management test suite."""

    def test_dashboard_shows_seeded_habits(self, page):
        """Dashboard should display the three pre-seeded habits."""
        dashboard = _login_and_go_to_dashboard(page)

        names = dashboard.get_habit_names()
        for habit in SEEDED_HABITS:
            assert habit in names, f"Seeded habit '{habit}' not found on dashboard"

    def test_add_new_habit(self, page):
        """Adding a new habit should make it appear in the list."""
        dashboard = _login_and_go_to_dashboard(page)

        initial_count = len(dashboard.get_habit_cards())
        dashboard.add_habit(NEW_HABIT)

        names = dashboard.get_habit_names()
        assert NEW_HABIT in names, f"New habit '{NEW_HABIT}' not found after adding"
        assert len(dashboard.get_habit_cards()) == initial_count + 1

    def test_mark_habit_completed(self, page):
        """Clicking the checkbox should mark a habit as completed."""
        dashboard = _login_and_go_to_dashboard(page)

        habit_name = SEEDED_HABITS[0]  # "Exercise"
        assert not dashboard.is_habit_completed(habit_name)

        dashboard.toggle_habit_complete(habit_name)
        assert dashboard.is_habit_completed(habit_name), \
            f"Habit '{habit_name}' was not marked as completed"

    def test_unmark_habit_completed(self, page):
        """Clicking the checkbox again should unmark a completed habit."""
        dashboard = _login_and_go_to_dashboard(page)

        habit_name = SEEDED_HABITS[0]

        # Mark then unmark
        dashboard.toggle_habit_complete(habit_name)
        assert dashboard.is_habit_completed(habit_name)

        dashboard.toggle_habit_complete(habit_name)
        assert not dashboard.is_habit_completed(habit_name), \
            f"Habit '{habit_name}' was not unmarked"

    def test_delete_habit(self, page):
        """Deleting a habit should remove it from the dashboard."""
        dashboard = _login_and_go_to_dashboard(page)

        habit_to_delete = SEEDED_HABITS[1]  # "Reading"
        initial_count = len(dashboard.get_habit_cards())

        dashboard.delete_habit(habit_to_delete)

        names = dashboard.get_habit_names()
        assert habit_to_delete not in names, \
            f"Deleted habit '{habit_to_delete}' still present on dashboard"
        assert len(dashboard.get_habit_cards()) == initial_count - 1

    def test_progress_updates_on_completion(self, page):
        """Progress percentage should update when a habit is marked complete."""
        dashboard = _login_and_go_to_dashboard(page)

        # Initially 0%
        assert dashboard.get_progress_percentage_text() == "0%"

        # Complete one out of three
        dashboard.toggle_habit_complete(SEEDED_HABITS[0])
        pct_text = dashboard.get_progress_percentage_text()
        assert pct_text == "33%", f"Expected 33%, got '{pct_text}'"

        progress_text = dashboard.get_progress_text()
        assert "1 of 3" in progress_text

    def test_add_habit_empty_name_ignored(self, page):
        """Submitting an empty habit name should not add a card."""
        dashboard = _login_and_go_to_dashboard(page)

        initial_count = len(dashboard.get_habit_cards())
        dashboard.add_habit("")

        assert len(dashboard.get_habit_cards()) == initial_count
