import os
import hashlib
from pathlib import Path
from flask import Blueprint, Response, jsonify, request, send_file, abort
from backend.extensions import create_logger
from backend.touchstone_calendar.src import generate_ics, OUTPUT_ICS  # OUTPUT_ICS: Path

logger = create_logger(__name__, level="DEBUG")

touchstone_calendar = Blueprint(
    "touchstone_calendar", __name__, url_prefix="/touchstone_calendar"
)

REBUILD_TOKEN = os.getenv("TOUCHSTONE_TOKEN")


def _file_etag(p: Path) -> str:
    # Strong ETag; fine for a single ~100KB ICS
    h = hashlib.md5()  # nosec - not for security, just cache key
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _serve_ics(p: Path) -> Response:
    if not p.exists():
        abort(404)
    resp = send_file(
        p,
        mimetype="text/calendar",
        as_attachment=False,
        download_name="touchstone.ics",
        conditional=True,  # enables Last-Modified / If-Modified-Since
    )
    # Add strong ETag (some clients prefer it)
    try:
        resp.set_etag(_file_etag(p))
    except Exception as e:
        logger.warning("Failed to compute ETag: %s", e)
    # Encourage clients to revalidate
    resp.headers["Cache-Control"] = "no-cache, must-revalidate"
    # Be explicit on charset
    resp.headers["Content-Type"] = "text/calendar; charset=utf-8"
    # Inline filename hint
    resp.headers["Content-Disposition"] = 'inline; filename="touchstone.ics"'
    return resp


# Stable, pretty URL for subscriptions:
@touchstone_calendar.route("/touchstone.ics", methods=["GET"])
def ics_direct():
    # Lazy-generate on first request (optional)
    if not OUTPUT_ICS.exists():
        try:
            generate_ics()  # make sure this is atomic (temp file + rename) inside the function
        except Exception as e:
            logger.exception("Initial generate failed")
            # Provide more specific error information
            error_msg = "Calendar not available yet"
            if "Playwright" in str(e) or "Chromium" in str(e):
                error_msg = "Calendar generation failed due to browser dependencies. This may be a containerized environment issue."
            abort(503, description=error_msg)
    return _serve_ics(OUTPUT_ICS)


# Secured rebuild webhook (used by your cron/job)
@touchstone_calendar.route("/rebuild", methods=["POST"])
def rebuild():
    token = request.headers.get("X-Token")
    if not token:
        try:
            json_data = request.get_json()
            if json_data:
                token = json_data.get("token")
        except Exception:
            pass  # Ignore JSON parsing errors

    if not REBUILD_TOKEN or token != REBUILD_TOKEN:
        # 403 is fine for token mismatch
        return jsonify({"error": "Forbidden"}), 403

    # Check for force discovery refresh
    force_discovery = request.args.get("refresh") == "discovery"
    if not force_discovery:
        try:
            json_data = request.get_json()
            if json_data:
                force_discovery = json_data.get("refresh") == "discovery"
        except Exception:
            pass  # Ignore JSON parsing errors

    try:
        if force_discovery:
            # Run the daily step now
            from backend.touchstone_calendar.src import refresh_discovery

            refresh_discovery()
            logger.info("Discovery refreshed via webhook")

        generate_ics()  # ensure atomic write inside
        return (
            jsonify({"message": "ICS rebuilt", "discovery_refreshed": force_discovery}),
            200,
        )
    except Exception as e:
        logger.exception("Rebuild failed")
        error_msg = "Rebuild failed"
        if "Playwright" in str(e) or "Chromium" in str(e):
            error_msg = "Rebuild failed due to browser dependencies. This may be a containerized environment issue."
        return jsonify({"error": error_msg}), 500
