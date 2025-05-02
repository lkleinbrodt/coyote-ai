import Cookies from "js-cookie";
import axios from "axios";

// Create an axios instance with base URL and default configuration
const axiosInstance = axios.create({
  baseURL: `${import.meta.env.VITE_BASE_URL}api`, // Base URL for all API calls
  withCredentials: true, // Send cookies with requests
});

// Add a request interceptor to inject the JWT token into the headers
axiosInstance.interceptors.request.use(
  async (config) => {
    const token = Cookies.get("accessToken");

    if (token) {
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

// Helper function to handle streaming responses
export const streamResponse = async (
  url: string,
  data: Record<string, unknown>,
  onData: (data: Record<string, unknown>) => void,
  onError: (error: unknown) => void,
  onComplete: () => void
) => {
  try {
    const response = await fetch(`${axiosInstance.defaults.baseURL}${url}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        Authorization: `Bearer ${Cookies.get("accessToken")}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error("Response body is null");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      let boundary = buffer.indexOf("\n\n");
      while (boundary >= 0) {
        const message = buffer.substring(0, boundary);
        buffer = buffer.substring(boundary + 2);

        if (message.startsWith("data:")) {
          const dataString = message.substring(5).trim();
          if (dataString) {
            try {
              const data = JSON.parse(dataString);
              onData(data);
            } catch (e) {
              console.error(`Error parsing stream JSON:`, e);
            }
          }
        }

        boundary = buffer.indexOf("\n\n");
      }
    }

    onComplete();
  } catch (error) {
    onError(error);
  }
};

export default axiosInstance;
