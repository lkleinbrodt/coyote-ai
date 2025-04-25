import json
import time

from flask import Blueprint, Response, jsonify, request, stream_with_context

from backend.extensions import create_logger
from backend.lyrica import ArtistClient

logger = create_logger(__name__, level="DEBUG")

lyrica = Blueprint("lyrica", __name__, url_prefix="/lyrica")


@lyrica.route("/search-artist/<artist_name>", methods=["GET"])
def search_artist(artist_name: str):
    logger.info(f"Searching for artist: {artist_name}")

    try:
        artist_id = ArtistClient.name_to_id(artist_name)
        logger.debug(f"Found artist ID: {artist_id} for artist: {artist_name}")
    except ValueError as e:
        logger.error(f"Artist not found: {artist_name}", exc_info=True)
        return jsonify({"error": "Artist not found"}), 404

    try:
        artist = ArtistClient.ArtistClient(artist_id=artist_id)
        logger.debug(f"Successfully created ArtistClient for ID: {artist_id}")
    except Exception as e:
        logger.error(f"Error creating ArtistClient: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to create artist client"}), 500

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
