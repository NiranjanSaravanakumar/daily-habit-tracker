require('dotenv').config();

const express = require('express');
const cors = require('cors');
const path = require('path');

// ── Guard: JWT_SECRET must be set ───────────────────────────────────────────
if (!process.env.JWT_SECRET) {
  console.error('❌  ERROR: JWT_SECRET is not set in .env. Server cannot start without it.');
  process.exit(1);
}

const authRoutes = require('./routes/authRoutes');
const habitRoutes = require('./routes/habitRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// ── Middleware ───────────────────────────────────────────────────────────────
app.use(cors());
app.use(express.json({ limit: '1mb' }));

// ── Serve static frontend files ─────────────────────────────────────────────
app.use(express.static(path.join(__dirname, '..', 'public')));

// ── API Routes ──────────────────────────────────────────────────────────────
app.use('/api/auth', authRoutes);
app.use('/api/habits', habitRoutes);

// ── Root redirect ───────────────────────────────────────────────────────────
app.get('/', (_req, res) => {
  res.redirect('/login.html');
});

// ── Start ───────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`\n🚀  Habit Tracker server running at http://localhost:${PORT}\n`);
});
