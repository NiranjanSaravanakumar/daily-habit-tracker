"""
Mock database fixture – creates a temporary SQLite database, seeds it with
test data, starts a test server on port 3001, and tears everything down after
the test session.
"""

import os
import sys
import time
import sqlite3
import tempfile
import subprocess
import signal
import requests

import pytest
import bcrypt

# ── Constants ────────────────────────────────────────────────────────────────

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEST_PORT = 3001
SERVER_ENTRY = os.path.join(PROJECT_ROOT, "server", "server.js")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_verified INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS otps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    expires_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    habit_name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    completed INTEGER DEFAULT 1,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(habit_id, date)
);
"""


def _hash_password(plain: str) -> str:
    """Hash a password with bcrypt (compatible with bcryptjs on the Node side)."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def _seed_database(db_path: str):
    """Insert the pre-verified test user and sample habits."""
    from tests.utils.test_data import VERIFIED_USER, SEEDED_HABITS

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Seed verified user
    pw_hash = _hash_password(VERIFIED_USER["password"])
    cur.execute(
        "INSERT INTO users (name, email, password_hash, is_verified) VALUES (?, ?, ?, 1)",
        (VERIFIED_USER["name"], VERIFIED_USER["email"], pw_hash),
    )
    user_id = cur.lastrowid

    # Seed habits
    for habit_name in SEEDED_HABITS:
        cur.execute(
            "INSERT INTO habits (user_id, habit_name) VALUES (?, ?)",
            (user_id, habit_name),
        )

    conn.commit()
    conn.close()


def _wait_for_server(url: str, timeout: int = 15):
    """Poll the server until it responds or timeout is reached."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code < 500:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Test server did not start within {timeout}s")


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def mock_db():
    """
    Session-scoped fixture that:
    1. Creates a temp SQLite database file with schema + test data
    2. Starts the Node.js server on port 3001 using the temp DB
    3. Yields the db path for any test that needs direct DB access
    4. Tears down server + deletes temp DB
    """
    # 1. Create temp database
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False, prefix="habit_test_")
    db_path = tmp.name
    tmp.close()

    # 2. Initialise schema
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

    # 3. Seed test data
    _seed_database(db_path)

    # 4. Start test server
    env = {
        **os.environ,
        "PORT": str(TEST_PORT),
        "DB_PATH": db_path,
        "JWT_SECRET": "test_jwt_secret_key_for_testing",
        "EMAIL_USER": "test@test.com",
        "EMAIL_PASS": "",
    }

    server_proc = subprocess.Popen(
        ["node", SERVER_ENTRY],
        env=env,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )

    try:
        _wait_for_server(f"http://localhost:{TEST_PORT}/login.html")
    except RuntimeError:
        server_proc.kill()
        os.unlink(db_path)
        raise

    yield db_path

    # 5. Tear down
    if sys.platform == "win32":
        server_proc.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        server_proc.terminate()

    try:
        server_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_proc.kill()

    # Delete temp database
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def reset_db(mock_db):
    """
    Per-test fixture that resets the mock database to its seeded state before
    each test, keeping tests isolated.
    """
    conn = sqlite3.connect(mock_db)
    cur = conn.cursor()

    # Clear all data
    cur.execute("DELETE FROM habit_logs")
    cur.execute("DELETE FROM habits")
    cur.execute("DELETE FROM otps")
    cur.execute("DELETE FROM users")

    conn.commit()
    conn.close()

    # Re-seed
    _seed_database(mock_db)

    # Force WAL checkpoint so the Node server (better-sqlite3) sees fresh data
    conn = sqlite3.connect(mock_db)
    conn.execute("PRAGMA wal_checkpoint(FULL)")
    conn.close()

    # Small delay to ensure the Node server picks up the changes
    time.sleep(0.1)

    yield

