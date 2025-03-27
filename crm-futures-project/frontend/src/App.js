import React, { useContext } from 'react';
import { Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ThemeContext } from './contexts/ThemeContext';
import { AuthContext } from './contexts/AuthContext'; // <-- Импорт AuthContext
import ProtectedRoute from './components/ProtectedRoute'; // <-- Импорт ProtectedRoute
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import LoginPage from './pages/LoginPage';     // <-- Импорт LoginPage
import RegisterPage from './pages/RegisterPage'; // <-- Импорт RegisterPage

function App() {
  const { theme } = useContext(ThemeContext);
  const { t } = useTranslation();
  const { isAuthenticated, logout, user } = useContext(AuthContext); // <-- Получаем статус и logout
  const navigate = useNavigate(); // Для программного редиректа при выходе

  React.useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  const handleLogout = () => {
      logout();
      navigate('/login'); // Перенаправляем на страницу входа после выхода
  };

  return (
    <div className={`app-container ${theme}`}>
      {/* Показываем навигацию только если пользователь аутентифицирован */}
      {isAuthenticated && (
        <nav>
          <ul>
            <li><Link to="/dashboard">{t('navigation.dashboard')}</Link></li>
            <li><Link to="/settings">{t('navigation.settings')}</Link></li>
            {/* Добавьте другие ссылки */}
          </ul>
          <div style={{ float: 'right', paddingRight: '10px' }}>
              {user && <span>Welcome, {user.username}! </span>}
              <button onClick={handleLogout}>Logout</button>
          </div>
        </nav>
      )}

      <main style={{ paddingTop: isAuthenticated ? '50px' : '0' }}> {/* Добавляем отступ, если есть навбар */}
        <Routes>
          {/* Публичные роуты */}
          <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/dashboard" replace />} />
          <Route path="/register" element={!isAuthenticated ? <RegisterPage /> : <Navigate to="/dashboard" replace />} />

          {/* Защищенные роуты */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
          {/* Добавьте другие защищенные роуты здесь, оборачивая их в ProtectedRoute */}

          {/* Главная страница или редирект */}
          <Route
            path="/"
            element={
              isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
            }
          />
          {/* Заглушка для 404 */}
          <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;