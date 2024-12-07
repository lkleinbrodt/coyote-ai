import sqlalchemy as sa
from sqlalchemy.orm import relationship
from backend import db
import numpy as np


class Artist(db.Model):
    __tablename__ = "artists"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(128), unique=True, nullable=False)
    songs = relationship("Song", backref="artist", lazy=True)
    url = sa.Column(sa.String(128), nullable=True)

    def __repr__(self):
        return f"<Artist: {self.name}>"


class Song(db.Model):
    __tablename__ = "songs"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(128), nullable=False)
    url = sa.Column(sa.String(128), nullable=False)
    artist_id = sa.Column(
        sa.Integer, sa.ForeignKey("artists.id"), nullable=False, name="artist_id"
    )

    lyrics = relationship("Lyric", backref="song", lazy=True)

    def __repr__(self):
        return f"<Song: {self.title}>"


class Lyric(db.Model):
    __tablename__ = "lyrics"

    id = sa.Column(sa.Integer, primary_key=True)
    lyric = sa.Column(sa.String(128), nullable=False)
    order = sa.Column(sa.Integer, nullable=False)
    song_id = sa.Column(
        sa.Integer, sa.ForeignKey("songs.id"), nullable=False, name="song_id"
    )
    embeddings = sa.Column(sa.LargeBinary, nullable=True)

    def add_embedding(self, embedding: np.ndarray):
        self.embeddings = embedding.tobytes()

    def get_embedding(self) -> np.ndarray:
        return np.frombuffer(self.embeddings, dtype=np.float64)

    def __repr__(self):
        return f"<Lyric: {self.lyric}>"
