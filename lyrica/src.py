import os
import json
import openai
from lyricsgenius import Genius
from openai import OpenAI
from lyrica.VectorDB import Dictbased_VectorDB
from server.config import create_logger

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
ai_client = OpenAI()

genius = Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]

logger = create_logger(__name__, level="DEBUG")


def load_artist(artist_id):
    path = f"./data/{artist_id}.json"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        data = json.load(f)
    return data


def save_artist(artist_id, data):
    path = f"./data/{artist_id}.json"
    with open(path, "w") as f:
        json.dump(data, f)


def query_artist(artist_name, max_songs):
    artist = genius.search_artist(
        artist_name=artist_name,
        max_songs=max_songs,
        sort="popularity",
        get_full_info=False,
        include_features=False,
    )

    return artist


def load_artist_lyrics(artist_id):
    artist_data = load_artist(artist_id)

    embedding_dict = {}
    lyrics_dict = {}
    for song in artist_data.values():
        for bar_id, bar_info in song["lyrics"].items():
            embedding_dict[bar_id] = bar_info["embedding"]
            lyrics_dict[bar_id] = bar_info["text"]

    return embedding_dict, lyrics_dict


def load_artist_db(artist_id):
    embedding_dict, lyrics_dict = load_artist_lyrics(artist_id)
    db = Dictbased_VectorDB(embedding_dict, lyrics_dict)
    return db


def get_top_lyric(artist_id):
    db = load_artist_db(artist_id)
    if len(db) == 0:
        print("No lyrics found")
        return None

    return db.get_top_lyrics()


def get_artist_id(artist_name):
    results = genius.search_artists(artist_name)
    top_result = results["sections"][0]
    artist_id = top_result["hits"][0]["result"]["id"]
    return artist_id


def get_artist_songs(artist_id, max_songs=50):

    page = 1
    songs = []

    while (page is not None) & (len(songs) < max_songs):
        request = genius.artist_songs(
            artist_id, sort="popularity", per_page=50, page=page
        )
        new_songs = request["songs"]
        rel_songs = [
            song for song in new_songs if song["primary_artist"]["id"] == artist_id
        ]

        songs += rel_songs

        page = request["next_page"]
        logger.debug(f"Page: {page}")
        logger.debug(f"Total songs: {len(songs)}")

    return songs


def get_song_lyrics(song_url=None, song_id=None):
    # give either song_url or song_id but not both
    if song_url:
        return genius.lyrics(song_url=song_url)
    elif song_id:
        return genius.lyrics(song_id=song_id)
    else:
        raise ValueError("Either song_url or song_id must be provided")
