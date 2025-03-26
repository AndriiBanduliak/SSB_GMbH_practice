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

i18n
  .use(initReactI18next) // передаем инстанс i18n в react-i18next
  .init({
    resources,
    lng: localStorage.getItem('language') || 'en', // язык по умолчанию
    fallbackLng: 'en', // язык, если текущий недоступен

    interpolation: {
      escapeValue: false, // не нужно для React, т.к. он сам защищает от XSS
    },
  });

export default i18n;
