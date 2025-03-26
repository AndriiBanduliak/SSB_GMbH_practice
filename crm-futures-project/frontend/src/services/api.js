import axios from 'axios';

// Создаем инстанс axios
// baseURL будет автоматически подставляться перед /api/...
// В Docker окружении Nginx перенаправит /api на бэкенд
const apiClient = axios.create({
  baseURL: '/api', // Используем относительный путь для Nginx proxy
  headers: {
    'Content-Type': 'application/json'
  },
});

// Перехватчик для добавления токена (пример)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken'); // Получаем токен
  if (token) {
    config.headers.Authorization = "Bearer " + token;

  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Функции для работы с API
export const getSettings = () => {
  return apiClient.get('/settings/'); // Запрос на GET /api/settings/
};

export const updateSettings = (settingsData) => {
  // settingsData = { language: 'en', theme: 'dark' }
  return apiClient.put('/settings/', settingsData); // Запрос на PUT /api/settings/
};

export default apiClient;
