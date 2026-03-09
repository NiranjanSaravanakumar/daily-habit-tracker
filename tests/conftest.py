"""
Root conftest.py – imports all fixtures and adds the pytest hook for
tracking test pass/fail status (used by screenshot-on-failure logic).
"""

import pytest

# Import fixtures so pytest discovers them
from tests.fixtures.mock_db_fixture import mock_db, reset_db  # noqa: F401
from tests.fixtures.browser_fixture import browser, page     # noqa: F401


# ── Hook: store test result on the node for screenshot-on-failure ────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach test outcome to the request node so fixtures can inspect it."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
