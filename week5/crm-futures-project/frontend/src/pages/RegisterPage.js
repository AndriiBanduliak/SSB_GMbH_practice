import React, { useState, useContext, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

function RegisterPage() {
  const { t } = useTranslation();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { register, isLoading, authError, clearAuthError } = useContext(AuthContext);
  const navigate = useNavigate();
  const [successMessage, setSuccessMessage] = useState('');

  // Clear errors/messages on mount or input change
   useEffect(() => {
    clearAuthError();
    setSuccessMessage('');
  }, [clearAuthError, username, email, password]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const success = await register({ username, email, password });
    if (success) {
      setSuccessMessage(t('register.success'));
      setTimeout(() => {
          navigate('/login');
      }, 2500); // Slightly longer delay
    }
    // Error displayed via authError
  };

  return (
    <div>
      <h2>{t('register.title')}</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="regUsername">{t('register.username')}:</label>
          <input
            type="text"
            id="regUsername"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={isLoading || successMessage} // Disable if successful too
          />
        </div>
        {/* Removed <br /> */}
        <div>
          <label htmlFor="regEmail">{t('register.email')}:</label>
          <input
            type="email"
            id="regEmail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading || successMessage}
          />
        </div>
        {/* Removed <br /> */}
        <div>
          <label htmlFor="regPassword">{t('register.password')}:</label>
          <input
            type="password"
            id="regPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            disabled={isLoading || successMessage}
          />
        </div>
        {/* Removed <br /> */}
        {authError && <p style={{ color: 'red', marginTop: '10px' }}>{authError}</p>}
        {successMessage && <p style={{ color: 'green', marginTop: '10px' }}>{successMessage}</p>}
        <button type="submit" disabled={isLoading || successMessage} style={{ marginTop: '15px' }}>
          {isLoading ? 'Registering...' : t('register.register_button')}
        </button>
      </form>
       <p style={{ marginTop: '20px' }}>
          {t('register.have_account')} <Link to="/login">{t('register.login_link')}</Link>
      </p>
    </div>
  );
}

export default RegisterPage;
