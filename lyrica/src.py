import os
import json
import openai
from lyricsgenius import Genius
from openai import OpenAI
from lyrica.VectorDB import Dictbased_VectorDB

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
ai_client = OpenAI()

genius = Genius(os.getenv("GENIUS_ACCESS_TOKEN"))
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]

# TODO: persist


def load_data():
    if not os.path.exists("data.json"):
        with open("data.json", "w") as f:
            json.dump({}, f)
    with open("data.json", "r") as f:
        data = json.load(f)

    return data


def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f)


def query_artist(artist_name, max_songs):
    artist = genius.search_artist(
        artist_name="Chance the Rapper",
        max_songs=10,
        sort="popularity",
        get_full_info=False,
        include_features=False,
    )

    return artist


def pull_artist_lyrics(artist_name, max_songs):
    artist = query_artist(artist_name, max_songs)
    data = load_data()
    songs = data.get(artist.name, {})

    for song in artist.songs:
        if song.id not in songs:
            song_info = {"title": song.title, "url": song.url}

            lyrics = song.lyrics

            bars = lyrics.split("\n\n")
            base_id = str(song.id)
            bar_info = {}
            for i, bar in enumerate(bars):
                response = ai_client.embeddings.create(
                    input=bar, model="text-embedding-ada-002"
                )
                bar_info[int(base_id + str(i))] = {
                    "text": bar,
                    "embedding": response.data[0].embedding,
                }

            song_info["lyrics"] = bar_info
            songs[song.id] = song_info

    data[artist.name] = songs

    save_data(data)


def load_artist_lyrics(artist_name):
    data = load_data()
    embedding_dict = {}
    lyrics_dict = {}
    for song in data.get(artist_name, {}).values():
        for bar_id, bar_info in song["lyrics"].items():
            embedding_dict[bar_id] = bar_info["embedding"]
            lyrics_dict[bar_id] = bar_info["text"]

    return embedding_dict, lyrics_dict


def load_artist_db(artist_name):
    embedding_dict, lyrics_dict = load_artist_lyrics(artist_name)
    db = Dictbased_VectorDB(embedding_dict, lyrics_dict)
    return db
