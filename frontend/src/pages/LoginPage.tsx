import "./LoginPage.css";

import { useLocation } from "react-router-dom";

const Login = () => {
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";
  const handleSignIn = () => {
    const nextPath = encodeURIComponent(from);
    const baseUrl = import.meta.env.VITE_AUTH_BASE_URL;
    window.location.href = `${baseUrl}/authorize/google?next=${nextPath}`;
  };

  return (
    <div className="loginContainer">
      <button className="signInButton" onClick={handleSignIn}>
        Sign In with Google
      </button>
    </div>
  );
};

export default Login;
