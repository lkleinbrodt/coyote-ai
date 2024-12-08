import Cookies from "js-cookie"; // To store the token as a cookie
import { useAuth } from "@/contexts/AuthContext";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom"; // Import useRouter to access URL params

const AuthPage = () => {
  const navigate = useNavigate(); // Get the router instance
  const { user, setUser } = useAuth(); // Destructure setUser from useAuth hook

  useEffect(() => {
    const { searchParams } = new URL(window.location.href); // Get URL search parameters
    const token = searchParams.get("access_token"); // Get the access_token from URL params

    if (!token) {
      // Redirect to login page if no token is present
      // navigate("/login");
      console.log("No token found, redirecting to login");
      return;
    }

    // Store the token in a secure cookie
    Cookies.set("accessToken", token, { secure: true, sameSite: "strict" });
    const user = JSON.parse(atob(token.split(".")[1]));
    const userInfo = user.sub;
    const userDict = {
      id: userInfo.id,
      email: userInfo.email,
      name: userInfo.name,
      image: userInfo.picture,
      token: token,
    };

    Cookies.set("user", JSON.stringify(userDict), {
      secure: true,
      sameSite: "strict",
    });

    setUser(userInfo);
    navigate("/");
  }, [navigate, setUser]);
  //TODO: Add loading screen
  return <div>Loading... {JSON.stringify(user)}</div>;
};

export default AuthPage;
