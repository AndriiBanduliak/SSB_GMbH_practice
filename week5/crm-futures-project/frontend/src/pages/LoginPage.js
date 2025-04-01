import React, { useState, useContext, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

function LoginPage() {
  const { t } = useTranslation();
  const [identifier, setIdentifier] = useState(''); // Can be username or email
  const [password, setPassword] = useState('');
  const { login, isLoading, authError, clearAuthError } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || "/dashboard";

  // Clear error when component mounts or identifier/password changes
  useEffect(() => {
    clearAuthError();
  }, [clearAuthError, identifier, password]);


  const handleSubmit = async (event) => {
    event.preventDefault();
    // Use 'identifier' for both username/email field
    const success = await login({ username: identifier, password });
    if (success) {
      console.log("Login successful, navigating to:", from);
      navigate(from, { replace: true });
    }
    // Error is displayed via authError from context
  };

  return (
    <div>
      <h2>{t('login.title')}</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="loginIdentifier">{t('login.username_email')}:</label>
          <input
            type="text"
            id="loginIdentifier"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        {/* Removed <br /> for better spacing with CSS margins */}
        <div>
          <label htmlFor="loginPassword">{t('login.password')}:</label>
          <input
            type="password"
            id="loginPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        {/* Removed <br /> */}
        {authError && <p style={{ color: 'red', marginTop: '10px' }}>{authError}</p>}
        <button type="submit" disabled={isLoading} style={{ marginTop: '15px' }}>
          {isLoading ? 'Logging in...' : t('login.login_button')}
        </button>
      </form>
      <p style={{ marginTop: '20px' }}>
          {t('login.no_account')} <Link to="/register">{t('login.register_link')}</Link>
      </p>
    </div>
  );
}

export default LoginPage;
