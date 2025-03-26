import React, { createContext, useState, useEffect } from 'react';
import i18n from '../i18n'; // Импортируем инстанс i18next

export const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  // Получаем язык из localStorage или используем 'en' по умолчанию
  const [language, setLanguage] = useState(() => localStorage.getItem('language') || 'en');

  // Меняем язык в i18next и сохраняем в localStorage
  useEffect(() => {
    i18n.changeLanguage(language);
    localStorage.setItem('language', language);
  }, [language]);

  const changeLanguage = (newLang) => {
    if (['en', 'de', 'ru'].includes(newLang)) {
      setLanguage(newLang);
    }
  };

  return (
    <LanguageContext.Provider value={{ language, changeLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};
