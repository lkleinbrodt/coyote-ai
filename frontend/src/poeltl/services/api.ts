import axiosInstance from "@/utils/axiosInstance";

export const poeltlApi = {
  getPerson: async () => {
    const response = await axiosInstance.get("/poeltl/get-person");
    return response.data;
  },

  askQuestion: async (
    messages: { role: string; content: string }[],
    person: string
  ) => {
    const response = await axiosInstance.post("/poeltl/ask", {
      messages,
      person,
    });
    return response.data;
  },
};
