/**
 * auth.js – Handles signup, OTP verification, and login forms.
 */

const API = '/api/auth';

// ── Helpers ─────────────────────────────────────────────────────────────────

function showAlert(message, type = 'error') {
  const alert = document.getElementById('alert');
  alert.textContent = message;
  alert.className = `alert alert-${type}`;
  alert.style.display = 'block';
}

function hideAlert() {
  const alert = document.getElementById('alert');
  alert.style.display = 'none';
}

function setLoading(btn, loading) {
  if (loading) {
    btn.dataset.originalText = btn.textContent;
    btn.innerHTML = '<span class="spinner"></span>Please wait…';
    btn.disabled = true;
  } else {
    btn.textContent = btn.dataset.originalText || btn.textContent;
    btn.disabled = false;
  }
}

// ── Signup Form ─────────────────────────────────────────────────────────────

const signupForm = document.getElementById('signupForm');
if (signupForm) {
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert();

    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const btn = document.getElementById('signupBtn');

    if (password.length < 6) {
      return showAlert('Password must be at least 6 characters.');
    }

    setLoading(btn, true);

    try {
      const res = await fetch(`${API}/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(data.error || 'Signup failed.');
        setLoading(btn, false);
        return;
      }

      // Store email for OTP page
      localStorage.setItem('otp_email', email);
      showAlert(data.message, 'success');

      setTimeout(() => {
        window.location.href = 'otp.html';
      }, 1000);
    } catch (err) {
      showAlert('Network error. Please try again.');
      setLoading(btn, false);
    }
  });
}

// ── OTP Form ────────────────────────────────────────────────────────────────

const otpForm = document.getElementById('otpForm');
if (otpForm) {
  // Redirect if no email is stored
  const email = localStorage.getItem('otp_email');
  if (!email) {
    window.location.href = 'signup.html';
  }

  otpForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert();

    const otp = document.getElementById('otp').value.trim();
    const btn = document.getElementById('otpBtn');

    if (otp.length !== 6) {
      return showAlert('Please enter a valid 6-digit OTP.');
    }

    setLoading(btn, true);

    try {
      const res = await fetch(`${API}/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(data.error || 'Verification failed.');
        setLoading(btn, false);
        return;
      }

      localStorage.removeItem('otp_email');
      showAlert(data.message, 'success');

      setTimeout(() => {
        window.location.href = 'login.html';
      }, 1200);
    } catch (err) {
      showAlert('Network error. Please try again.');
      setLoading(btn, false);
    }
  });
}

// ── Login Form ──────────────────────────────────────────────────────────────

const loginForm = document.getElementById('loginForm');
if (loginForm) {
  // If already logged in, redirect to dashboard
  if (localStorage.getItem('token')) {
    window.location.href = 'dashboard.html';
  }

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const btn = document.getElementById('loginBtn');

    setLoading(btn, true);

    try {
      const res = await fetch(`${API}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(data.error || 'Login failed.');
        setLoading(btn, false);
        return;
      }

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));

      showAlert('Login successful!', 'success');

      setTimeout(() => {
        window.location.href = 'dashboard.html';
      }, 800);
    } catch (err) {
      showAlert('Network error. Please try again.');
      setLoading(btn, false);
    }
  });
}
