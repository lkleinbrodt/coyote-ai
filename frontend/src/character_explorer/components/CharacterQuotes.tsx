import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Character, Quote } from "../types";

import React from "react";
import { Skeleton } from "@/components/ui/skeleton";

interface CharacterQuotesProps {
  character: Character;
  quotes: Quote[];
  loading: boolean;
}

export const CharacterQuotes: React.FC<CharacterQuotesProps> = ({
  character,
  quotes,
  loading,
}) => {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </CardHeader>
        <CardContent className="space-y-6">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Representative Quotes from {character.name}</CardTitle>
        <CardDescription>
          Quotes that are most typical of their speaking style.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {quotes.map((quote) => (
            <blockquote
              key={quote.id}
              className="border-l-4 pl-4 italic text-muted-foreground"
            >
              "{quote.text}"
            </blockquote>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
