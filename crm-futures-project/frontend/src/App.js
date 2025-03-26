import React, { useContext } from 'react';
import { Routes, Route, Link, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ThemeContext } from './contexts/ThemeContext';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
// import LoginPage from './pages/LoginPage'; // Импортируйте страницы, когда они будут

function App() {
  const { theme } = useContext(ThemeContext);
  const { t } = useTranslation();

  // Простая проверка аутентификации (замените на реальную логику)
  const isAuthenticated = true; // Placeholder

  // Применяем класс темы к body
  React.useEffect(() => {
    document.body.className = theme; // 'light' или 'dark'
  }, [theme]);

  return (
    <div className={`app-container ${theme}`}>
      {/* Простая навигация для примера */}
      {isAuthenticated && (
        <nav>
          <ul>
            <li><Link to="/dashboard">{t('navigation.dashboard')}</Link></li>
            <li><Link to="/settings">{t('navigation.settings')}</Link></li>
          </ul>
          {/* Кнопка смены темы для демонстрации */}
          {/* <button onClick={toggleTheme}>Toggle Theme</button> */}
        </nav>
      )}

      <main>
        <Routes>
          {/* <Route path="/login" element={<LoginPage />} /> */}
          <Route
            path="/dashboard"
            element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/settings"
            element={isAuthenticated ? <Settings /> : <Navigate to="/login" replace />}
          />
          {/* Главная страница или редирект */}
          <Route
            path="/"
            element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />}
          />
          {/* Добавьте страницу входа /login */}
          <Route path="/login" element={<div>Login Page Placeholder</div>} />
          {/* Заглушка для 404 */}
          <Route path="*" element={<div>404 Not Found</div>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
