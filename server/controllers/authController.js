const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const db = require('../database/db');
const sendOtp = require('../utils/sendOtp');

// ── Signup ──────────────────────────────────────────────────────────────────

async function signup(req, res) {
  try {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ error: 'Name, email, and password are required.' });
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({ error: 'Invalid email format.' });
    }

    // Validate password length
    if (password.length < 6) {
      return res.status(400).json({ error: 'Password must be at least 6 characters.' });
    }

    // Check if user already exists
    const existing = db.prepare('SELECT id, is_verified FROM users WHERE email = ?').get(email);

    if (existing && existing.is_verified) {
      return res.status(409).json({ error: 'Email already registered.' });
    }

    const passwordHash = await bcrypt.hash(password, 12);

    if (existing && !existing.is_verified) {
      // Update the unverified user's details
      db.prepare('UPDATE users SET name = ?, password_hash = ? WHERE email = ?').run(name, passwordHash, email);
    } else {
      db.prepare('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)').run(name, email, passwordHash);
    }

    // ── TEST_MODE: skip OTP, auto-verify ──────────────────────────────────
    if (process.env.TEST_MODE === 'true') {
      db.prepare('UPDATE users SET is_verified = 1 WHERE email = ?').run(email);
      return res.status(200).json({ message: 'Account created and auto-verified (TEST_MODE).' });
    }

    // Generate 6-digit OTP
    const otpCode = String(Math.floor(100000 + Math.random() * 900000));
    const expiresAt = new Date(Date.now() + 5 * 60 * 1000).toISOString();

    // Remove old OTPs for this email
    db.prepare('DELETE FROM otps WHERE email = ?').run(email);
    db.prepare('INSERT INTO otps (email, otp_code, expires_at) VALUES (?, ?, ?)').run(email, otpCode, expiresAt);

    // Send OTP via email (or console in dev mode)
    await sendOtp(email, otpCode);

    res.status(200).json({ message: 'OTP sent to your email. Please verify to activate your account.' });
  } catch (err) {
    console.error('Signup error:', err);
    res.status(500).json({ error: 'Internal server error.' });
  }
}

// ── Verify OTP ──────────────────────────────────────────────────────────────

function verifyOtp(req, res) {
  try {
    const { email, otp } = req.body;

    if (!email || !otp) {
      return res.status(400).json({ error: 'Email and OTP are required.' });
    }

    const record = db.prepare('SELECT * FROM otps WHERE email = ? ORDER BY id DESC LIMIT 1').get(email);

    if (!record) {
      return res.status(400).json({ error: 'No OTP found for this email. Please sign up again.' });
    }

    if (new Date(record.expires_at) < new Date()) {
      db.prepare('DELETE FROM otps WHERE email = ?').run(email);
      return res.status(400).json({ error: 'OTP has expired. Please sign up again.' });
    }

    if (record.otp_code !== otp) {
      return res.status(400).json({ error: 'Invalid OTP.' });
    }

    // Activate user
    db.prepare('UPDATE users SET is_verified = 1 WHERE email = ?').run(email);
    db.prepare('DELETE FROM otps WHERE email = ?').run(email);

    res.status(200).json({ message: 'Email verified successfully. You can now log in.' });
  } catch (err) {
    console.error('Verify OTP error:', err);
    res.status(500).json({ error: 'Internal server error.' });
  }
}

// ── Login ───────────────────────────────────────────────────────────────────

async function login(req, res) {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required.' });
    }

    const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);

    if (!user) {
      return res.status(401).json({ error: 'Invalid email or password.' });
    }

    if (!user.is_verified) {
      return res.status(403).json({ error: 'Account not verified. Please verify your email first.' });
    }

    const isMatch = await bcrypt.compare(password, user.password_hash);

    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid email or password.' });
    }

    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    res.status(200).json({
      message: 'Login successful.',
      token,
      user: { id: user.id, name: user.name, email: user.email },
    });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ error: 'Internal server error.' });
  }
}

module.exports = { signup, verifyOtp, login };
