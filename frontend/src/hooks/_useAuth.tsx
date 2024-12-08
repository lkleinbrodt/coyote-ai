import { useEffect, useState } from "react";

import Cookies from "js-cookie";
import { useNavigate } from "react-router-dom";

interface User {
  id: number;
  email: string;
  name: string;
  image: string;
  token: string;
}

const useAuth = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const userCookie = Cookies.get("user");

    if (userCookie) {
      setUser(JSON.parse(userCookie));
    }
  }, [navigate]);

  return { user, setUser };
};

export default useAuth;
