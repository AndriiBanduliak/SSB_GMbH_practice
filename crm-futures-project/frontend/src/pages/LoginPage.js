import React, { useState, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

function LoginPage() {
  const [username, setUsername] = useState(''); // Может быть username или email
  const [password, setPassword] = useState('');
  const { login, isLoading, authError, clearAuthError } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  // Откуда пользователь пришел (если был редирект с защищенной страницы)
  const from = location.state?.from?.pathname || "/dashboard"; // По умолчанию на дашборд

  const handleSubmit = async (event) => {
    event.preventDefault();
    clearAuthError(); // Сброс предыдущей ошибки
    const success = await login({ username, password }); // Используем username для обоих случаев
    if (success) {
      // Перенаправляем на исходную страницу или дашборд
      navigate(from, { replace: true });
    }
    // Ошибка будет отображена через authError из контекста
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="loginUsername">Username or Email:</label>
          <input
            type="text"
            id="loginUsername"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        <br />
        <div>
          <label htmlFor="loginPassword">Password:</label>
          <input
            type="password"
            id="loginPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        <br />
        {authError && <p style={{ color: 'red' }}>{authError}</p>}
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p>
          Don't have an account? <a href="/register">Register here</a>
      </p>
    </div>
  );
}

export default LoginPage;