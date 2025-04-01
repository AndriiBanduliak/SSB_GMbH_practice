import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api', // Proxied by Nginx in Docker, or by react-scripts proxy in dev
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Axios Interceptors ---

// Request Interceptor: Adds JWT token to Authorization header
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    // Log request details only in development
    if (process.env.NODE_ENV === 'development') {
        console.log(`--- API Request --- ${config.method.toUpperCase()} ${config.url}`);
        if (token) {
            console.log("Authorization header ADDED");
        } else {
             console.log("Authorization header NOT added");
        }
    }
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error("Request Interceptor Error:", error);
    return Promise.reject(error);
  }
);

// Response Interceptor: Handles 401 Unauthorized errors globally
apiClient.interceptors.response.use(
  (response) => {
    return response; // Pass through successful responses
  },
  (error) => {
    // Check if it's a 401 error
    if (error.response && error.response.status === 401) {
      console.warn('API returned 401 Unauthorized. Token might be invalid or expired.');
      // Check if we are not already on the login page to avoid infinite loops
      if (window.location.pathname !== '/login') {
        // Clear potentially invalid token and user data
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        // Redirect to login page
        // Using window.location.href is simpler but causes a full page reload.
        // A more integrated approach would use the useNavigate hook from react-router-dom
        // passed down via context or props, but this is safer for a global interceptor.
        console.log('Redirecting to /login due to 401.');
        window.location.href = '/login';
      } else {
          console.log('Already on login page, not redirecting.');
      }
    }
    // Reject the promise so the error can be handled by the calling code (.catch block)
    return Promise.reject(error);
  }
);


// --- API Service Functions ---

// Auth
export const registerUser = (userData) => apiClient.post('/auth/register', userData);
export const loginUser = (credentials) => apiClient.post('/auth/login', credentials);
export const getCurrentUser = () => apiClient.get('/auth/me'); // For verifying token / getting user data

// Settings
export const getSettings = () => apiClient.get('/settings/');
export const updateSettings = (settingsData) => apiClient.put('/settings/', settingsData);

// Contacts
export const getContacts = (sortBy = 'first_name', sortOrder = 'asc') => {
    return apiClient.get('/contacts/', {
        params: {
            sort_by: sortBy,
            sort_order: sortOrder
        }
    });
};
// TODO: Add functions for POST, PUT, DELETE contacts

export default apiClient; // Export instance for potential direct use
