from flask import jsonify, Blueprint, request, Response, stream_with_context
from backend.config import create_logger
from backend.lyrica import ArtistClient
import json
import time

logger = create_logger(__name__, level="DEBUG")

lyrica = Blueprint("lyrica", __name__, url_prefix="/lyrica")


@lyrica.route("/search-artist/<artist_name>", methods=["GET"])
def search_artist(artist_name: str):

    try:
        artist_id = ArtistClient.name_to_id(artist_name)
    except ValueError as e:
        logger.exception(e)
        return jsonify({"error": "Artist not found"}), 404

    artist = ArtistClient.ArtistClient(artist_id=artist_id)
    return jsonify({"id": artist.artist_id, "name": artist.artist.name}), 200


@lyrica.route("get-top-lyrics", methods=["POST"])
def get_top_lyrics():
    artist_id = request.json.get("artist_id")

    try:
        artist = ArtistClient.ArtistClient(artist_id=artist_id)
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Error pulling artist info"}), 500

    N_SONG_TARGET = 10

    def yield_lyrics():
        top_lyrics = artist.get_top_lyrics()
        if top_lyrics is None:
            top_lyrics = []

        # find the number of songs related to this artist that have lyridcs
        # artist is related to songs which is related to lyrics

        n_songs_with_lyrics = len(
            [song for song in artist.artist.songs if len(song.lyrics) > 0]
        )

        out = json.dumps(
            {
                "n_songs": n_songs_with_lyrics,
                "artist": artist.artist.name,
                "top_lyrics": top_lyrics,
            }
        )

        yield out

        if len(artist.artist.songs) < N_SONG_TARGET:
            logger.info(f"Getting more songs for {artist.artist.name}")
            artist.get_songs(N_SONG_TARGET - len(artist.artist.songs))

        for i in range(N_SONG_TARGET):
            song = artist.artist.songs[i]
            if len(song.lyrics) == 0:
                logger.info(f"Getting lyrics for {song.title}")
                artist.get_lyrics(song.id)
                n_songs_with_lyrics += 1

                out = json.dumps(
                    {
                        "n_songs": n_songs_with_lyrics,
                        "artist": artist.artist.name,
                        "top_lyrics": artist.get_top_lyrics(),
                    }
                )

                time.sleep(2)

                yield out

    return Response(stream_with_context(yield_lyrics()))
