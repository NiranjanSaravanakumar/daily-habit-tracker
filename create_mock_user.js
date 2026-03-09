const db = require('./server/database/db');
const bcrypt = require('bcryptjs');

function createMockUser() {
  const email = 'test@example.com';
  const password = 'password123';
  const name = 'Test User';

  try {
    const existing = db.prepare('SELECT id FROM users WHERE email = ?').get(email);
    if (!existing) {
      const passwordHash = bcrypt.hashSync(password, 10);
      const stmt = db.prepare('INSERT INTO users (name, email, password_hash, is_verified) VALUES (?, ?, ?, ?)');
      const info = stmt.run(name, email, passwordHash, 1);
      
      // Add some sample habits
      const insertHabit = db.prepare('INSERT INTO habits (user_id, habit_name) VALUES (?, ?)');
      insertHabit.run(info.lastInsertRowid, 'Morning Run');
      insertHabit.run(info.lastInsertRowid, 'Read 10 Pages');
      insertHabit.run(info.lastInsertRowid, 'Drink Water');

      console.log('✅ Mock user created successfully!');
    } else {
      console.log('✅ Mock user already exists!');
    }
    
    console.log('\n--- Test Credentials ---');
    console.log(`Email:    ${email}`);
    console.log(`Password: ${password}`);
    console.log('------------------------\n');
  } catch (error) {
    console.error('Error creating mock user:', error);
  }
}

createMockUser();
