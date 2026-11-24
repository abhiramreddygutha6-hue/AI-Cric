import { useEffect, useRef, useState } from 'react'
import { api } from '../services/api.js'

const STARTERS = [
  'Who are the best bowlers in the death overs?',
  'Compare V Kohli\u2019s strike rate by phase.',
  'How has V Kohli done against JJ Bumrah?',
]

export default function ChatPanel() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, busy, open])

  async function send(text) {
    const content = text.trim()
    if (!content || busy) return
    const next = [...messages, { role: 'user', content }]
    setMessages(next)
    setInput('')
    setError(null)
    setBusy(true)
    try {
      const history = next.slice(-20).map(({ role, content: c }) => ({ role, content: c }))
      const res = await api.post('/chat', { messages: history })
      setMessages([...next, { role: 'assistant', content: res.reply, tools: res.tools_used }])
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  if (!open) {
    return <button className="chat-fab" onClick={() => setOpen(true)}>Ask AiCric</button>
  }

  return (
    <aside className="chat" aria-label="AiCric assistant">
      <header className="chat-head">
        <strong>Ask AiCric</strong>
        <button onClick={() => setOpen(false)} aria-label="Close chat">Close</button>
      </header>
      <div className="chat-body">
        {messages.length === 0 && (
          <div>
            <p className="muted">Ask about players, matchups or match plans. Numbers come from your imported matches.</p>
            {STARTERS.map((s) => (
              <button key={s} className="chat-starter" onClick={() => send(s)}>{s}</button>
            ))}
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            {m.content}
            {m.tools && m.tools.length > 0 && <div className="bubble-note">Looked up: {[...new Set(m.tools)].join(', ')}</div>}
          </div>
        ))}
        {busy && <p className="muted">Looking at the numbers…</p>}
        {error && <p className="error">{error}</p>}
        <div ref={endRef} />
      </div>
      <form className="chat-form" onSubmit={(e) => { e.preventDefault(); send(input) }}>
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask a question" disabled={busy} />
        <button type="submit" disabled={busy || !input.trim()}>Send</button>
      </form>
    </aside>
  )
}
