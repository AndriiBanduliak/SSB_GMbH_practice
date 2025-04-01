import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enTranslation from './locales/en.json';
import deTranslation from './locales/de.json';
import ruTranslation from './locales/ru.json';

const resources = {
  en: { translation: enTranslation },
  de: { translation: deTranslation },
  ru: { translation: ruTranslation },
};

const savedLanguage = localStorage.getItem('language');

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage || 'en', // Use saved language or default to 'en'
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
     debug: process.env.NODE_ENV === 'development', // Enable debug logs in development
  });

export default i18n;
