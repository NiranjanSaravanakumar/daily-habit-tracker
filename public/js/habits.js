/**
 * habits.js – Dashboard logic: fetch habits, add, delete, toggle completion, show progress.
 */

const API_HABITS = '/api/habits';

// ── Auth Guard ──────────────────────────────────────────────────────────────

const token = localStorage.getItem('token');
if (!token) {
  window.location.href = 'login.html';
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

// ── Greeting ────────────────────────────────────────────────────────────────

(function setGreeting() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const greetingEl = document.getElementById('greeting');
  if (user.name && greetingEl) {
    const hour = new Date().getHours();
    let timeGreeting = 'Good evening';
    if (hour < 12) timeGreeting = 'Good morning';
    else if (hour < 18) timeGreeting = 'Good afternoon';
    greetingEl.textContent = `${timeGreeting}, ${user.name}! Stay consistent.`;
  }
})();

// ── Alert ───────────────────────────────────────────────────────────────────

function showAlert(message, type = 'error') {
  const alert = document.getElementById('alert');
  alert.textContent = message;
  alert.className = `alert alert-${type}`;
  alert.style.display = 'block';
  setTimeout(() => { alert.style.display = 'none'; }, 4000);
}

// ── Render Habits ───────────────────────────────────────────────────────────

function renderHabits(habits) {
  const list = document.getElementById('habitsList');
  const emptyState = document.getElementById('emptyState');

  if (!habits.length) {
    list.innerHTML = '';
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';

  list.innerHTML = habits
    .map(
      (h) => `
    <div class="habit-card ${h.completed_today ? 'completed' : ''}" data-id="${h.id}">
      <label class="habit-checkbox">
        <input type="checkbox" ${h.completed_today ? 'checked' : ''} onchange="toggleHabit(${h.id})">
        <span class="checkmark"></span>
      </label>
      <span class="habit-name">${escapeHtml(h.habit_name)}</span>
      <button class="btn-delete" onclick="deleteHabit(${h.id})">✕ Remove</button>
    </div>
  `
    )
    .join('');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ── Fetch Habits ────────────────────────────────────────────────────────────

async function fetchHabits() {
  try {
    const res = await fetch(API_HABITS, { headers: authHeaders() });

    if (res.status === 401) {
      localStorage.clear();
      window.location.href = 'login.html';
      return;
    }

    const data = await res.json();
    renderHabits(data.habits || []);
    fetchProgress();
  } catch (err) {
    showAlert('Failed to load habits.');
  }
}

// ── Add Habit ───────────────────────────────────────────────────────────────

async function addHabit() {
  const input = document.getElementById('habitInput');
  const habitName = input.value.trim();

  if (!habitName) return;

  try {
    const res = await fetch(API_HABITS, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ habit_name: habitName }),
    });

    if (!res.ok) {
      const data = await res.json();
      showAlert(data.error || 'Failed to add habit.');
      return;
    }

    input.value = '';
    fetchHabits();
  } catch (err) {
    showAlert('Network error.');
  }
}

// ── Delete Habit ────────────────────────────────────────────────────────────

async function deleteHabit(id) {
  try {
    const res = await fetch(`${API_HABITS}/${id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    });

    if (!res.ok) {
      const data = await res.json();
      showAlert(data.error || 'Failed to delete habit.');
      return;
    }

    fetchHabits();
  } catch (err) {
    showAlert('Network error.');
  }
}

// ── Toggle Completion ───────────────────────────────────────────────────────

async function toggleHabit(id) {
  try {
    const res = await fetch(`${API_HABITS}/${id}/complete`, {
      method: 'POST',
      headers: authHeaders(),
    });

    if (!res.ok) {
      const data = await res.json();
      showAlert(data.error || 'Failed to update habit.');
      fetchHabits();
      return;
    }

    fetchHabits();
  } catch (err) {
    showAlert('Network error.');
    fetchHabits();
  }
}

// ── Fetch Progress ──────────────────────────────────────────────────────────

async function fetchProgress() {
  try {
    const res = await fetch(`${API_HABITS}/progress`, { headers: authHeaders() });
    const data = await res.json();

    document.getElementById('progressBar').style.width = `${data.percentage}%`;
    document.getElementById('progressText').textContent = `${data.completed} of ${data.total} completed`;
    document.getElementById('progressPercentage').textContent = `${data.percentage}%`;
  } catch (err) {
    // silently fail – progress is non-critical
  }
}

// ── Event Listeners ─────────────────────────────────────────────────────────

document.getElementById('addHabitBtn').addEventListener('click', addHabit);

document.getElementById('habitInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') addHabit();
});

document.getElementById('logoutBtn').addEventListener('click', () => {
  localStorage.clear();
  window.location.href = 'login.html';
});

// ── Init ────────────────────────────────────────────────────────────────────
fetchHabits();
