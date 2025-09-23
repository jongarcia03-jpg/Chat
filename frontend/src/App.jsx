import { useState, useEffect } from "react"
import "./App.css"

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [conversations, setConversations] = useState({})
  const [activeConv, setActiveConv] = useState(null)

  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

  // Cargar lista de conversaciones al iniciar
  useEffect(() => {
    fetch(`${API_URL}/conversations`)
      .then((res) => res.json())
      .then((data) => setConversations(data))
  }, [API_URL])

  const sendMessage = async () => {
    if (!input) return
    const userMsg = { role: "user", content: input }
    setMessages((prev) => [...prev, userMsg, { role: "assistant", content: "🤖 escribiendo..." }])
    setLoading(true)

    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    })
    const data = await res.json()

    setMessages(data.history)
    setInput("")
    setLoading(false)

    // Refrescar lista de conversaciones
    const convs = await fetch(`${API_URL}/conversations`).then((r) => r.json())
    setConversations(convs)
  }

  const speakLast = async () => {
    const lastBot = [...messages].reverse().find((m) => m.role === "assistant")
    if (!lastBot) return

    const res = await fetch(`${API_URL}/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: lastBot.content }),
    })
    const data = await res.json()

    // 👉 Reemplaza "backend" por "localhost" para que funcione en el navegador
    const audioUrl = data.audio_url.replace("backend", "localhost")
    const audio = new Audio(audioUrl)
    audio.play()
  }

  const newConversation = async () => {
    const res = await fetch(`${API_URL}/conversations`, { method: "POST" })
    const data = await res.json()
    setConversations((prev) => ({ ...prev, [data.id]: { title: data.title } }))
    setActiveConv(data.id)
    setMessages([])
  }

  const loadConversation = async (cid) => {
    const res = await fetch(`${API_URL}/conversations/${cid}`)
    const data = await res.json()
    setActiveConv(cid)
    setMessages(data.history)
  }

  const deleteConversation = async (cid) => {
    await fetch(`${API_URL}/conversations/${cid}`, { method: "DELETE" })
    const convs = await fetch(`${API_URL}/conversations`).then((r) => r.json())
    setConversations(convs)
    if (activeConv === cid) {
      setMessages([])
      setActiveConv(null)
    }
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <h2>Conversaciones</h2>
        <button className="new-chat" onClick={newConversation}>+ Nueva conversación</button>
        <div className="conv-list">
          {Object.entries(conversations).map(([cid, conv]) => (
            <div key={cid} className={`conv-item ${cid === activeConv ? "active" : ""}`}>
              <span onClick={() => loadConversation(cid)}>{conv.title}</span>
              <button className="delete-btn" onClick={() => deleteConversation(cid)}>🗑️</button>
            </div>
          ))}
        </div>
      </aside>

      {/* Chat principal */}
      <main className="chat-container">
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              <div className="bubble">{m.content}</div>
            </div>
          ))}
          {loading && <p className="typing">🤖 escribiendo...</p>}
        </div>

        {/* Input */}
        <div className="input-container">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu mensaje..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage}>Enviar</button>
          <button onClick={speakLast}>🔊</button>
        </div>
      </main>
    </div>
  )
}

export default App
