import axiosInstance from "@/utils/axiosInstance";
import Cookies from "js-cookie";

export const poeltlApi = {
  getPerson: async () => {
    const response = await axiosInstance.get("/poeltl/get-person");
    return response.data;
  },

  askQuestion: async (
    messages: { role: string; content: string }[],
    person: string
  ) => {
    const response = await fetch(
      `${axiosInstance.defaults.baseURL}/poeltl/ask`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${Cookies.get("accessToken") || ""}`,
        },
        body: JSON.stringify({
          messages,
          person,
        }),
        credentials: "include",
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.body;
  },
};
