from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from .models import Book, Character
from .services.character_service import CharacterService

character_explorer_bp = Blueprint(
    "character_explorer", __name__, url_prefix="/character-explorer"
)


@character_explorer_bp.route("/search", methods=["GET"])
@jwt_required()
def search_characters():
    """Search characters by name"""
    query = request.args.get("q", "").strip()
    # book_id = request.args.get('book_id', type=int)  # For future cross-book filtering

    characters = CharacterService.search_by_name(query, book_id=None)
    return jsonify([char.to_dict() for char in characters])


@character_explorer_bp.route("/random", methods=["GET"])
@jwt_required()
def random_character():
    """Get a random character"""
    # book_id = request.args.get('book_id', type=int)
    character = CharacterService.get_random_character(book_id=None)
    return jsonify(character.to_dict() if character else None)


@character_explorer_bp.route("/<int:character_id>/similar", methods=["GET"])
@jwt_required()
def get_similar_characters(character_id):
    """Get top 10 similar characters"""
    limit = request.args.get("limit", 10, type=int)
    similar = CharacterService.find_similar_characters(character_id, limit)

    return jsonify(
        [
            {"character": char.to_dict(), "similarity_score": score}
            for char, score in similar
        ]
    )


@character_explorer_bp.route("/<int:character_id>/quotes", methods=["GET"])
@jwt_required()
def get_character_quotes(character_id):
    """Get representative quotes for a character"""
    limit = request.args.get("limit", 5, type=int)
    quotes = CharacterService.get_representative_quotes(character_id, limit)
    return jsonify([quote.to_dict() for quote in quotes])


@character_explorer_bp.route("/books", methods=["GET"])
@jwt_required()
def get_books():
    """Get a list of all processed books"""
    books = Book.query.order_by(Book.title).all()
    return jsonify([book.to_dict() for book in books])
