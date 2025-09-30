import { useEffect, useRef } from "react";
import {
  FiMenu,
  FiPlus,
  FiTrash2,
  FiMessageSquare,
  FiSearch,
  FiBook,
  FiSettings,
} from "react-icons/fi";
import Logo from "../../assets/logo.png";
import "./Sidebar.css";

function Sidebar({
  isOpen,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onToggleSidebar,
  isNewChatDisabled,
  showConfig,
  onToggleConfig,
  onCloseConfig,
  showThemeMenu,
  onToggleThemeMenu,
  onChangeTheme,
  theme,
  onLogout,
}) {
  const configWrapperRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!showConfig) {
        return;
      }

      if (configWrapperRef.current && !configWrapperRef.current.contains(event.target)) {
        onCloseConfig();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showConfig, onCloseConfig]);

  const themeLabel = theme === "system" ? "Sistema" : theme === "dark" ? "Oscuro" : "Claro";

  return (
    <aside className={`sidebar ${isOpen ? "open" : ""}`}>
      <div className="sidebar__header">
        {isOpen ? (
          <>
            <div className="logo-fixed">
              <img src={Logo} alt="Logo" className="logo-img" />
            </div>
            <button className="hamburger--small" onClick={() => onToggleSidebar(false)} title="Cerrar">
              <FiMenu />
            </button>
          </>
        ) : (
          <button className="logo-button" onClick={() => onToggleSidebar(true)} title="Abrir">
            <img src={Logo} alt="Logo" className="logo-img" />
            <FiMenu className="logo-menu" />
          </button>
        )}
      </div>

      {!isOpen && (
        <div className="sidebar__shortcuts">
          <button title="Nuevo chat" onClick={onNewConversation} disabled={isNewChatDisabled}>
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

      {isOpen && (
        <div className="sidebar__nav">
          <div
            className={`sidebar__item ${isNewChatDisabled ? "is-disabled" : ""}`}
            onClick={() => !isNewChatDisabled && onNewConversation()}
          >
            <FiPlus /> <span>Nuevo chat</span>
          </div>
          <div className="sidebar__item">
            <FiSearch /> <span>Buscar chats</span>
          </div>
          <div className="sidebar__item">
            <FiBook /> <span>Biblioteca</span>
          </div>

          <div className="sidebar__section">Chats</div>
          <div className="sidebar__chats">
            {Object.entries(conversations).map(([conversationId, conversation]) => (
              <div
                key={conversationId}
                className={`conv-item ${activeConversationId === conversationId ? "is-active" : ""}`}
                onClick={() => onSelectConversation(conversationId)}
              >
                <FiMessageSquare />
                <span>{conversation.title || "Nueva conversacion"}</span>
                <button
                  className="conv-item__delete"
                  onClick={(event) => {
                    event.stopPropagation();
                    onDeleteConversation(conversationId);
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
        <div className="sidebar__config-wrapper" ref={configWrapperRef}>
          <div className="sidebar__item" onClick={onToggleConfig}>
            <FiSettings /> {isOpen && <span>Configuracion</span>}
          </div>

          {showConfig && (
            <div className={`config-popup ${isOpen ? "from-sidebar" : "from-quick"}`}>
              <div className="config-option" onClick={onToggleThemeMenu}>
                Tema
                <span className="config-value">{themeLabel}</span>
              </div>

              {showThemeMenu && (
                <div className="submenu">
                  <div className="submenu-option" onClick={() => onChangeTheme("system")}>
                    Sistema {theme === "system" ? "(actual)" : ""}
                  </div>
                  <div className="submenu-option" onClick={() => onChangeTheme("dark")}>
                    Oscuro {theme === "dark" ? "(actual)" : ""}
                  </div>
                  <div className="submenu-option" onClick={() => onChangeTheme("light")}>
                    Claro {theme === "light" ? "(actual)" : ""}
                  </div>
                </div>
              )}

              <div className="config-separator" />
              <div className="config-option logout" onClick={onLogout}>
                Cerrar sesion
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;