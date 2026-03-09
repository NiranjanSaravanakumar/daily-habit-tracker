"""
Test data constants used across all test modules.
"""

# ── Base URL ─────────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:3001"

# ── Test User (pre-seeded and verified in mock DB) ───────────────────────────
VERIFIED_USER = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "password123",
}

# ── New User (for signup tests — NOT pre-seeded) ────────────────────────────
NEW_USER = {
    "name": "New Signup User",
    "email": "newuser@example.com",
    "password": "newpass456",
}

# ── Invalid Credentials ─────────────────────────────────────────────────────
INVALID_USER = {
    "email": "nobody@example.com",
    "password": "wrongpassword",
}

# ── Sample Habits (pre-seeded in mock DB) ────────────────────────────────────
SEEDED_HABITS = ["Exercise", "Reading", "Drink Water"]

# ── New Habit (for add-habit tests) ──────────────────────────────────────────
NEW_HABIT = "Meditate"

# ── Pages ────────────────────────────────────────────────────────────────────
SIGNUP_URL = f"{BASE_URL}/signup.html"
LOGIN_URL = f"{BASE_URL}/login.html"
OTP_URL = f"{BASE_URL}/otp.html"
DASHBOARD_URL = f"{BASE_URL}/dashboard.html"
