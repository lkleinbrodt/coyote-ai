import os
import json
import numpy as np
import openai
from lyricsgenius import Genius
from openai import OpenAI
from lyrica.VectorDB import Dictbased_VectorDB
from server.config import create_logger
from dotenv import load_dotenv
from functools import lru_cache
from lyrica.models import Artist, Song, Lyric
from server import db

load_dotenv()

logger = create_logger(__name__, level="DEBUG")

genius = Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]

openai.api_key = os.getenv("OPENAI_API_KEY")
ai_client = OpenAI()

# def load_artist(artist_id):
#     path = f"./data/{artist_id}.json"
#     if not os.path.exists(path):
#         os.makedirs(os.path.dirname(path), exist_ok=True)
#         with open(path, "w") as f:
#             json.dump({}, f)
#     with open(path, "r") as f:
#         data = json.load(f)
#     return data


# def save_artist(artist_id, data):
#     path = f"./data/{artist_id}.json"
#     with open(path, "w") as f:
#         json.dump(data, f)


def name_to_id(artist_name: str) -> str:
    results = genius.search_artists(artist_name)
    top_result = results["sections"][0]

    if len(top_result["hits"]) == 0:
        logger.error(f"Could not find artist: {artist_name}")
        logger.error(top_result)
        raise ValueError(f"Could not find artist: {artist_name}")

    artist_id = top_result["hits"][0]["result"]["id"]

    return str(artist_id)


def get_song_lyrics(song_url=None, song_id=None):
    logger.info(f"getting song lyrics for: {song_id}: {song_url}")
    if song_url:
        return genius.lyrics(song_url=song_url)
    elif song_id:
        return genius.lyrics(song_id=song_id)
    else:
        raise ValueError("Either song_url or song_id must be provided")


def lyrics_to_bars(lyrics):
    bars = lyrics.split("\n\n")

    bar_chunks = []
    for bar in bars:
        if len(bar.split("\n")) > 10:
            chunks = bar.split("\n")
            while chunks:
                # pop off the first 10 lines
                bar_chunks.append("\n".join(chunks[:10]))
                chunks = chunks[10:]
        else:
            bar_chunks.append(bar.strip())
    return bar_chunks


@lru_cache(maxsize=128)
def get_artist_songs(artist_id, max_songs=25):
    logger.info("Getting songs for artist")
    page = 1
    songs = []

    while (page is not None) & (len(songs) < max_songs):
        logger.info(f"Getting page {page} of songs for {artist_id}")
        request = genius.artist_songs(
            artist_id, sort="popularity", per_page=25, page=page
        )
        new_songs = request["songs"]
        rel_songs = [
            song for song in new_songs if str(song["primary_artist"]["id"]) == artist_id
        ]

        songs += rel_songs

        page = request["next_page"]

    return songs


class ArtistClient:
    def __init__(self, artist_id=None, artist_name=None):

        self.genius = genius

        if artist_id is not None:
            self.artist_id = artist_id
        elif artist_name is not None:
            try:
                self.artist_id = name_to_id(artist_name)
            except ValueError as e:
                logger.exception(e)
                raise ValueError("Could not find artist")
        else:
            raise ValueError("Either artist_id or artist_name must be provided")

        self.artist = Artist.query.get(self.artist_id)

        if self.artist is None:
            logger.info(f"Creating artist {self.artist_id}")
            try:
                genius_artist = genius.artist(artist_id=self.artist_id)["artist"]
            except:
                raise ValueError(f"Could not find artist: {artist_id}")
            self.artist = Artist(
                id=self.artist_id,
                name=genius_artist["name"],
                url=genius_artist["url"],
            )

            db.session.add(self.artist)
            db.session.commit()

        self.vdb = self.create_vbd()

    def create_vbd(self):
        embedding_dict = {}
        metadata = {}
        for song in self.artist.songs:

            lyrics = song.lyrics

            for lyric in lyrics:
                embedding_dict[lyric.id] = lyric.get_embedding()
                metadata[lyric.id] = {
                    "song_name": song.title,
                    "song_url": song.url,
                    "text": lyric.lyric,
                }

        db = Dictbased_VectorDB(embedding_dict, metadata)

        self.vdb = db

        return db

    def get_top_lyrics(self):

        return self.vdb.get_top_lyrics()

    def get_songs(self, max_songs=50, pull_lyrics=False):

        songs = get_artist_songs(self.artist_id, max_songs=max_songs)

        for song in songs:
            self.add_song(song, pull_lyrics=pull_lyrics)

        return True

    def add_song(self, song, pull_lyrics=False):
        if Song.query.get(song["id"]) is None:

            new_song = Song(
                id=song["id"],
                title=song["title"],
                url=song["url"],
                artist=self.artist,
            )

            db.session.add(new_song)
            db.session.commit()

            if pull_lyrics:
                self.get_lyrics(song["id"])

            return new_song

        return True

    def get_lyrics(self, song_id, overwrite=False):

        song = Song.query.get(song_id)
        if song is not None:
            existing_lyrics = Song.query.get(song_id).lyrics
            if len(existing_lyrics) > 0:
                if overwrite:
                    song = Song.query.get(song_id)
                else:
                    return
        else:
            song = self.add_song(song_id, pull_lyrics=False)

        lyrics = get_song_lyrics(song_id=song_id)

        lyrics = lyrics_to_bars(lyrics)

        db_lyrics = []
        for i, bar in enumerate(lyrics):

            response = ai_client.embeddings.create(
                input=bar, model="text-embedding-3-small"
            )

            embedding = np.array(response.data[0].embedding)

            logger.debug(
                f"""Embedding for {bar}: 
                         mean: {np.mean(embedding)},
                         std: {np.std(embedding)},
                         median: {np.median(embedding)},
                         """
            )

            db_lyric = Lyric(lyric=bar, order=i, song=song)
            db_lyric.add_embedding(embedding)
            db_lyrics.append(db_lyric)

            assert len(embedding) == 1536

            self.vdb.add_item(
                db_lyric.id,
                embedding,
                {
                    "song_name": song.title,
                    "song_url": song.url,
                    "text": bar,
                },
            )

        logger.debug(f"Pulled {len(db_lyrics)} lyrics for {song.title}")

        db.session.add_all(db_lyrics)
        db.session.commit()
