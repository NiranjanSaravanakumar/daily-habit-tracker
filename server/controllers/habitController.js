const db = require('../database/db');

// ── Get all habits for the logged-in user ───────────────────────────────────

function getHabits(req, res) {
  try {
    const userId = req.user.userId;
    const today = new Date().toISOString().split('T')[0];

    const habits = db.prepare(`
      SELECT h.id, h.habit_name, h.created_at,
             COALESCE(hl.completed, 0) AS completed_today
      FROM habits h
      LEFT JOIN habit_logs hl ON hl.habit_id = h.id AND hl.date = ?
      WHERE h.user_id = ?
      ORDER BY h.created_at DESC
    `).all(today, userId);

    res.status(200).json({ habits });
  } catch (err) {
    console.error('Get habits error:', err);
    res.status(500).json({ error: 'Internal server error.' });
  }
}

// ── Add a new habit ─────────────────────────────────────────────────────────

function addHabit(req, res) {
  try {
    const userId = req.user.userId;
    const { habit_name } = req.body;

    if (!habit_name || !habit_name.trim()) {
      return res.status(400).json({ error: 'Habit name is required.' });
    }

    const result = db.prepare('INSERT INTO habits (user_id, habit_name) VALUES (?, ?)').run(userId, habit_name.trim());

    res.status(201).json({
      message: 'Habit created.',
      habit: { id: result.lastInsertRowid, habit_name: habit_name.trim() },
    });
  } catch (err) {
    console.error('Add habit error:', err);
    res.status(500).json({ error: 'Internal server error.' });
  }
}

// ── Delete a habit ──────────────────────────────────────────────────────────

function deleteHabit(req, res) {
  try {
    const userId = req.user.userId;
    const habitId = req.params.id;

    const habit = db.prepare('SELECT id FROM habits WHERE id = ? AND user_id = ?').get(habitId, userId);

    if (!habit) {
      return res.status(404).json({ error: 'Habit not found.' });
    }

    db.prepare('DELETE FROM habits WHERE id = ? AND user_id = ?').run(habitId, userId);

    res.status(200).json({ message: 'Habit deleted.' });
  } catch (err) {
    console.error('Delete habit error:', err);
    res.status(500).json({ error: 'Internal server error.' });
  }
}

// ── Mark habit as completed for today (toggle) ─────────────────────────────

function completeHabit(req, res) {
  try {
    const userId = req.user.userId;
    const habitId = req.params.id;
    const today = new Date().toISOString().split('T')[0];

    // Verify ownership
    const habit = db.prepare('SELECT id FROM habits WHERE id = ? AND user_id = ?').get(habitId, userId);

    if (!habit) {
      return res.status(404).json({ error: 'Habit not found.' });
    }

    // Toggle: if log exists, remove it; otherwise, create it
    const existingLog = db.prepare('SELECT id FROM habit_logs WHERE habit_id = ? AND date = ?').get(habitId, today);

    if (existingLog) {
      db.prepare('DELETE FROM habit_logs WHERE id = ?').run(existingLog.id);
      res.status(200).json({ message: 'Habit unmarked.', completed: false });
    } else {
      db.prepare('INSERT INTO habit_logs (habit_id, date, completed) VALUES (?, ?, 1)').run(habitId, today);
      res.status(200).json({ message: 'Habit completed!', completed: true });
    }
  } catch (err) {
    console.error('Complete habit error:', err);
    res.status(500).json({ error: 'Internal server error.' });
  }
}

// ── Daily progress ──────────────────────────────────────────────────────────

function getProgress(req, res) {
  try {
    const userId = req.user.userId;
    const today = new Date().toISOString().split('T')[0];

    const totalHabits = db.prepare('SELECT COUNT(*) AS count FROM habits WHERE user_id = ?').get(userId).count;

    const completedHabits = db.prepare(`
      SELECT COUNT(*) AS count
      FROM habit_logs hl
      JOIN habits h ON h.id = hl.habit_id
      WHERE h.user_id = ? AND hl.date = ? AND hl.completed = 1
    `).get(userId, today).count;

    const percentage = totalHabits > 0 ? Math.round((completedHabits / totalHabits) * 100) : 0;

    res.status(200).json({
      total: totalHabits,
      completed: completedHabits,
      percentage,
    });
  } catch (err) {
    console.error('Get progress error:', err);
    res.status(500).json({ error: 'Internal server error.' });
  }
}

module.exports = { getHabits, addHabit, deleteHabit, completeHabit, getProgress };
