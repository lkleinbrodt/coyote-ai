from flask import jsonify, Blueprint, request, Response, stream_with_context
from server.config import create_logger
from lyrica import src
from flask_cors import CORS, cross_origin
import json

logger = create_logger(__name__, level="DEBUG")

lyrica = Blueprint("lyrica", __name__, url_prefix="/lyrica")


@lyrica.route("/")
def home():
    logger.debug("Home route accessed")
    return jsonify({"message": "Hello from Lyrica Flask!"})


@lyrica.route("get-top-lyrics", methods=["POST"])
def get_top_lyrics():
    artist_name = request.json.get("artist")
    artist_id = src.get_artist_id(artist_name)
    artist_songs = src.get_artist_songs(artist_id, max_songs=50)

    artist_data = src.load_artist(artist_id)

    def yield_lyrics(artist_songs):
        top_lyrics = []
        for song in artist_songs:
            song_id = str(song["id"])
            if song_id not in artist_data:
                song_info = {"title": song["title"], "url": song["url"]}

                logger.info(f'pulling song info for {song["title"]}')

                lyrics = src.get_song_lyrics(song_url=song["url"])
                bars = lyrics.split("\n\n")
                base_id = str(song_id)
                bar_info = {}
                for i, bar in enumerate(bars):
                    response = src.ai_client.embeddings.create(
                        input=bar, model="text-embedding-ada-002"
                    )
                    bar_info[int(base_id + str(i))] = {
                        "text": bar,
                        "embedding": response.data[0].embedding,
                    }

                song_info["lyrics"] = bar_info
                artist_data[song_id] = song_info

                src.save_artist(artist_id, artist_data)

            if len(artist_data) >= 2:
                top_lyrics = src.get_top_lyric(artist_id)
            out = json.dumps({"n_songs": len(artist_data), "lyrics": top_lyrics})
            yield out
        logger.info("done finding top lyrics")

    return Response(stream_with_context(yield_lyrics(artist_songs)))
