import React, { useContext } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useContext(AuthContext);
  const location = useLocation(); // Для перенаправления обратно после логина

  if (!isAuthenticated) {
    // Если пользователь не аутентифицирован, перенаправляем на /login
    // state={{ from: location }} позволяет вернуться на исходную страницу после входа
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Если аутентифицирован, отображаем дочерний компонент (например, Dashboard)
  return children;
};

export default ProtectedRoute;