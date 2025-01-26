export const poeltlApi = {
  getPerson: async () => {
    const response = await fetch("/api/twenty-questions/get-person", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  askQuestion: async (
    messages: { role: string; content: string }[],
    person: string
  ) => {
    const response = await fetch("/api/poeltl/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ messages, person }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.body;
  },
};
