import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import React, { useState } from "react";

import { Button } from "@/components/ui/button";
import { Character } from "../types";
import { characterExplorerApi } from "../services/api";

interface CharacterSearchProps {
  onCharacterSelect: (character: Character) => void;
  disabled: boolean;
}

export const CharacterSearch: React.FC<CharacterSearchProps> = ({
  onCharacterSelect,
  disabled,
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Character[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [popoverOpen, setPopoverOpen] = useState(false);

  const handleSearch = async (currentQuery: string) => {
    setQuery(currentQuery);
    if (currentQuery.length < 2) {
      setResults([]);
      return;
    }
    setIsLoading(true);
    try {
      const data = await characterExplorerApi.searchCharacters(currentQuery);
      setResults(data);
    } catch (error) {
      console.error("Failed to search characters:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (character: Character) => {
    setQuery(character.name);
    setPopoverOpen(false);
    onCharacterSelect(character);
  };

  const handleRandom = async () => {
    setIsLoading(true);
    try {
      const randomChar = await characterExplorerApi.getRandomCharacter();
      if (randomChar) {
        onCharacterSelect(randomChar);
      }
    } catch (error) {
      console.error("Failed to get random character", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex gap-4">
      <Popover open={popoverOpen} onOpenChange={setPopoverOpen}>
        <PopoverTrigger asChild>
          <div className="w-full">
            <Command>
              <CommandInput
                placeholder="Search for a character (e.g., Frodo)"
                value={query}
                onValueChange={handleSearch}
                disabled={disabled}
                className="text-lg"
              />
            </Command>
          </div>
        </PopoverTrigger>
        <PopoverContent className="w-[--radix-popover-trigger-width] p-0">
          <CommandList>
            {isLoading && <CommandEmpty>Loading...</CommandEmpty>}
            {!isLoading && results.length === 0 && query.length > 1 && (
              <CommandEmpty>No results found.</CommandEmpty>
            )}
            {results.length > 0 && (
              <CommandGroup>
                {results.map((char) => (
                  <CommandItem
                    key={char.id}
                    onSelect={() => handleSelect(char)}
                    value={char.name}
                  >
                    {char.name} ({char.book.title})
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </PopoverContent>
      </Popover>
      <Button
        onClick={handleRandom}
        disabled={disabled || isLoading}
        className="text-lg"
      >
        I'm Feeling Lucky
      </Button>
    </div>
  );
};
