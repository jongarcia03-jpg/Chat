import { FiSend, FiVolume2 } from "react-icons/fi";
import "./ChatWindow.css";

function ChatWindow({
  isSidebarOpen,
  messages,
  loading,
  input,
  onInputChange,
  onSendMessage,
  onSpeakLast,
  messagesEndRef,
}) {
  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      onSendMessage();
    }
  };

  return (
    <main className={`chat ${isSidebarOpen ? "shifted" : ""}`}>
      <div className="messages">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`message ${message.role === "user" ? "message--user" : "message--bot"}`}
          >
            <div className="bubble">{message.content}</div>
          </div>
        ))}
        {loading && <div className="typing">Asistente escribiendo...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="composer">
        <input
          className="composer__input"
          type="text"
          placeholder="Escribe tu mensaje..."
          value={input}
          onChange={(event) => onInputChange(event.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="btn btn--primary" onClick={onSendMessage}>
          <FiSend />
        </button>
        <button className="btn btn--success" onClick={onSpeakLast}>
          <FiVolume2 />
        </button>
      </div>
    </main>
  );
}

export default ChatWindow;