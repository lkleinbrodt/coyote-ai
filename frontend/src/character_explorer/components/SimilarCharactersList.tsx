import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Character, SimilarCharacter } from "../types";

import { Badge } from "@/components/ui/badge";
import React from "react";
import { Skeleton } from "@/components/ui/skeleton";

interface SimilarCharactersProps {
  mainCharacter: Character;
  similarChars: SimilarCharacter[];
  onCharacterSelect: (character: Character) => void;
  loading: boolean;
}

export const SimilarCharactersList: React.FC<SimilarCharactersProps> = ({
  mainCharacter,
  similarChars,
  onCharacterSelect,
  loading,
}) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </CardHeader>
        <CardContent className="space-y-4">
          {[...Array(10)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Characters Similar to {mainCharacter.name}</CardTitle>
        <CardDescription>Based on their speech patterns</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {similarChars.map(({ character, similarity_score }) => (
            <li
              key={character.id}
              className="flex items-center justify-between p-3 rounded-md hover:bg-accent transition-colors cursor-pointer"
              onClick={() => onCharacterSelect(character)}
            >
              <div>
                <p className="font-semibold">{character.name}</p>
                <p className="text-sm text-muted-foreground">
                  {character.book.title}
                </p>
              </div>
              <Badge variant="secondary" className="font-mono">
                {similarity_score.toFixed(3)}
              </Badge>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
};
