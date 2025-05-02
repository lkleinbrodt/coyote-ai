import { AuthResponse, User } from "@/types/auth";

import axiosInstance from "@/utils/axiosInstance";

export const authService = {
  login: async (provider: string, nextPath: string = "/"): Promise<void> => {
    const encodedPath = encodeURIComponent(nextPath);
    window.location.href = `${
      import.meta.env.VITE_BASE_URL
    }api/auth/authorize/${provider}?next=${encodedPath}`;
  },

  handleAuthCallback: async (accessToken: string): Promise<User> => {
    try {
      const user = JSON.parse(atob(accessToken.split(".")[1]));
      return {
        id: user.sub,
        email: user.email,
        name: user.name,
        image: user.picture,
        token: accessToken,
      };
    } catch (error) {
      throw new Error("Invalid access token format");
    }
  },

  logout: async (): Promise<void> => {
    // Clear all auth-related data
    localStorage.removeItem("authError");
    // Note: We don't need to call a backend endpoint since we're using JWT
    // The token is simply invalidated by removing it from cookies
  },

  refreshToken: async (): Promise<AuthResponse> => {
    try {
      const response = await axiosInstance.post("/auth/refresh");
      return response.data;
    } catch (error) {
      throw new Error("Failed to refresh token");
    }
  },
};
