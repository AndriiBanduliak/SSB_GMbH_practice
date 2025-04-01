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
  const { user } = useContext(AuthContext); // Get user data for initial state

  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [selectedTheme, setSelectedTheme] = useState(theme);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Update local state if user data (potentially with saved prefs) becomes available
  // or if global language/theme contexts change
  useEffect(() => {
      setSelectedLanguage(user?.language || language);
      setSelectedTheme(user?.theme || theme);
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
      // Update global contexts immediately for instant UI feedback
      changeAppLanguage(response.data.language);
      changeTheme(response.data.theme);
      setMessage(t('settings.success'));
      // Note: User data in AuthContext might not update until next login or /auth/me call
    } catch (err) {
      // 401 errors are handled by the interceptor (redirect)
      if (err.response?.status !== 401) {
          const errorMsg = err.response?.data?.message || t('settings.error');
          console.error("Error saving settings:", errorMsg, err.response);
          setError(errorMsg);
      } else {
          // Optionally show a generic message if needed, but interceptor handles the redirect
          // setError("Authentication error. Please log in again.");
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
          <label style={{ marginRight: '10px' }}>
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
