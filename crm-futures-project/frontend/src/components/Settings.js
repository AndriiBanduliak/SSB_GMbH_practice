import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { ThemeContext } from '../contexts/ThemeContext';
import { LanguageContext } from '../contexts/LanguageContext';
import { AuthContext } from '../contexts/AuthContext';
import { updateSettings } from '../services/api';

function Settings() {
  const { t } = useTranslation();
  const { theme, changeTheme } = useContext(ThemeContext);
  const { language, changeLanguage: changeAppLanguage } = useContext(LanguageContext);
  const { user } = useContext(AuthContext);

  // Используем данные пользователя из контекста как начальное значение, если они есть
  const [selectedLanguage, setSelectedLanguage] = useState(user?.language || language);
  const [selectedTheme, setSelectedTheme] = useState(user?.theme || theme);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Синхронизация при изменении user из AuthContext (например, после логина)
  useEffect(() => {
      if (user) {
          setSelectedLanguage(user.language);
          setSelectedTheme(user.theme);
      }
      // Добавляем language и theme как зависимости, чтобы синхронизировать
      // если они изменятся в контексте до того, как загрузится user
  }, [user, language, theme]);

  const handleSave = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setMessage('');
    setError('');
    try {
      const response = await updateSettings({
        language: selectedLanguage,
        theme: selectedTheme,
      });
      // Обновляем контексты языка и темы сразу для мгновенного отклика UI
      changeAppLanguage(response.data.language);
      changeTheme(response.data.theme);
      setMessage(t('settings.success'));
      // Данные пользователя (user) в AuthContext обновятся при следующем
      // получении данных с бэкенда или перезагрузке страницы (если есть запрос /me)
    } catch (err) { // Переименовал переменную, чтобы избежать путаницы с useState `error`
      console.error("Error saving settings:", err.response?.data?.message || err.message);
      // Ошибка 401 (Unauthorized) должна обрабатываться Axios интерцептором
      if (err.response?.status !== 401) {
          setError(err.response?.data?.message || t('settings.error'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>{t('settings.title')}</h2>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSave}>
        <div>
          <label htmlFor="languageSelect">{t('settings.language')}: </label>
          <select
            id="languageSelect"
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            disabled={isLoading}
          >
            <option value="en">English</option>
            <option value="de">Deutsch</option>
            <option value="ru">Русский</option>
          </select>
        </div>
        <br />
        <div>
          <label>{t('settings.theme')}: </label>
          <label style={{ marginRight: '10px' }}> {/* Добавил отступ */}
            <input
              type="radio"
              name="theme"
              value="light"
              checked={selectedTheme === 'light'}
              onChange={(e) => setSelectedTheme(e.target.value)}
              disabled={isLoading}
            /> {t('settings.light')}
          </label>
          <label>
            <input
              type="radio"
              name="theme"
              value="dark"
              checked={selectedTheme === 'dark'}
              onChange={(e) => setSelectedTheme(e.target.value)}
              disabled={isLoading}
            /> {t('settings.dark')}
          </label>
        </div>
        <br />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : t('settings.save')}
        </button>
      </form>
    </div>
  );
}

export default Settings;