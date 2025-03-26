import React, { useState, useEffect, useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { ThemeContext } from '../contexts/ThemeContext';
import { LanguageContext } from '../contexts/LanguageContext';
import { getSettings, updateSettings } from '../services/api';

function Settings() {
  const { t } = useTranslation();
  const { theme, changeTheme } = useContext(ThemeContext);
  const { language, changeLanguage: changeAppLanguage } = useContext(LanguageContext);

  // Локальное состояние для формы
  const [selectedLanguage, setSelectedLanguage] = useState(language);
  const [selectedTheme, setSelectedTheme] = useState(theme);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Синхронизация локального состояния с глобальным при монтировании
  // и при изменении глобального контекста
  useEffect(() => {
    setSelectedLanguage(language);
  }, [language]);

  useEffect(() => {
    setSelectedTheme(theme);
  }, [theme]);

  // Загрузка настроек с бэкенда при монтировании (опционально, если контекст надежен)
  // useEffect(() => {
  //   setIsLoading(true);
  //   getSettings()
  //     .then(response => {
  //       changeAppLanguage(response.data.language);
  //       changeTheme(response.data.theme);
  //       setMessage('');
  //     })
  //     .catch(error => {
  //       console.error("Error fetching settings:", error);
  //       setMessage(t('settings.error'));
  //     })
  //     .finally(() => setIsLoading(false));
  // }, [changeAppLanguage, changeTheme, t]); // Добавляем зависимости

  const handleSave = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setMessage('');
    try {
      const response = await updateSettings({
        language: selectedLanguage,
        theme: selectedTheme,
      });
      // Обновляем глобальный контекст после успешного сохранения
      changeAppLanguage(response.data.language);
      changeTheme(response.data.theme);
      setMessage(t('settings.success'));
    } catch (error) {
      console.error("Error saving settings:", error);
      setMessage(t('settings.error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>{t('settings.title')}</h2>
      {message && <p>{message}</p>}
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
          <label>
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