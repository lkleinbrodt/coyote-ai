from sqlalchemy.sql.expression import func

from backend.extensions import db

from ..models import Book, Character, Quote


class CharacterService:
    @staticmethod
    def search_by_name(query: str, book_id: int = None):
        search_query = Character.query
        if book_id:
            search_query = search_query.filter(Character.book_id == book_id)

        if query:
            search_query = search_query.filter(Character.name.ilike(f"%{query}%"))

        return search_query.order_by(Character.name).limit(20).all()

    @staticmethod
    def get_random_character(book_id: int = None):
        query = Character.query
        if book_id:
            query = query.filter(Character.book_id == book_id)
        return query.order_by(func.random()).first()

    @staticmethod
    def find_similar_characters(character_id: int, limit: int = 10):
        target_character = Character.query.get(character_id)
        if not target_character or target_character.embedding is None:
            return []

        # Use the l2_distance operator for similarity (lower is better)
        # For cosine similarity, use <=>
        # For max inner product, use <#>
        similar_characters = (
            db.session.query(
                Character,
                Character.embedding.l2_distance(target_character.embedding).label(
                    "distance"
                ),
            )
            .filter(Character.id != character_id)
            .order_by("distance")
            .limit(limit)
            .all()
        )

        # The query returns tuples of (Character, distance)
        results = []
        for char, distance in similar_characters:
            # We convert distance to a similarity score (0-1, higher is better)
            # This is a simple inversion, more complex formulas could be used.
            similarity_score = 1 / (1 + distance)
            results.append((char, similarity_score))

        return results

    @staticmethod
    def get_representative_quotes(character_id: int, limit: int = 5):
        """
        Gets quotes that are closest to the character's central embedding.
        These are the most 'on-brand' quotes for the character.
        """
        character = Character.query.get(character_id)
        if not character:
            return []

        quotes = (
            db.session.query(Quote)
            .filter(Quote.character_id == character_id)
            .order_by(Quote.embedding.l2_distance(character.embedding))
            .limit(limit)
            .all()
        )
        return quotes
