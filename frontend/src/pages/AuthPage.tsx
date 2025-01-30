import { Navigate, useSearchParams } from "react-router-dom";

import Cookies from "js-cookie"; // To store the token as a cookie
import { isValidRedirectPath } from "../utils/routes";

const AuthPage = () => {
  const [searchParams] = useSearchParams();
  const accessToken = searchParams.get("access_token");
  const next = searchParams.get("next") || "/";

  // Validate the access token exists
  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  // Validate the next path
  console.log("next", next);
  const redirectTo = isValidRedirectPath(next) ? next : "/";
  console.log("redirectTo", redirectTo);
  // Store the token in a secure cookie
  Cookies.set("accessToken", accessToken, { secure: true, sameSite: "strict" });
  const user = JSON.parse(atob(accessToken.split(".")[1]));

  const userDict = {
    id: user.sub,
    email: user.email,
    name: user.name,
    image: user.picture,
    token: accessToken,
  };

  Cookies.set("user", JSON.stringify(userDict), {
    secure: true,
    sameSite: "strict",
  });

  return <Navigate to={redirectTo} replace />;
};

export default AuthPage;
