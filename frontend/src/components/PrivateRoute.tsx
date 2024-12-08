import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

const PrivateRoute = () => {
  const { user, loading } = useAuth();

  // Wait for the authentication check to complete
  if (loading) {
    return null; // or return a loading spinner
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default PrivateRoute;
