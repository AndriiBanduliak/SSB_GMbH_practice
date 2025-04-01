import React, { createContext, useState, useEffect, useCallback } from 'react';
import i18n from '../i18n';

export const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => localStorage.getItem('language') || i18n.language || 'en');

  useEffect(() => {
    if (i18n.language !== language) {
       i18n.changeLanguage(language);
    }
    localStorage.setItem('language', language);
  }, [language]);

  // Listen to i18next language changes (e.g., from browser detector)
  useEffect(() => {
    const handleLanguageChanged = (lng) => {
        setLanguage(lng);
    };
    i18n.on('languageChanged', handleLanguageChanged);
    return () => {
      i18n.off('languageChanged', handleLanguageChanged);
    };
  }, []);


  const changeLanguage = useCallback((newLang) => {
    if (['en', 'de', 'ru'].includes(newLang)) {
      setLanguage(newLang); // This will trigger the useEffect above
    }
  }, []);

  return (
    <LanguageContext.Provider value={{ language, changeLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};
