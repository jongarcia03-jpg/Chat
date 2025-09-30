import { useCallback, useEffect, useRef, useState } from "react";
import AuthView from "./components/Auth/AuthView";
import Sidebar from "./components/Sidebar/Sidebar";
import ChatWindow from "./components/Chat/ChatWindow";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState({});
  const [activeConversationId, setActiveConversationId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);

  const [theme, setTheme] = useState(localStorage.getItem("theme") || "system");
  const [showConfig, setShowConfig] = useState(false);
  const [showThemeMenu, setShowThemeMenu] = useState(false);

  const messagesEndRef = useRef(null);
  const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const applyTheme = useCallback((selected) => {
    if (selected === "system") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      document.body.classList.toggle("light-theme", !prefersDark);
    } else {
      document.body.classList.toggle("light-theme", selected === "light");
    }
  }, []);

  useEffect(() => {
    applyTheme(theme);
  }, [theme, applyTheme]);

  const changeTheme = (newTheme) => {
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    setShowThemeMenu(false);
    setShowConfig(false);
  };

  const handleToggleConfig = () => {
    setShowConfig((previous) => {
      const next = !previous;
      if (!next) {
        setShowThemeMenu(false);
      }
      return next;
    });
  };

  const handleCloseConfig = useCallback(() => {
    setShowConfig(false);
    setShowThemeMenu(false);
  }, []);

  const logout = () => {
    setToken(null);
    localStorage.removeItem("token");
    setShowConfig(false);
    setShowThemeMenu(false);
    setActiveConversationId(null);
    setMessages([]);
    setConversations({});
  };

  const login = async () => {
    const response = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      setToken(data.token);
      localStorage.setItem("token", data.token);
      await refreshConversations();
    } else {
      alert("Credenciales incorrectas");
    }
  };

  const register = async () => {
    const response = await fetch(`${API_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      alert("Usuario registrado. Ahora inicia sesion.");
      setIsRegister(false);
    } else {
      const error = await response.json();
      alert(error.detail || "Error al registrar");
    }
  };

  const refreshConversations = async () => {
    if (!token) {
      return;
    }

    const response = await fetch(`${API_URL}/conversations`, {
      headers: { Authorization: token },
    });

    if (!response.ok) {
      return;
    }

    const data = await response.json();
    setConversations(data);
  };

  const loadConversation = async (conversationId) => {
    const response = await fetch(`${API_URL}/conversations/${conversationId}`, {
      headers: { Authorization: token },
    });

    if (!response.ok) {
      return;
    }

    const data = await response.json();
    setActiveConversationId(conversationId);
    setMessages(data.history || []);
  };

  const newConversation = async () => {
    const response = await fetch(`${API_URL}/conversations`, {
      method: "POST",
      headers: { Authorization: token },
    });

    if (!response.ok) {
      return;
    }

    const data = await response.json();
    const updated = { ...conversations, [data.id]: { title: data.title } };
    setConversations(updated);
    setActiveConversationId(data.id);
    setMessages([]);
  };

  const deleteConversation = async (conversationId) => {
    await fetch(`${API_URL}/conversations/${conversationId}`, {
      method: "DELETE",
      headers: { Authorization: token },
    });

    await refreshConversations();

    if (activeConversationId === conversationId) {
      setActiveConversationId(null);
      setMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) {
      return;
    }

    const userMessage = { role: "user", content: input };
    const typingMessage = { role: "assistant", content: "Asistente escribiendo..." };
    setMessages((previous) => [...previous, userMessage, typingMessage]);
    setInput("");
    setLoading(true);

    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: token,
      },
      body: JSON.stringify({ message: userMessage.content }),
    });

    const data = await response.json();
    setMessages(data.history || []);
    setLoading(false);

    await refreshConversations();
  };

  const speakLast = async () => {
    const lastBot = [...messages].reverse().find((message) => message.role === "assistant");
    if (!lastBot) {
      return;
    }

    const response = await fetch(`${API_URL}/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: lastBot.content }),
    });

    const data = await response.json();
    const audioUrl = (data.audio_url || "").replace("backend", "localhost");

    if (!audioUrl) {
      return;
    }

    const audio = new Audio(audioUrl);
    audio.play();
  };

  useEffect(() => {
    if (!token) {
      return;
    }

    (async () => {
      await refreshConversations();
      const ids = Object.keys(conversations || {});
      if (ids.length > 0) {
        const lastId = ids[ids.length - 1];
        await loadConversation(lastId);
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
    activeConversationId &&
    (!messages || messages.length === 0 || !messages.some((message) => message.role === "user"));

  if (!token) {
    return (
      <AuthView
        isRegister={isRegister}
        username={username}
        password={password}
        onUsernameChange={setUsername}
        onPasswordChange={setPassword}
        onSubmit={isRegister ? register : login}
        onToggleMode={() => setIsRegister((previous) => !previous)}
      />
    );
  }

  return (
    <div className="app">
      <Sidebar
        isOpen={sidebarOpen}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={loadConversation}
        onNewConversation={newConversation}
        onDeleteConversation={deleteConversation}
        onToggleSidebar={setSidebarOpen}
        isNewChatDisabled={isNewChatDisabled}
        showConfig={showConfig}
        onToggleConfig={handleToggleConfig}
        onCloseConfig={handleCloseConfig}
        showThemeMenu={showThemeMenu}
        onToggleThemeMenu={() => setShowThemeMenu((previous) => !previous)}
        onChangeTheme={changeTheme}
        theme={theme}
        onLogout={logout}
      />

      <ChatWindow
        isSidebarOpen={sidebarOpen}
        messages={messages}
        loading={loading}
        input={input}
        onInputChange={setInput}
        onSendMessage={sendMessage}
        onSpeakLast={speakLast}
        messagesEndRef={messagesEndRef}
      />
    </div>
  );
}

export default App;