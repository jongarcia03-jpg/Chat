import { useEffect, useState, useRef } from "react";
import {
  FiMenu,
  FiPlus,
  FiTrash2,
  FiSend,
  FiVolume2,
  FiMessageSquare,
  FiSearch,
  FiBook,
  FiSettings,
} from "react-icons/fi";
import "./App.css";
import Logo from "./assets/logo.png"; // ✅ Importa tu logo desde src/assets

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState({});
  const [activeConv, setActiveConv] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Login
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);

  // Tema y configuración
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "system");
  const [showConfig, setShowConfig] = useState(false);
  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const configRef = useRef(null);

  const applyTheme = (selected) => {
    if (selected === "system") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      document.body.classList.toggle("light-theme", !prefersDark);
    } else {
      document.body.classList.toggle("light-theme", selected === "light");
    }
  };

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const changeTheme = (newTheme) => {
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    setShowThemeMenu(false);
    setShowConfig(false);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
    setShowConfig(false);
    setActiveConv(null);
    setMessages([]);
    setConversations({});
  };

  // cerrar menús al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (configRef.current && !configRef.current.contains(e.target)) {
        setShowConfig(false);
        setShowThemeMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const messagesEndRef = useRef(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  // ===== Autenticación =====
  const login = async () => {
    const res = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (res.ok) {
      const data = await res.json();
      setToken(data.token);
      localStorage.setItem("token", data.token);
      await refreshConversations();
    } else {
      alert("Credenciales incorrectas");
    }
  };

  const register = async () => {
    const res = await fetch(`${API_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (res.ok) {
      alert("Usuario registrado. Ahora inicia sesión.");
      setIsRegister(false);
    } else {
      const err = await res.json();
      alert(err.detail || "Error al registrar");
    }
  };

  // ===== API helpers =====
  const refreshConversations = async () => {
    if (!token) return;
    const res = await fetch(`${API_URL}/conversations`, {
      headers: { Authorization: token },
    });
    if (!res.ok) return;
    const data = await res.json();
    setConversations(data);
  };

  const loadConversation = async (cid) => {
    const res = await fetch(`${API_URL}/conversations/${cid}`, {
      headers: { Authorization: token },
    });
    if (!res.ok) return;
    const data = await res.json();
    setActiveConv(cid);
    setMessages(data.history || []);
  };

  const newConversation = async () => {
    const res = await fetch(`${API_URL}/conversations`, {
      method: "POST",
      headers: { Authorization: token },
    });
    if (!res.ok) return;
    const data = await res.json();

    const updated = { ...conversations, [data.id]: { title: data.title } };
    setConversations(updated);
    setActiveConv(data.id);
    setMessages([]);
  };

  const deleteConversation = async (cid) => {
    await fetch(`${API_URL}/conversations/${cid}`, {
      method: "DELETE",
      headers: { Authorization: token },
    });
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
      headers: {
        "Content-Type": "application/json",
        Authorization: token,
      },
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
    if (!token) return;
    (async () => {
      await refreshConversations();
      const ids = Object.keys(conversations || {});
      if (ids.length > 0) {
        const last = ids[ids.length - 1];
        await loadConversation(last);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const isNewChatDisabled =
    activeConv && (!messages || messages.length === 0 || !messages.some((m) => m.role === "user"));

  // ===== Pantalla de Login / Registro =====
  if (!token) {
    return (
      <div className="auth-container">
        <div className="auth-box">
          <h2>{isRegister ? "Crear cuenta" : "Iniciar sesión"}</h2>
          <input
            type="text"
            placeholder="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={isRegister ? register : login}>
            {isRegister ? "Registrarse" : "Entrar"}
          </button>
          <p>
            {isRegister ? "¿Ya tienes cuenta?" : "¿No tienes cuenta?"}{" "}
            <span onClick={() => setIsRegister(!isRegister)}>
              {isRegister ? "Inicia sesión" : "Regístrate"}
            </span>
          </p>
        </div>
      </div>
    );
  }

  // ===== UI principal =====
  return (
    <div className="app">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="sidebar__header">
          {sidebarOpen ? (
            // ✅ Abierta: logo a la izquierda + hamburguesa a la derecha
            <>
              <div className="logo-fixed">
                <img src={Logo} alt="Logo" className="logo-img" />
              </div>
              <button
                className="hamburger--small"
                onClick={() => setSidebarOpen(false)}
                title="Cerrar"
              >
                <FiMenu />
              </button>
            </>
          ) : (
            // ✅ Cerrada: logo camuflado en hamburguesa (hover)
            <button
              className="logo-button"
              onClick={() => setSidebarOpen(true)}
              title="Abrir"
            >
              <img src={Logo} alt="Logo" className="logo-img" />
              <FiMenu className="logo-menu" />
            </button>
          )}
        </div>

        {!sidebarOpen && (
          <div className="sidebar__shortcuts">
            <button title="Nuevo chat" onClick={newConversation} disabled={isNewChatDisabled}>
              <FiPlus />
            </button>
            <button title="Buscar chats">
              <FiSearch />
            </button>
            <button title="Biblioteca">
              <FiBook />
            </button>
          </div>
        )}

        {sidebarOpen && (
          <div className="sidebar__nav">
            <div
              className={`sidebar__item ${isNewChatDisabled ? "is-disabled" : ""}`}
              onClick={() => !isNewChatDisabled && newConversation()}
            >
              <FiPlus /> <span>Nuevo chat</span>
            </div>
            <div className="sidebar__item">
              <FiSearch /> <span>Buscar chats</span>
            </div>
            <div className="sidebar__item">
              <FiBook /> <span>Biblioteca</span>
            </div>

            <div className="sidebar__section">CHATS</div>
            <div className="sidebar__chats">
              {Object.entries(conversations).map(([cid, conv]) => (
                <div
                  key={cid}
                  className={`conv-item ${activeConv === cid ? "is-active" : ""}`}
                  onClick={() => loadConversation(cid)}
                >
                  <FiMessageSquare />
                  <span>{conv.title || "Nueva conversación"}</span>
                  <button
                    className="conv-item__delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(cid);
                    }}
                  >
                    <FiTrash2 />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="sidebar__footer">
          <div className="sidebar__item" onClick={() => setShowConfig(!showConfig)} ref={configRef}>
            <FiSettings /> {sidebarOpen && <span>Configuración</span>}
          </div>
        </div>

        {showConfig && (
          <div className={`config-popup ${sidebarOpen ? "from-sidebar" : "from-quick"}`} ref={configRef}>
            <div className="config-option" onClick={() => setShowThemeMenu(!showThemeMenu)}>
              Tema
              <span className="config-value">
                {theme === "system" ? "Sistema" : theme === "dark" ? "Oscuro" : "Claro"} ▼
              </span>
            </div>

            {showThemeMenu && (
              <div className="submenu">
                <div className="submenu-option" onClick={() => changeTheme("system")}>
                  Sistema {theme === "system" && "✓"}
                </div>
                <div className="submenu-option" onClick={() => changeTheme("dark")}>
                  Oscuro {theme === "dark" && "✓"}
                </div>
                <div className="submenu-option" onClick={() => changeTheme("light")}>
                  Claro {theme === "light" && "✓"}
                </div>
              </div>
            )}

            <div className="config-separator"></div>
            <div className="config-option logout" onClick={logout}>
              Cerrar sesión
            </div>
          </div>
        )}
      </aside>

      <main className={`chat ${sidebarOpen ? "shifted" : ""}`}>
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role === "user" ? "message--user" : "message--bot"}`}>
              <div className="bubble">{m.content}</div>
            </div>
          ))}
          {loading && <div className="typing">🤖 escribiendo…</div>}
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
            <FiSend />
          </button>
          <button className="btn btn--success" onClick={speakLast}>
            <FiVolume2 />
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;
