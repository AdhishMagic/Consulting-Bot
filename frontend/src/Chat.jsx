import React, { useEffect, useRef, useState } from 'react'
import { BACKEND_URL } from './config'

// Simple chat component hitting /chat
export default function Chat({ pushToast }) {
  const [messages, setMessages] = useState([
    { id: 'sys-welcome', role: 'system', text: 'Welcome! Ask me about bookings, availability, payments or general questions.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [userId] = useState('visitor') // could be enhanced with auth/session
  const endRef = useRef(null)

  useEffect(() => { if(endRef.current){ endRef.current.scrollIntoView({ behavior: 'smooth' }) } }, [messages])

  async function sendMessage() {
    const trimmed = input.trim()
    if(!trimmed) return
    const userMsg = { id: Date.now()+':u', role: 'user', text: trimmed }
    setMessages(msgs => [...msgs, userMsg])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch(BACKEND_URL + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed, user_id: userId })
      })
      let data = null
      try { data = await res.json() } catch {}
      if(data && data.success && data.data && typeof data.data.response === 'string') {
        appendBot(data.data.response)
      } else {
        const fallback = (data && (data.error || data.data?.response)) || 'Unexpected response format.'
        appendBot('Error: ' + fallback)
        pushToast('Chat error: ' + fallback, 'error')
      }
    } catch (e) {
      appendBot('Connection error: ' + e.message)
      pushToast('Network error contacting backend', 'error')
    } finally {
      setLoading(false)
    }
  }

  function appendBot(text){
    setMessages(msgs => [...msgs, { id: Date.now()+':b', role: 'bot', text }])
  }

  function handleKey(e){
    if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); sendMessage(); }
  }

  return (
    <div className='chat-window'>
      <div className='chat-messages'>
        {messages.map(m => (
          <div key={m.id} className={`message ${m.role}`}> 
            {m.text}
            {m.role !== 'system' && <span className='timestamp'>{new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>}
          </div>
        ))}
        {loading && (
          <div className='message bot'>
            <div className='loader-dots'>
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>
      <div className='chat-input-row'>
        <textarea
          placeholder='Type your question...'
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
        />
        <div style={{display:'flex', flexDirection:'column', gap:8}}>
          <button onClick={sendMessage} disabled={!input.trim() || loading}>Send</button>
          <button type='button' className='secondary-btn' onClick={() => setMessages(ms => ms.filter(m => m.role !== 'system'))} disabled={!messages.some(m => m.role !== 'system')}>Clear</button>
        </div>
      </div>
    </div>
  )
}
