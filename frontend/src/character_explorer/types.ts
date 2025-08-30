export interface Book {
  id: number;
  title: string;
  author: string;
  total_characters: number;
}

export interface Character {
  id: number;
  name: string;
  total_quotes: number;
  book: Book;
}

export interface Quote {
  id: number;
  text: string;
  context: string | null;
  word_count: number;
  page_number: number | null;
}

export interface SimilarCharacter {
  character: Character;
  similarity_score: number;
}
