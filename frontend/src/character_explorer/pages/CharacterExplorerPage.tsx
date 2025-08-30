import { Character, Quote, SimilarCharacter } from "../types";
import React, { useCallback, useState } from "react";

import { CharacterQuotes } from "../components/CharacterQuotes";
import { CharacterSearch } from "../components/CharacterSearch";
import { SimilarCharactersList } from "../components/SimilarCharactersList";
import { characterExplorerApi } from "../services/api";

const CharacterExplorerPage: React.FC = () => {
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(
    null
  );
  const [similarCharacters, setSimilarCharacters] = useState<
    SimilarCharacter[]
  >([]);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(false);

  const handleCharacterSelect = useCallback(async (character: Character) => {
    if (!character) return;

    setLoading(true);
    setSelectedCharacter(character);
    setSimilarCharacters([]);
    setQuotes([]);

    try {
      const [similarRes, quotesRes] = await Promise.all([
        characterExplorerApi.getSimilarCharacters(character.id),
        characterExplorerApi.getCharacterQuotes(character.id, 5),
      ]);

      setSimilarCharacters(similarRes);
      setQuotes(quotesRes);
    } catch (error) {
      console.error("Error fetching character data:", error);
      // Optionally, show a toast notification to the user
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="container mx-auto p-4 md:p-8 space-y-8">
      <header className="text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-gray-100">
          Character Similarity Explorer
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          Discover fictional characters who speak like your favorites.
        </p>
      </header>

      <div className="max-w-2xl mx-auto">
        <CharacterSearch
          onCharacterSelect={handleCharacterSelect}
          disabled={loading}
        />
      </div>

      {selectedCharacter && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8 animate-fade-in">
          <div>
            <SimilarCharactersList
              mainCharacter={selectedCharacter}
              similarChars={similarCharacters}
              onCharacterSelect={handleCharacterSelect}
              loading={loading}
            />
          </div>
          <div>
            <CharacterQuotes
              character={selectedCharacter}
              quotes={quotes}
              loading={loading}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default CharacterExplorerPage;
