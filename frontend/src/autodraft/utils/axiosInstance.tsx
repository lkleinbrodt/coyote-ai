import Cookies from "js-cookie";
import axios from "axios";

// Create an axios instance with base URL and default configuration
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_AUTH_BASE_URL + "/autodraft/",
  withCredentials: true, // Send cookies with requests
});

// Add a request interceptor to inject the JWT token into the headers
axiosInstance.interceptors.request.use(
  async (config) => {
    const token = Cookies.get("accessToken");

    if (token) {
      // Set the Authorization header with the Bearer token
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.setItem("authError", "Session expired. Please login again.");
      Cookies.remove("accessToken");
      Cookies.remove("user");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
