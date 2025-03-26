import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  // Получаем тему из localStorage или используем 'light' по умолчанию
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  // Сохраняем тему в localStorage при изменении
  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.body.className = theme; // Обновляем класс на body
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  const changeTheme = (newTheme) => {
    if (newTheme === 'light' || newTheme === 'dark') {
      setTheme(newTheme);
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, changeTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
