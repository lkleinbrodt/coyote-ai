interface PetMessage {
  text: string;
  type: "eat" | "idle" | "play";
}

interface PetState {
  happiness: number;
  lastFed: Date;
  messages: string[];
}

// For now, return placeholder messages
const placeholderMessages: Record<string, string[]> = {
  eat: [
    "Yummy!",
    "This is delicious!",
    "More please!",
    "Thank you for the food!",
    "Nom nom nom...",
  ],
  idle: [
    "Pet me!",
    "What should we do today?",
    "I'm happy to see you!",
    "Let's play!",
  ],
  play: ["This is fun!", "I love playing with you!", "Wheee!", "Again, again!"],
};

export const petApi = {
  getMessage: async (type: PetMessage["type"]): Promise<string> => {
    try {
      // TODO: Replace with actual API call
      // const response = await fetch(`/api/pet/message?type=${type}`, {
      //   method: "GET",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      // });
      // if (!response.ok) {
      //   throw new Error(`HTTP error! status: ${response.status}`);
      // }
      // return response.json();

      // For now, return a random placeholder message
      const messages = placeholderMessages[type] || placeholderMessages.idle;
      return messages[Math.floor(Math.random() * messages.length)];
    } catch (error) {
      console.error("Error getting pet message:", error);
      return "...";
    }
  },

  saveState: async (state: Partial<PetState>) => {
    try {
      // TODO: Implement actual API call
      // const response = await fetch("/api/pet/state", {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      //   body: JSON.stringify(state),
      // });
      // if (!response.ok) {
      //   throw new Error(`HTTP error! status: ${response.status}`);
      // }
      console.log("Saving pet state:", state);
    } catch (error) {
      console.error("Error saving pet state:", error);
    }
  },
};

export const getPetMessage = async (
  type: PetMessage["type"]
): Promise<string> => {
  try {
    // TODO: Replace with actual API call
    // const response = await axiosInstance.get(`/message?type=${type}`);
    // return response.data.text;

    // For now, return a random placeholder message
    const messages = placeholderMessages[type] || placeholderMessages.idle;
    return messages[Math.floor(Math.random() * messages.length)];
  } catch (error) {
    console.error("Error getting pet message:", error);
    return "...";
  }
};

// Add more API functions as needed
export const savePetState = async (state: any) => {
  try {
    // TODO: Implement actual API call
    // await axiosInstance.post('/state', state);
    console.log("Saving pet state:", state);
  } catch (error) {
    console.error("Error saving pet state:", error);
  }
};
