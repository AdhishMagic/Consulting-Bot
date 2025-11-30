import React from 'react'
import './styles.css'

export default function App() {
  return (
    <div className="single-dashboard">
      <h1>Consulting Bot Dashboard</h1>
      <p>
        This simple dashboard describes what the bot backend does.
        The backend is a FastAPI service providing endpoints and integrations
        to power consulting workflows: bookings, calendars, payments, email,
        OTP verification, AI assistance, and voice features.
      </p>
      <ul className="bullet-points">
        <li><strong>Authentication:</strong> User sessions and OTP via `auth.py` and `otp_client.py`.</li>
        <li><strong>Bookings:</strong> Create/manage appointments via `bookings.py` and `calendar_client.py`.</li>
        <li><strong>Calendar:</strong> Schedule, update, cancel events with external providers.</li>
        <li><strong>Payments:</strong> Handle payment intents and confirmations in `payment.py`.</li>
        <li><strong>Email:</strong> Send/read confirmations and notifications via `gmail_client.py`.</li>
        <li><strong>AI/Gemini:</strong> Use `gemini_client.py` for AI-driven responses.</li>
        <li><strong>Database:</strong> Persist records via `database.py` and `models.py`.</li>
        <li><strong>Utilities:</strong> Common helpers in `utils.py` across services.</li>
        <li><strong>API Entry:</strong> FastAPI app in `app/main.py` exposes HTTP endpoints.</li>
      </ul>
      <p className="note">
        Frontend reduced to a single page for clarity. Use the tasks
        to run: Backend (Uvicorn) and Frontend (Vite).
      </p>
    </div>
  )
}
