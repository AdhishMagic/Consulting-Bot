import React, { useEffect } from 'react'

export function Toasts({ items, remove }) {
  useEffect(() => {
    const timers = items.map(t => setTimeout(() => remove(t.id), t.ttl || 4000))
    return () => timers.forEach(clearTimeout)
  }, [items, remove])

  return (
    <div className="toast-container">
      {items.map(t => (
        <div key={t.id} className={`toast toast--${t.type}`}>{t.msg}</div>
      ))}
    </div>
  )
}