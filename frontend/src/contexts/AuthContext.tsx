import {
  ReactNode,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import Cookies from "js-cookie";
import { useNavigate } from "react-router-dom";

interface User {
  id: number;
  email: string;
  name: string;
  image: string;
  token: string;
}

interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  loading: boolean;
  logout: () => void;
  login: (from: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  useEffect(() => {
    const userCookie = Cookies.get("user");
    if (userCookie) {
      setUser(JSON.parse(userCookie));
    }
    setLoading(false);
  }, []);

  const handleSetUser = (newUser: User | null) => {
    console.log("handleSetUser", newUser);
    setUser(newUser);
    if (newUser) {
      Cookies.set("user", JSON.stringify(newUser));
    } else {
      Cookies.remove("user");
    }
  };

  const logout = async () => {
    await navigate("/");

    // Ensure navigation completes before clearing user state
    // React Router's navigation can be asynchronous
    await new Promise((resolve) => setTimeout(resolve, 100));

    setUser(null);
    Cookies.remove("user");
  };

  const login = (from: string) => {
    if (!from) {
      from = "/";
    }
    console.log("from", from);
    const nextPath = encodeURIComponent(from);
    console.log("nextPath", nextPath);
    const baseUrl = import.meta.env.VITE_BASE_URL;
    window.location.href = `${baseUrl}/api/auth/authorize/google?next=${nextPath}`;
  };

  return (
    <AuthContext.Provider
      value={{ user, setUser: handleSetUser, loading, logout, login }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
