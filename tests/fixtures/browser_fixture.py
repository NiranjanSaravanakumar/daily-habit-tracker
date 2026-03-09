"""
Playwright browser fixtures – headless Chromium browser and fresh page per test.
"""

import os
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser():
    """Launch a single headless Chromium instance for the entire test session."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture()
def page(browser, request):
    """
    Create a fresh browser context + page for each test.
    Captures a screenshot automatically on test failure.
    """
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
    )
    pg = context.new_page()

    yield pg

    # Screenshot on failure
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        screenshot_dir = os.path.join(
            os.path.dirname(__file__), "..", "screenshots"
        )
        os.makedirs(screenshot_dir, exist_ok=True)
        safe_name = request.node.name.replace("[", "_").replace("]", "_")
        pg.screenshot(path=os.path.join(screenshot_dir, f"FAIL_{safe_name}.png"))

    pg.close()
    context.close()
