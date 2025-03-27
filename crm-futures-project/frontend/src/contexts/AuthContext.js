import React, { createContext, useState, useEffect, useCallback } from 'react';
import { loginUser as apiLogin, registerUser as apiRegister } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('authToken') || null);
  const [userData, setUserData] = useState(() => {
      const storedUser = localStorage.getItem('userData');
      try {
          return storedUser ? JSON.parse(storedUser) : null;
      } catch (e) {
          console.error("Failed to parse user data from localStorage", e);
          localStorage.removeItem('userData'); // Очистить некорректные данные
          return null;
      }
  });
  const [isLoading, setIsLoading] = useState(false); // Для индикаторов загрузки
  const [authError, setAuthError] = useState(null); // Для отображения ошибок

  // Эффект для обновления localStorage при изменении токена или данных пользователя
  useEffect(() => {
    if (authToken) {
      localStorage.setItem('authToken', authToken);
    } else {
      localStorage.removeItem('authToken');
    }
  }, [authToken]);

  useEffect(() => {
      if (userData) {
          localStorage.setItem('userData', JSON.stringify(userData));
      } else {
          localStorage.removeItem('userData');
      }
  }, [userData]);


  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    setAuthError(null);
    try {
      const response = await apiLogin(credentials);
      if (response.data.access_token && response.data.user) {
        setAuthToken(response.data.access_token);
        setUserData(response.data.user);
        return true; // Успешный вход
      }
    } catch (error) {
      console.error("Login failed:", error.response?.data?.message || error.message);
      setAuthError(error.response?.data?.message || "Login failed. Please check your credentials.");
      setAuthToken(null); // Убедиться, что токен сброшен при ошибке
      setUserData(null);
    } finally {
      setIsLoading(false);
    }
    return false; // Ошибка входа
  }, []);

  const register = useCallback(async (userData) => {
      setIsLoading(true);
      setAuthError(null);
      try {
          await apiRegister(userData);
          return true; // Успешная регистрация
      } catch (error) {
          console.error("Registration failed:", error.response?.data?.message || error.message);
          setAuthError(error.response?.data?.message || "Registration failed. Please try again.");
      } finally {
          setIsLoading(false);
      }
      return false; // Ошибка регистрации
  }, []);

  const logout = useCallback(() => {
    setAuthToken(null);
    setUserData(null);
    // localStorage очистится автоматически через useEffect
    // Можно добавить вызов API для блок-листа токена на бэкенде, если реализовано
    console.log("Logged out");
    // Перенаправление на /login обычно происходит в компоненте или роутере
  }, []);

  // Проверка при загрузке, валиден ли токен (опционально, требует API эндпоинта)
  // useEffect(() => {
  //   const verifyToken = async () => {
  //     if (authToken) {
  //       try {
  //          // Нужен API эндпоинт типа GET /api/auth/me или /api/auth/verify
  //          // await apiClient.get('/auth/me');
  //          // Если запрос успешен, токен валиден
  //       } catch (error) {
  //         // Если 401, токен невалиден
  //         if (error.response && error.response.status === 401) {
  //           console.warn("Stored token is invalid, logging out.");
  //           logout();
  //         }
  //       }
  //     }
  //   };
  //   verifyToken();
  // }, [authToken, logout]);


  const value = {
    isAuthenticated: !!authToken, // Проверяем наличие токена
    token: authToken,
    user: userData,
    isLoading,
    authError,
    login,
    register,
    logout,
    clearAuthError: () => setAuthError(null) // Функция для сброса ошибки
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};