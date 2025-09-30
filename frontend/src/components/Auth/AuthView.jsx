import "./AuthView.css";

function AuthView({
  isRegister,
  username,
  password,
  onUsernameChange,
  onPasswordChange,
  onSubmit,
  onToggleMode,
}) {
  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>{isRegister ? "Crear cuenta" : "Iniciar sesion"}</h2>
        <input
          type="text"
          placeholder="Usuario"
          value={username}
          onChange={(event) => onUsernameChange(event.target.value)}
        />
        <input
          type="password"
          placeholder="Contrasena"
          value={password}
          onChange={(event) => onPasswordChange(event.target.value)}
        />
        <button onClick={onSubmit}>{isRegister ? "Registrarse" : "Entrar"}</button>
        <p>
          {isRegister ? "Ya tienes cuenta?" : "No tienes cuenta?"}{" "}
          <span onClick={onToggleMode}>{isRegister ? "Inicia sesion" : "Registrate"}</span>
        </p>
      </div>
    </div>
  );
}

export default AuthView;