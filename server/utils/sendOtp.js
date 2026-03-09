const nodemailer = require('nodemailer');

/**
 * Send a 6-digit OTP to the given email address.
 * Falls back to console logging if email credentials are not configured.
 */
async function sendOtp(email, otpCode) {
  const emailUser = process.env.EMAIL_USER;
  const emailPass = process.env.EMAIL_PASS;

  // If email credentials are not set, log OTP to console (dev mode)
  if (!emailUser || !emailPass || emailUser === 'your_email@gmail.com') {
    console.log('──────────────────────────────────────');
    console.log(`📧  OTP for ${email}: ${otpCode}`);
    console.log('──────────────────────────────────────');
    return;
  }

  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: emailUser,
      pass: emailPass,
    },
  });

  const mailOptions = {
    from: `"Habit Tracker" <${emailUser}>`,
    to: email,
    subject: 'Your Verification Code – Habit Tracker',
    html: `
      <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px;background:#1a1a2e;color:#e0e0e0;border-radius:12px;">
        <h2 style="color:#7c3aed;margin-top:0;">Habit Tracker</h2>
        <p>Your verification code is:</p>
        <div style="font-size:36px;font-weight:700;letter-spacing:8px;text-align:center;padding:16px;background:#16213e;border-radius:8px;color:#a78bfa;">
          ${otpCode}
        </div>
        <p style="margin-top:16px;font-size:13px;color:#888;">This code expires in 5 minutes. If you did not request this, please ignore this email.</p>
      </div>
    `,
  };

  await transporter.sendMail(mailOptions);
}

module.exports = sendOtp;
