#!/usr/bin/env node

/**
 * seedTestUsers.js – Inserts predefined test accounts into the database.
 *
 * Usage:   node seedTestUsers.js
 *            npm run seed
 *
 * Safety:  Only runs when NODE_ENV is NOT "production".
 *          Skips any user whose email already exists (idempotent).
 */

require('dotenv').config();

// ── Safety Guard ────────────────────────────────────────────────────────────

if (process.env.NODE_ENV === 'production') {
  console.error('❌  ERROR: seedTestUsers.js must NOT run in production.');
  process.exit(1);
}

const bcrypt = require('bcryptjs');
const db = require('./server/database/db');

// ── Test Accounts ───────────────────────────────────────────────────────────

const TEST_USERS = [
  {
    name: 'Test User',
    email: 'test@example.com',
    password: 'password123',
    habits: ['Morning Run', 'Read 10 Pages', 'Drink Water'],
  },
  {
    name: 'Test User',
    email: 'testuser1@example.com',
    password: 'Test@123',
    habits: ['Morning Run', 'Read 10 Pages', 'Drink Water'],
  },
  {
    name: 'Demo User',
    email: 'demo@example.com',
    password: 'Demo@123',
    habits: ['Exercise', 'Meditate'],
  },
  {
    name: 'Automation Tester',
    email: 'automation@example.com',
    password: 'Auto@123',
    habits: ['Write Tests', 'Code Review', 'Stand-up Meeting'],
  },
];

// ── Seed Logic ──────────────────────────────────────────────────────────────

function seedTestUsers() {
  console.log('\n🌱  Seeding test users …\n');

  const insertUser = db.prepare(
    'INSERT INTO users (name, email, password_hash, is_verified) VALUES (?, ?, ?, 1)'
  );
  const insertHabit = db.prepare(
    'INSERT INTO habits (user_id, habit_name) VALUES (?, ?)'
  );
  const findUser = db.prepare('SELECT id FROM users WHERE email = ?');

  let created = 0;
  let skipped = 0;

  for (const user of TEST_USERS) {
    const existing = findUser.get(user.email);

    if (existing) {
      console.log(`⏭️  Skipped (already exists): ${user.email}`);
      skipped++;
      continue;
    }

    const passwordHash = bcrypt.hashSync(user.password, 12);
    const info = insertUser.run(user.name, user.email, passwordHash);

    // Seed sample habits for each test user
    for (const habit of user.habits) {
      insertHabit.run(info.lastInsertRowid, habit);
    }

    console.log(`✅  Created: ${user.name} <${user.email}>`);
    created++;
  }

  // ── Summary ───────────────────────────────────────────────────────────────

  console.log('\n────────────────────────────────────────');
  console.log(`  Created: ${created}   Skipped: ${skipped}`);
  console.log('────────────────────────────────────────');
  console.log('\n📋  Test Credentials:\n');

  for (const user of TEST_USERS) {
    console.log(`  ${user.name}`);
    console.log(`    Email:    ${user.email}`);
    console.log(`    Password: ${user.password}\n`);
  }
}

try {
  seedTestUsers();
} catch (err) {
  console.error('❌  Seeding failed:', err.message);
  process.exit(1);
}
