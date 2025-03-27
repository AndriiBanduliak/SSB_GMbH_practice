import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext'; // Используем для isLoading и ошибок

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { register, isLoading, authError, clearAuthError } = useContext(AuthContext);
  const navigate = useNavigate();
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    clearAuthError();
    setSuccessMessage('');
    const success = await register({ username, email, password });
    if (success) {
      // Показываем сообщение и/или перенаправляем на логин
      setSuccessMessage('Registration successful! Redirecting to login...');
      setTimeout(() => {
          navigate('/login');
      }, 2000); // Задержка для чтения сообщения
    }
    // Ошибка отображается через authError
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="regUsername">Username:</label>
          <input
            type="text"
            id="regUsername"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        <br />
        <div>
          <label htmlFor="regEmail">Email:</label>
          <input
            type="email"
            id="regEmail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        <br />
        <div>
          <label htmlFor="regPassword">Password:</label>
          <input
            type="password"
            id="regPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6} // Хорошо бы дублировать проверку с бэкенда
            disabled={isLoading}
          />
        </div>
        <br />
        {authError && <p style={{ color: 'red' }}>{authError}</p>}
        {successMessage && <p style={{ color: 'green' }}>{successMessage}</p>}
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Registering...' : 'Register'}
        </button>
      </form>
       <p>
          Already have an account? <a href="/login">Login here</a>
      </p>
    </div>
  );
}

export default RegisterPage;