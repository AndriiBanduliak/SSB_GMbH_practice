import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Axios Interceptors ---

// 1. Request Interceptor: Добавляем токен к исходящим запросам
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    // Добавляем подробные логи:
    console.log("--- Request Interceptor START ---");
    console.log("Request URL:", config.url);
    console.log("Token from localStorage:", token ? "Found" : "NOT Found");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log("Authorization header ADDED");
    } else {
      console.log("Authorization header NOT added");
    }
    console.log("--- Request Interceptor END ---");
    return config;
  },
  (error) => {
    console.error("Request Interceptor Error:", error);
    return Promise.reject(error);
  }
);

// 2. Response Interceptor (Опционально, но полезно): Обработка ошибок авторизации
apiClient.interceptors.response.use(
  (response) => {
    // Если ответ успешный, просто возвращаем его
    return response;
  },
  (error) => {
    // Если сервер вернул 401 Unauthorized (токен невалиден или истек)
    if (error.response && error.response.status === 401) {
      // Удаляем невалидный токен
      localStorage.removeItem('authToken');
      // Удаляем данные пользователя (если хранятся)
      localStorage.removeItem('userData');
      // Перенаправляем на страницу входа
      // Используем window.location для простоты, в реальном приложении лучше через React Router
      if (window.location.pathname !== '/login') {
         console.warn('Unauthorized or token expired. Redirecting to login.');
         window.location.href = '/login'; // Или используйте navigate из react-router-dom
      }
    }
    // Возвращаем ошибку для дальнейшей обработки (например, в .catch() компонента)
    return Promise.reject(error);
  }
);


// --- API Функции ---

export const getSettings = () => {
  return apiClient.get('/settings/');
};

export const updateSettings = (settingsData) => {
  return apiClient.put('/settings/', settingsData);
};

// Новые функции для аутентификации
export const registerUser = (userData) => {
    // userData = { username: '...', email: '...', password: '...' }
    return apiClient.post('/auth/register', userData);
};

export const loginUser = (credentials) => {
    // credentials = { username: '...' (or email), password: '...' }
    return apiClient.post('/auth/login', credentials);
};

// Экспортируем инстанс (для возможного прямого использования, но обычно лучше через функции)
export default apiClient;