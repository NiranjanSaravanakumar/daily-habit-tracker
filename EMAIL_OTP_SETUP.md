# 📧 Email OTP Setup Guide

A complete step-by-step guide to configure the email OTP verification system in the Habit Tracker app.

---

## How It Works

When a user signs up, the server:

1. Generates a random **6-digit OTP** code
2. Stores the OTP + a 5-minute expiry in the `otps` database table
3. Sends the OTP to the user's email via **Nodemailer** (Gmail SMTP)
4. The user enters the OTP on the verification page
5. The server validates the OTP and activates the account

> [!NOTE]
> If email credentials are **not configured**, the OTP is printed to the server console instead — perfect for local development.

---

## Step 1 — Enable 2-Step Verification on Your Google Account

You need 2-Step Verification enabled before you can create an App Password.

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Under **"How you sign in to Google"**, click **2-Step Verification**
3. Follow the prompts to enable it (you'll need your phone)
4. Once enabled, you'll see a ✅ next to "2-Step Verification"

---

## Step 2 — Generate a Gmail App Password

Gmail doesn't allow direct password login from apps. You need an **App Password**.

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - If the link doesn't work, search **"App Passwords"** in your Google Account settings
2. You may need to re-enter your Google password
3. Under **"Select app"**, type a custom name: `Habit Tracker`
4. Click **Create**
5. Google will show a **16-character password** like: `abcd efgh ijkl mnop`
6. **Copy this password** — you will only see it once!

> [!CAUTION]
> Never share your App Password or commit it to Git. Treat it like a real password.

---

## Step 3 — Configure the `.env` File

Open the `.env` file in your project root (create it from `.env.example` if it doesn't exist):

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
# Server
PORT=3000

# JWT Secret – use any strong random string
JWT_SECRET=my_super_secret_key_change_me

# Email credentials
EMAIL_USER=your_real_email@gmail.com
EMAIL_PASS=abcd efgh ijkl mnop
```

| Variable     | What to put                                          |
| ------------ | ---------------------------------------------------- |
| `EMAIL_USER` | Your full Gmail address (e.g. `john@gmail.com`)      |
| `EMAIL_PASS` | The 16-character App Password from Step 2            |

> [!IMPORTANT]
> Use the **App Password**, NOT your regular Gmail password.

---

## Step 4 — Verify It Works

1. Start the server:
   ```bash
   npm start
   ```

2. Open `http://localhost:3000/signup.html` in your browser

3. Enter a name, your real email, and a password

4. Click **Create Account**

5. Check your email inbox — you should receive an email like:

   > **Subject:** Your Verification Code – Habit Tracker
   >
   > Your verification code is: **482917**

6. Enter the 6-digit code on the OTP verification page

7. If verified, you'll be redirected to the login page ✅

---

## Step 5 — Understand the Code

Here's how each piece fits together:

### `server/utils/sendOtp.js`

This file handles email sending. Key logic:

```javascript
// If credentials aren't set, fall back to console logging
if (!emailUser || !emailPass || emailUser === 'your_email@gmail.com') {
    console.log(`📧  OTP for ${email}: ${otpCode}`);
    return;
}

// Otherwise, send via Gmail SMTP
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: emailUser, pass: emailPass }
});
```

### `server/controllers/authController.js` — signup function

```javascript
// Generate 6-digit OTP
const otpCode = String(Math.floor(100000 + Math.random() * 900000));

// Expires in 5 minutes
const expiresAt = new Date(Date.now() + 5 * 60 * 1000).toISOString();

// Store in database
db.prepare('INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)')
  .run(email, otpCode, expiresAt);

// Send via email (or console)
await sendOtp(email, otpCode);
```

### `server/controllers/authController.js` — verifyOtp function

```javascript
// Find the latest OTP for this email
const record = db.prepare('SELECT * FROM otps WHERE email = ? ORDER BY id DESC LIMIT 1')
  .get(email);

// Check expiry
if (new Date(record.expires_at) < new Date()) {
    return res.status(400).json({ error: 'OTP has expired.' });
}

// Check code matches
if (record.otp_code !== otp) {
    return res.status(400).json({ error: 'Invalid OTP.' });
}

// Activate user
db.prepare('UPDATE users SET is_verified = 1 WHERE email = ?').run(email);
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| OTP prints to console instead of email | Set `EMAIL_USER` and `EMAIL_PASS` in `.env` to real values |
| "Invalid login" error from Gmail | Make sure you're using the **App Password**, not your regular password |
| "Less secure app" error | Enable 2-Step Verification first (Step 1), then use App Passwords |
| Email not arriving | Check your spam/junk folder. Also verify the email address is correct |
| "Missing credentials" error | Restart the server after editing `.env` — dotenv only reads on startup |
| App Password option not visible | 2-Step Verification must be enabled first |

---

## Development Mode (No Email)

During development, you can skip email setup entirely. Just leave `.env` with the defaults:

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password_here
```

The OTP will be printed to your terminal:

```
──────────────────────────────────────
📧  OTP for user@example.com: 482917
──────────────────────────────────────
```

Copy the code from the terminal and enter it on the OTP page.
