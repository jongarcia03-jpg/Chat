import { useEffect, useState, useRef } from "react";
import { FiMenu, FiPlus, FiSettings, FiArrowLeft } from "react-icons/fi";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState({});
  const [activeConv, setActiveConv] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  // ===== API helpers =====
  const refreshConversations = async () => {
    const data = await fetch(`${API_URL}/conversations`).then((r) => r.json());
    setConversations(data);
  };

  const loadConversation = async (cid) => {
    const data = await fetch(`${API_URL}/conversations/${cid}`).then((r) =>
      r.json()
    );
    setActiveConv(cid);
    setMessages(data.history || []);
  };

  const newConversation = async () => {
    const data = await fetch(`${API_URL}/conversations`, {
      method: "POST",
    }).then((r) => r.json());

    const updated = { ...conversations, [data.id]: { title: data.title } };
    setConversations(updated);
    setActiveConv(data.id);
    setMessages([]);
    setSidebarOpen(false);
  };

  const deleteConversation = async (cid) => {
    await fetch(`${API_URL}/conversations/${cid}`, { method: "DELETE" });
    await refreshConversations();
    if (activeConv === cid) {
      setActiveConv(null);
      setMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    const typing = { role: "assistant", content: "🤖 escribiendo..." };
    setMessages((prev) => [...prev, userMsg, typing]);
    setInput("");
    setLoading(true);

    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMsg.content }),
    });
    const data = await res.json();

    setMessages(data.history || []);
    setLoading(false);
    await refreshConversations();
  };

  const speakLast = async () => {
    const lastBot = [...messages].reverse().find((m) => m.role === "assistant");
    if (!lastBot) return;

    const res = await fetch(`${API_URL}/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: lastBot.content }),
    });
    const data = await res.json();

    const audioUrl = (data.audio_url || "").replace("backend", "localhost");
    if (!audioUrl) return;
    const audio = new Audio(audioUrl);
    audio.play();
  };

  // ===== efectos =====
  useEffect(() => {
    (async () => {
      const data = await fetch(`${API_URL}/conversations`).then((r) =>
        r.json()
      );
      setConversations(data);
      const ids = Object.keys(data);
      if (ids.length > 0) {
        const last = ids[ids.length - 1];
        await loadConversation(last);
      }
    })();
  }, [API_URL]);

  // Auto-scroll
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <div className="app">
      {/* Sidebar siempre presente (mini o completo) */}
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        {sidebarOpen ? (
          <div className="sidebar__header">
            <h2 className="sidebar__title">Conversaciones</h2>
            <button
              className="hamburger--small"
              onClick={() => setSidebarOpen(false)}
              title="Cerrar"
            >
              <FiArrowLeft />
            </button>
          </div>
        ) : (
          <div
            className="sidebar__header"
            style={{ flexDirection: "column", alignItems: "center" }}
          >
            <button
              className="hamburger--small"
              onClick={() => setSidebarOpen(true)}
              title="Abrir"
            >
              <FiMenu />
            </button>
            {/* Atajos rápidos */}
            <div
              style={{
                marginTop: "20px",
                display: "flex",
                flexDirection: "column",
                gap: "14px",
              }}
            >
              <button onClick={newConversation} title="Nueva conversación">
                <FiPlus />
              </button>
              <button title="Configuración">
                <FiSettings />
              </button>
            </div>
          </div>
        )}

        {sidebarOpen && (
          <>
            <button className="btn btn--ghost" onClick={newConversation}>
              + Nueva conversación
            </button>

            <div className="conv-list">
              {Object.entries(conversations).length === 0 && (
                <div className="conv-empty">No hay conversaciones</div>
              )}
              {Object.entries(conversations).map(([cid, conv]) => (
                <div
                  key={cid}
                  className={`conv-item ${cid === activeConv ? "is-active" : ""}`}
                >
                  <button
                    className="conv-item__btn"
                    onClick={() => {
                      loadConversation(cid);
                      setSidebarOpen(false);
                    }}
                  >
                    {conv.title}
                  </button>
                  <button
                    className="conv-item__delete"
                    onClick={() => deleteConversation(cid)}
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </aside>

      {/* Chat principal */}
      <main className={`chat ${sidebarOpen ? "shifted" : ""}`}>
        <div className="messages">
          {messages.map((m, i) => (
            <div
              key={i}
              className={`message ${
                m.role === "user" ? "message--user" : "message--bot"
              }`}
            >
              <div className="bubble">{m.content}</div>
            </div>
          ))}
          {loading && <div className="typing">🤖 escribiendo…</div>}
          {/* marcador invisible para auto-scroll */}
          <div ref={messagesEndRef} />
        </div>

        <div className="composer">
          <input
            className="composer__input"
            type="text"
            placeholder="Escribe tu mensaje…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button className="btn btn--primary" onClick={sendMessage}>
            Enviar
          </button>
          <button className="btn btn--success" onClick={speakLast}>
            🔊
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;
