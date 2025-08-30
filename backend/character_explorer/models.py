from backend.extensions import db
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB

class Book(db.Model):
    __tablename__ = 'books'
    __table_args__ = {'schema': 'character_explorer'}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    processed_at = db.Column(db.DateTime, default=db.func.now())
    total_characters = db.Column(db.Integer, default=0)

    characters = db.relationship('Character', backref='book', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'total_characters': self.total_characters
        }

class Character(db.Model):
    __tablename__ = 'characters'
    __table_args__ = (
        db.UniqueConstraint('book_id', 'name', name='uq_character_book_name'),
        {'schema': 'character_explorer'}
    )

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('character_explorer.books.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    total_quotes = db.Column(db.Integer, default=0)
    embedding = db.Column(Vector(384))
    created_at = db.Column(db.DateTime, default=db.func.now())

    quotes = db.relationship('Quote', backref='character', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'total_quotes': self.total_quotes,
            'book': {
                'id': self.book.id,
                'title': self.book.title,
                'author': self.book.author
            }
        }

class Quote(db.Model):
    __tablename__ = 'quotes'
    __table_args__ = {'schema': 'character_explorer'}

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character_explorer.characters.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    embedding = db.Column(Vector(384))
    context = db.Column(db.Text)
    page_number = db.Column(db.Integer)
    word_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'context': self.context,
            'word_count': self.word_count,
            'page_number': self.page_number
        }

class CharacterSimilarity(db.Model):
    __tablename__ = 'character_similarities'
    __table_args__ = (
        db.UniqueConstraint('character_id', 'similar_character_id', name='uq_similarity_pair'),
        {'schema': 'character_explorer'}
    )

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('character_explorer.characters.id'), nullable=False)
    similar_character_id = db.Column(db.Integer, db.ForeignKey('character_explorer.characters.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    calculated_at = db.Column(db.DateTime, default=db.func.now()) 