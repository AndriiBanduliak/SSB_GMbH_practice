import React, { createContext, useState, useEffect, useCallback } from 'react';
import { loginUser as apiLogin, registerUser as apiRegister } from '../services/api';
import apiClient from '../services/api'; // Import apiClient for direct use if needed

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authToken, setAuthToken] = useState(() => localStorage.getItem('authToken') || null);
  const [userData, setUserData] = useState(() => {
      const storedUser = localStorage.getItem('userData');
      try {
          return storedUser ? JSON.parse(storedUser) : null;
      } catch (e) {
          console.error("Failed to parse user data from localStorage", e);
          localStorage.removeItem('userData');
          return null;
      }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [authError, setAuthError] = useState(null);

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
        return true;
      } else {
          // Handle cases where API might return 200 OK but no token/user
          throw new Error("Invalid login response from server");
      }
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.message || "Login failed. Please check credentials.";
      console.error("Login failed:", errorMsg);
      setAuthError(errorMsg);
      setAuthToken(null);
      setUserData(null);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (registerData) => { // Renamed from 'userData' to avoid confusion
      setIsLoading(true);
      setAuthError(null);
      try {
          await apiRegister(registerData);
          return true;
      } catch (error) {
          const errorMsg = error.response?.data?.message || error.message || "Registration failed. Please try again.";
          console.error("Registration failed:", errorMsg);
          setAuthError(errorMsg);
          return false;
      } finally {
          setIsLoading(false);
      }
  }, []);

  const logout = useCallback(() => {
    console.log("Logging out...");
    setAuthToken(null);
    setUserData(null);
    // localStorage is cleared by useEffect
  }, []);

  // Optional: Verify token on initial load or refresh
  // const verifyAuth = useCallback(async () => {
  //    if (!authToken) return;
  //    setIsLoading(true);
  //    try {
  //        const response = await apiClient.get('/auth/me'); // Assuming you added /auth/me endpoint
  //        setUserData(response.data.user);
  //    } catch (error) {
  //        // If /auth/me returns 401, the token is invalid/expired
  //        if (error.response && error.response.status === 401) {
  //            console.warn("Auth token verification failed, logging out.");
  //            logout();
  //        } else {
  //            console.error("Error verifying auth token:", error);
  //        }
  //    } finally {
  //        setIsLoading(false);
  //    }
  // }, [authToken, logout]);

  // useEffect(() => {
  //    verifyAuth();
  // }, [verifyAuth]); // Run only once on mount if needed

  const value = {
    isAuthenticated: !!authToken,
    token: authToken,
    user: userData,
    isLoading,
    authError,
    login,
    register,
    logout,
    clearAuthError: () => setAuthError(null)
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
