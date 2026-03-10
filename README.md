# 🎯 Daily Habit Tracker

A modern full-stack habit tracking application that helps users build and maintain daily habits. Features secure authentication with email OTP verification, intuitive habit management, and visual daily progress tracking.

---

## ✨ Features

- **Secure Authentication** – Signup with email OTP verification, bcrypt password hashing, JWT sessions
- **Habit Management** – Create, view, and delete personal habits
- **Daily Tracking** – Mark habits as completed each day with a single click
- **Progress Dashboard** – Visual progress bar showing daily completion rate
- **Dark Theme UI** – Modern, responsive design with glassmorphism aesthetics
- **Automated Tests** – Playwright + Pytest test suite with mock database

---

## 🛠️ Tech Stack

| Layer      | Technology              |
| ---------- | ----------------------- |
| Frontend   | HTML, CSS, JavaScript   |
| Backend    | Node.js, Express.js     |
| Database   | SQLite (better-sqlite3) |
| Auth       | JWT, bcryptjs           |
| Email      | Nodemailer              |
| Testing    | Playwright, Pytest      |

---

## 📁 Project Structure

```
daily-habit-tracker/
├── server/
│   ├── server.js              # Express app entry point
│   ├── routes/
│   │   ├── authRoutes.js      # Auth endpoints
│   │   └── habitRoutes.js     # Habit endpoints
│   ├── controllers/
│   │   ├── authController.js  # Auth logic
│   │   └── habitController.js # Habit logic
│   ├── middleware/
│   │   └── authMiddleware.js  # JWT verification
│   ├── database/
│   │   └── db.js              # SQLite setup & queries
│   └── utils/
│       └── sendOtp.js         # Email OTP sender
├── public/
│   ├── signup.html
│   ├── login.html
│   ├── otp.html
│   ├── dashboard.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── auth.js
│       └── habits.js
├── tests/
│   ├── conftest.py            # Pytest fixtures & config
│   ├── test_signup.py         # Signup flow tests
│   ├── test_login.py          # Login flow tests
│   ├── test_habits.py         # Habit management tests
│   ├── test_authentication.py # Auth guard tests
│   ├── pages/                 # Page Object Model
│   │   ├── signup_page.py
│   │   ├── login_page.py
│   │   └── dashboard_page.py
│   ├── fixtures/
│   │   ├── browser_fixture.py # Playwright browser setup
│   │   └── mock_db_fixture.py # Mock DB & test server
│   └── utils/
│       └── test_data.py       # Test constants
├── .env.example
├── .gitignore
├── package.json
├── requirements.txt           # Python test dependencies
├── pytest.ini
├── EMAIL_OTP_SETUP.md         # OTP setup guide
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) v16 or higher
- [Python](https://www.python.org/) 3.10+ (for running tests)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/daily-habit-tracker.git
cd daily-habit-tracker

# Install Node.js dependencies
npm install

# Create environment file
cp .env.example .env
```

### Environment Variables

Edit `.env` with your values:

| Variable     | Description                          | Example                     |
| ------------ | ------------------------------------ | --------------------------- |
| `PORT`       | Server port                          | `3000`                      |
| `JWT_SECRET` | Secret key for JWT token signing     | `my_super_secret_key`       |
| `EMAIL_USER` | Email address for sending OTPs       | `your_email@gmail.com`      |
| `EMAIL_PASS` | Email app password                   | `abcd efgh ijkl mnop`       |

> **Note:** For Gmail, enable [App Passwords](https://support.google.com/accounts/answer/185833) and use the generated password. See [EMAIL_OTP_SETUP.md](EMAIL_OTP_SETUP.md) for a detailed walkthrough.

### Run the Application

```bash
npm start
```

Open **http://localhost:3000** in your browser.

---

## 📧 Email OTP Setup

For a complete step-by-step guide on setting up email OTP, including Gmail App Passwords, code walkthrough, and troubleshooting, see:

👉 **[EMAIL_OTP_SETUP.md](EMAIL_OTP_SETUP.md)**

> **Dev mode:** If email credentials are not configured, OTPs are printed to the server console — no email setup needed for local development.

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint              | Description              | Auth |
| ------ | --------------------- | ------------------------ | ---- |
| POST   | `/api/auth/signup`    | Register a new user      | ❌   |
| POST   | `/api/auth/verify-otp`| Verify email OTP         | ❌   |
| POST   | `/api/auth/login`     | Login & receive JWT      | ❌   |

### Habits

| Method | Endpoint                    | Description                  | Auth |
| ------ | --------------------------- | ---------------------------- | ---- |
| GET    | `/api/habits`               | Get all user habits          | ✅   |
| POST   | `/api/habits`               | Create a new habit           | ✅   |
| DELETE | `/api/habits/:id`           | Delete a habit               | ✅   |
| POST   | `/api/habits/:id/complete`  | Toggle habit completion      | ✅   |
| GET    | `/api/habits/progress`      | Get daily progress           | ✅   |

> **Auth ✅** = Requires `Authorization: Bearer <token>` header.

---

## 🧪 Running Tests

The project includes an automated test suite using **Playwright** (browser automation) and **Pytest**. Tests use a **mock SQLite database** so the real database is never touched.

### Install Test Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Run All Tests

```bash
pytest tests -v
```

### Run Specific Test Categories

```bash
# Signup tests only
pytest tests -v -m signup

# Login tests only
pytest tests -v -m login

# Habit management tests only
pytest tests -v -m habits

# Authentication guard tests only
pytest tests -v -m auth
```

### Test Features

- ✅ Headless Chromium browser automation
- ✅ Mock database (tests never touch production data)
- ✅ Auto-screenshot on test failure (saved to `tests/screenshots/`)
- ✅ Per-test database reset for isolation
- ✅ Page Object Model for maintainability

---

## 🧑‍💻 Test Accounts

Predefined test accounts are available for development and automated testing. These accounts are **pre-verified** (OTP is skipped) and ready to log in immediately.

### Credentials

| Name               | Email                     | Password   |
| ------------------ | ------------------------- | ---------- |
| Test User          | `testuser1@example.com`   | `Test@123` |
| Demo User          | `demo@example.com`        | `Demo@123` |
| Automation Tester  | `automation@example.com`  | `Auto@123` |

### Seed Test Users

Run the seeder script to create all test accounts with sample habits:

```bash
npm run seed
# or
node seedTestUsers.js
```

The script is **idempotent** — it skips any user that already exists. It **will not run** if `NODE_ENV=production`.

### TEST_MODE

Set `TEST_MODE=true` in `.env` to enable test mode. In test mode:

- Signup **auto-verifies** the user (no OTP generation or email)
- Test accounts can log in directly without email verification

> ⚠️ **Safety:** Test accounts are only created in development/test environments. The seed script refuses to run when `NODE_ENV=production`, and `TEST_MODE` should be set to `false` in production.

---

## 📸 Screenshots

<!-- Add your screenshots here -->
| Signup | Dashboard |
|--------|-----------|
| *Coming soon* | *Coming soon* |

---

## 📄 License

This project is licensed under the MIT License.
