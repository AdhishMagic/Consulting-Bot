import React, { useState } from 'react'
import './styles.css'
import Chat from './Chat'
import VoiceRecorder from './VoiceRecorder'
import { Toasts } from './Toasts'

export default function App() {
  const [toasts, setToasts] = useState([])
  function pushToast(msg, type='info'){ setToasts(t => [...t, { id: Date.now()+Math.random(), msg, type }]) }
  function removeToast(id){ setToasts(t => t.filter(x => x.id !== id)) }

  return (
    <div className="single-dashboard">
      <h1>Consulting Bot</h1>
      <p className="muted" style={{marginBottom:24}}>Conversational AI assistant for scheduling, payments, and support. Integrated with Gemini (fallback demo mode if API key absent), calendar, OTP, email and voice.</p>
      <div className="app-shell">
        <div className="panel" style={{minHeight:560}}>
          <div className="panel-header">
            <h2>Chat Assistant</h2>
          </div>
          <Chat pushToast={pushToast} />
        </div>
        <div style={{display:'flex', flexDirection:'column', gap:24}}>
          <div className="panel">
            <VoiceRecorder />
          </div>
          <div className="panel">
            <h2>System Overview</h2>
            <ul style={{paddingLeft:18, margin:0, fontSize:13, lineHeight:1.6}}>
              <li><strong>Bookings:</strong> Calendar + DB linked events</li>
              <li><strong>Payments:</strong> Razorpay link generation</li>
              <li><strong>Email:</strong> Gmail API confirmations</li>
              <li><strong>OTP:</strong> Vonage verification flow</li>
              <li><strong>AI:</strong> Gemini with tool calls (when enabled)</li>
              <li><strong>Voice:</strong> Upload + live transcript UI</li>
            </ul>
            <p className="small muted" style={{marginTop:12}}>Use the chat to ask about availability, create bookings, or get generic assistance.</p>
          </div>
        </div>
      </div>
      <Toasts items={toasts} remove={removeToast} />
    </div>
  )
}
