import { AuthState, User } from "@/types/auth";
import {
  ReactNode,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import Cookies from "js-cookie";
import { authService } from "@/services/auth";
import { useNavigate } from "react-router-dom";

interface AuthContextType extends AuthState {
  setUser: (user: User | null) => void;
  logout: () => Promise<void>;
  login: (provider: string, from?: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
  });
  const navigate = useNavigate();

  useEffect(() => {
    const userCookie = Cookies.get("user");
    if (userCookie) {
      try {
        setState((prev) => ({
          ...prev,
          user: JSON.parse(userCookie),
          loading: false,
        }));
      } catch (error) {
        console.error("Error parsing user cookie:", error);
        setState((prev) => ({
          ...prev,
          loading: false,
          error: { message: "Invalid user data" },
        }));
      }
    } else {
      setState((prev) => ({ ...prev, loading: false }));
    }
  }, []);

  const handleSetUser = (newUser: User | null) => {
    setState((prev) => ({ ...prev, user: newUser, error: null }));
    if (newUser) {
      Cookies.set("user", JSON.stringify(newUser), {
        secure: true,
        sameSite: "strict",
      });
    } else {
      Cookies.remove("user");
    }
  };

  const logout = async () => {
    await authService.logout();
    await navigate("/");
    // Ensure navigation completes before clearing user state
    await new Promise((resolve) => setTimeout(resolve, 100));
    handleSetUser(null);
  };

  const login = async (from: string = "/") => {
    const provider = "google";
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      await authService.login(provider, from);
    } catch (error) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: { message: "Failed to initiate login" },
      }));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        setUser: handleSetUser,
        logout,
        login,
      }}
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
