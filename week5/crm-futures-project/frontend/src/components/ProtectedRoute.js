import React, { useContext } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useContext(AuthContext); // Added isLoading
  const location = useLocation();

  // Optional: Show a loading indicator while auth state is being verified
  // if (isLoading) {
  //   return <div>Loading...</div>; // Or a spinner component
  // }

  if (!isAuthenticated) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to. This allows us to send them along to that page after they login,
    // which is a nicer user experience than dropping them off on the home page.
    console.log("ProtectedRoute: Not authenticated, redirecting to login.");
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children; // Render the component if authenticated
};

export default ProtectedRoute;
