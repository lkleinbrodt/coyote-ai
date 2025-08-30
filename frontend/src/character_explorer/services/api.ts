import { Character, Quote, SimilarCharacter } from "../types";

import axiosInstance from "@/utils/axiosInstance";

const API_BASE = "/character-explorer";

export const characterExplorerApi = {
  searchCharacters: async (query: string): Promise<Character[]> => {
    const params = new URLSearchParams({ q: query });
    const response = await axiosInstance.get(`${API_BASE}/search?${params}`);
    return response.data;
  },

  getRandomCharacter: async (): Promise<Character> => {
    const response = await axiosInstance.get(`${API_BASE}/random`);
    return response.data;
  },

  getSimilarCharacters: async (
    characterId: number,
    limit = 10
  ): Promise<SimilarCharacter[]> => {
    const response = await axiosInstance.get(
      `${API_BASE}/${characterId}/similar?limit=${limit}`
    );
    return response.data;
  },

  getCharacterQuotes: async (
    characterId: number,
    limit = 5
  ): Promise<Quote[]> => {
    const response = await axiosInstance.get(
      `${API_BASE}/${characterId}/quotes?limit=${limit}`
    );
    return response.data;
  },
};
