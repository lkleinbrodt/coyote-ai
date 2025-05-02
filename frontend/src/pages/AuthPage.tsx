import { Navigate, useSearchParams } from "react-router-dom";

import { authService } from "@/services/auth";
import { isValidRedirectPath } from "@/utils/routes";
import { useAuth } from "@/contexts/AuthContext";

const AuthPage = () => {
  const [searchParams] = useSearchParams();
  const { setUser } = useAuth();
  const accessToken = searchParams.get("access_token");
  const next = searchParams.get("next") || "/";

  // Validate the access token exists
  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  const redirectTo = isValidRedirectPath(next) ? next : "/";

  // Handle the auth callback and set user data
  const handleAuthCallback = async () => {
    try {
      const user = await authService.handleAuthCallback(accessToken);
      setUser(user);
    } catch (error) {
      console.error("Error handling auth callback:", error);
      return <Navigate to="/login" replace />;
    }
  };

  // Call the handler immediately
  handleAuthCallback();

  return <Navigate to={redirectTo} replace />;
};

export default AuthPage;
