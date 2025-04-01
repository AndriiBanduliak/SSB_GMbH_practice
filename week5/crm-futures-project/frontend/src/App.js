import React, { useContext } from 'react';
import { Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ThemeContext } from './contexts/ThemeContext';
import { AuthContext } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
// TODO: Import ContactsPage when created

function App() {
  const { theme } = useContext(ThemeContext);
  const { t } = useTranslation();
  const { isAuthenticated, logout, user } = useContext(AuthContext);
  const navigate = useNavigate();

  React.useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  const handleLogout = () => {
      logout();
      navigate('/login');
  };

  return (
    <div className={`app-container ${theme}`}>
      {isAuthenticated && (
        <nav style={{ padding: '10px', borderBottom: '1px solid #ccc', marginBottom: '20px', overflow: 'hidden' }}>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0, float: 'left' }}>
            <li style={{ display: 'inline-block', marginRight: '15px' }}><Link to="/dashboard">{t('navigation.dashboard')}</Link></li>
            {/* TODO: Add link to Contacts page */}
            {/* <li style={{ display: 'inline-block', marginRight: '15px' }}><Link to="/contacts">Contacts</Link></li> */}
            <li style={{ display: 'inline-block', marginRight: '15px' }}><Link to="/settings">{t('navigation.settings')}</Link></li>
          </ul>
          <div style={{ float: 'right', paddingRight: '10px' }}>
              {user && <span>Welcome, {user.username}! </span>}
              <button onClick={handleLogout}>Logout</button>
          </div>
        </nav>
      )}

      <main style={{ padding: '0 20px 20px 20px' }}>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/dashboard" replace />} />
          <Route path="/register" element={!isAuthenticated ? <RegisterPage /> : <Navigate to="/dashboard" replace />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          {/* TODO: Add route for ContactsPage */}
          {/* <Route
            path="/contacts"
            element={
              <ProtectedRoute>
                <ContactsPage />
              </ProtectedRoute>
            }
          /> */}
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />

          {/* Root path redirect */}
          <Route
            path="/"
            element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
            }
          />
          {/* 404 Not Found */}
          <Route path="*" element={<div><h2>404 Not Found</h2><p>The page you are looking for does not exist.</p></div>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
