import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

type Props = { children: JSX.Element };

const ProtectedRoute: React.FC<Props> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Read token directly so navigation works immediately after login
  const hasToken = (() => {
    try {
      return Boolean(localStorage.getItem("access_token"));
    } catch {
      return false;
    }
  })();

  // If there's no token yet, you can show the loading spinner while AuthContext initializes.
  if (!hasToken && isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-mega-primary" />
      </div>
    );
  }

  const authed = hasToken || isAuthenticated;
  if (!authed) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

export default ProtectedRoute;
