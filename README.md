# Daily Habit Tracker

A modern full-stack habit tracking application that helps users build and maintain daily habits. Features secure authentication with email OTP verification, intuitive habit management, and visual daily progress tracking.

---

## Features

- **Secure Authentication** – Signup with email OTP verification, bcrypt password hashing, JWT sessions
- **Habit Management** – Create, view, and delete personal habits
- **Daily Tracking** – Mark habits as completed each day with a single click
- **Progress Dashboard** – Visual progress bar showing daily completion rate
- **Dark Theme UI** – Modern, responsive design with glassmorphism aesthetics
- **Automated Tests** – Playwright + Pytest test suite with mock database

---

## Tech Stack

| Layer    | Technology              |
| -------- | ----------------------- |
| Frontend | HTML, CSS, JavaScript   |
| Backend  | Node.js, Express.js     |
| Database | SQLite (better-sqlite3) |
| Auth     | JWT, bcryptjs           |
| Email    | Nodemailer              |
| Testing  | Playwright, Pytest      |

---

## Project Structure

```
daily-habit-tracker/
│
├─ server/                        # ── Backend ──────────────────────
│  ├─ server.js                   #    Express app entry point
│  ├─ controllers/
│  │  ├─ authController.js        #    Signup, OTP verify, login logic
│  │  └─ habitController.js       #    CRUD + completion logic
│  ├─ routes/
│  │  ├─ authRoutes.js            #    /api/auth/* endpoints
│  │  └─ habitRoutes.js           #    /api/habits/* endpoints
│  ├─ middleware/
│  │  └─ authMiddleware.js        #    JWT verification guard
│  ├─ database/
│  │  └─ db.js                    #    SQLite setup & table creation
│  └─ utils/
│     └─ sendOtp.js               #    Email OTP sender (Nodemailer)
│
├─ public/                        # ── Frontend ─────────────────────
│  ├─ signup.html                 #    Registration page
│  ├─ login.html                  #    Login page
│  ├─ otp.html                    #    OTP verification page
│  ├─ dashboard.html              #    Main habit tracker dashboard
│  ├─ css/
│  │  └─ style.css                #    Global styles (dark theme)
│  └─ js/
│     ├─ auth.js                  #    Auth form handlers
│     └─ habits.js                #    Dashboard & habit UI logic
│
├─ tests/                         # ── Test Suite (Python) ──────────
│  ├─ conftest.py                 #    Pytest fixtures & config
│  ├─ test_signup.py              #    Signup flow tests
│  ├─ test_login.py               #    Login flow tests
│  ├─ test_otp.py                 #    OTP verification tests
│  ├─ test_habits.py              #    Habit management tests
│  ├─ test_authentication.py      #    Auth guard tests
│  ├─ test_api_auth.py            #    Auth API endpoint tests
│  ├─ test_api_habits.py          #    Habits API endpoint tests
│  ├─ test_ui_validation.py       #    UI validation tests
│  ├─ pages/                      #    Page Object Model
│  │  ├─ signup_page.py
│  │  ├─ login_page.py
│  │  ├─ otp_page.py
│  │  └─ dashboard_page.py
│  ├─ fixtures/
│  │  ├─ browser_fixture.py       #    Playwright browser setup
│  │  └─ mock_db_fixture.py       #    Mock DB & test server
│  └─ utils/
│     └─ test_data.py             #    Test constants & helpers
│
├─ seedTestUsers.js               # Seed script – creates all test accounts
├─ .env.example                   # Environment variable template
├─ package.json                   # Node.js dependencies & scripts
├─ requirements.txt               # Python test dependencies
├─ pytest.ini                     # Pytest configuration
├─ EMAIL_OTP_SETUP.md             # OTP setup guide
└─ README.md
```

---

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) v16 or higher
- [Python](https://www.python.org/) 3.10+ (for running tests)

### Step 1 — Clone & Install

```bash
# Clone the repository
git clone https://github.com/your-username/daily-habit-tracker.git
cd daily-habit-tracker

# Install Node.js dependencies
npm install
```

### Step 2 — Create the `.env` File

Copy the example environment file and edit it with your values:

```bash
# Linux / macOS
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Open `.env` and fill in the required values:

| Variable     | Required | Description                             | Example                |
| ------------ | -------- | --------------------------------------- | ---------------------- |
| `PORT`       | Yes      | Server port                             | `3000`                 |
| `JWT_SECRET` | Yes      | Secret key for JWT token signing        | `my_super_secret_key`  |
| `EMAIL_USER` | No       | Email address for sending OTPs          | `your_email@gmail.com` |
| `EMAIL_PASS` | No       | Email app password                      | `abcd efgh ijkl mnop`  |
| `TEST_MODE`  | No       | Skip OTP on signup (`true` / `false`)   | `false`                |
| `NODE_ENV`   | No       | Environment mode                        | `development`          |

> **Note:** `EMAIL_USER` and `EMAIL_PASS` are only needed if you want OTPs sent via email. Without them, OTPs are printed to the server console — good enough for local development. For Gmail, enable [App Passwords](https://support.google.com/accounts/answer/185833) and use the generated password. See [EMAIL_OTP_SETUP.md](EMAIL_OTP_SETUP.md) for a detailed walkthrough.

### Step 3 — Seed Test Users (Optional)

Create pre-verified test accounts so you can log in without signing up:

```bash
node seedTestUsers.js
# or
npm run seed
```

This creates 4 test accounts with sample habits (see [Test Accounts](#test-accounts) below).

### Step 4 — Start the Server

```bash
npm start
```

Open **http://localhost:3000** in your browser.

### Step 5 — Install Python Test Dependencies (Optional)

Only needed if you want to run the automated test suite:

```bash
pip install -r requirements.txt
playwright install chromium
```

### Quick Start Summary

| Step | Command                     | File Used           | Purpose                        |
| ---- | --------------------------- | ------------------- | ------------------------------ |
| 1    | `npm install`               | `package.json`      | Install Node.js dependencies   |
| 2    | `cp .env.example .env`      | `.env.example`      | Create environment config      |
| 3    | `node seedTestUsers.js`     | `seedTestUsers.js`  | Seed test accounts (optional)  |
| 4    | `npm start`                 | `server/server.js`  | Start the application          |
| 5    | `pip install -r requirements.txt` | `requirements.txt` | Install Python test deps (optional) |
| 5    | `playwright install chromium` | —                 | Install test browser (optional)|

---

## Email OTP Setup

For a complete step-by-step guide on setting up email OTP, including Gmail App Passwords, code walkthrough, and troubleshooting, see:

**[EMAIL_OTP_SETUP.md](EMAIL_OTP_SETUP.md)**

> **Dev mode:** If email credentials are not configured, OTPs are printed to the server console — no email setup needed for local development.

---

## API Endpoints

### Authentication

| Method | Endpoint               | Description         | Auth |
| ------ | ---------------------- | ------------------- | ---- |
| POST   | `/api/auth/signup`     | Register a new user | No   |
| POST   | `/api/auth/verify-otp` | Verify email OTP    | No   |
| POST   | `/api/auth/login`      | Login & receive JWT | No   |

### Habits

| Method | Endpoint                   | Description             | Auth |
| ------ | -------------------------- | ----------------------- | ---- |
| GET    | `/api/habits`              | Get all user habits     | Yes  |
| POST   | `/api/habits`              | Create a new habit      | Yes  |
| DELETE | `/api/habits/:id`          | Delete a habit          | Yes  |
| POST   | `/api/habits/:id/complete` | Toggle habit completion | Yes  |
| GET    | `/api/habits/progress`     | Get daily progress      | Yes  |

> **Auth Yes** = Requires `Authorization: Bearer <token>` header.

---

## Test Accounts

Predefined test accounts are available for development and automated testing. All accounts are **pre-verified** (OTP is skipped) and ready to log in immediately.

### Seed Test Users

A single seed script creates all test accounts with sample habits:

```bash
npm run seed
# or
node seedTestUsers.js
```

The script is **idempotent** — it skips any user that already exists. It **will not run** if `NODE_ENV=production`.

### Credentials

| Name              | Email                    | Password      |
| ----------------- | ------------------------ | ------------- |
| Test User         | `test@example.com`       | `password123` |
| Test User         | `testuser1@example.com`  | `Test@123`    |
| Demo User         | `demo@example.com`       | `Demo@123`    |
| Automation Tester | `automation@example.com` | `Auto@123`    |

### TEST_MODE

Set `TEST_MODE=true` in `.env` to enable test mode. In test mode:

- Signup **auto-verifies** the user (no OTP generation or email)
- Test accounts can log in directly without email verification

> **Safety:** Test accounts are only created in development/test environments. The seed script refuses to run when `NODE_ENV=production`, and `TEST_MODE` should be set to `false` in production.

---

## Running Tests

The project includes an automated test suite using **Playwright** (browser automation) and **Pytest**. Tests use a **mock SQLite database** so the real database is never touched.

> Make sure you have installed the test dependencies first (see [Step 5](#step-5--install-python-test-dependencies-optional) above).

### Run All Tests

```bash
pytest tests -v
```

### Run Specific Test Categories

```bash
pytest tests -v -m signup          # Signup tests
pytest tests -v -m login           # Login tests
pytest tests -v -m habits          # Habit management tests
pytest tests -v -m auth            # Authentication guard tests
```

### Test Features

- Headless Chromium browser automation
- Mock database (tests never touch production data)
- Auto-screenshot on test failure (saved to `tests/screenshots/`)
- Per-test database reset for isolation
- Page Object Model for maintainability

---

## Screenshots

<!-- Add your screenshots here -->
| Signup | Dashboard |
|--------|-----------|
| *Coming soon* | *Coming soon* |

---

Step 1 — Clone & npm install (uses package.json)
Step 2 — Create .env from .env.example (includes Windows PowerShell command, marks which vars are required vs optional, explains that email config is only needed for real OTP sending)
Step 3 — node seedTestUsers.js to seed test accounts (optional)
Step 4 — npm start to run the server (uses server.js)
Step 5 — pip install -r requirements.txt + playwright install chromium for tests (optional)