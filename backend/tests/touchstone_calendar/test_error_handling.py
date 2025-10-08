"""
Basic tests for error handling.
"""

import pytest
from flask.testing import FlaskClient
from unittest.mock import patch


class TestErrorHandling:
    """Basic tests for error handling."""

    def test_missing_file_returns_404(self, client: FlaskClient):
        """Test that missing file returns 404."""
        with patch("backend.touchstone_calendar.routes.OUTPUT_ICS") as mock_path:
            mock_path.exists.return_value = True
            mock_path.__str__ = lambda x: "/nonexistent/file.ics"

            # Mock send_file to raise 404
            with patch(
                "backend.touchstone_calendar.routes.send_file"
            ) as mock_send_file:
                from werkzeug.exceptions import NotFound

                mock_send_file.side_effect = NotFound()

                response = client.get("/api/touchstone.ics")
                assert response.status_code == 404

    def test_generation_failure_returns_500(self, client: FlaskClient):
        """Test that generation failure returns 500 (caught by global error handler)."""
        with patch("backend.touchstone_calendar.routes.OUTPUT_ICS") as mock_path:
            mock_path.exists.return_value = False
            mock_path.__str__ = lambda x: "/tmp/nonexistent.ics"

            with patch(
                "backend.touchstone_calendar.routes.generate_ics"
            ) as mock_generate:
                mock_generate.side_effect = Exception("Generation failed")

                response = client.get("/api/touchstone.ics")
                assert response.status_code == 500

    def test_rebuild_without_token_returns_403(self, client: FlaskClient):
        """Test rebuild without token returns 403."""
        response = client.post("/api/touchstone_calendar/rebuild")
        assert response.status_code == 403

    def test_rebuild_with_invalid_token_returns_403(self, client: FlaskClient):
        """Test rebuild with invalid token returns 403."""
        with patch.dict("os.environ", {"TOUCHSTONE_TOKEN": "valid-token"}):
            response = client.post(
                "/api/touchstone_calendar/rebuild", headers={"X-Token": "invalid-token"}
            )
            assert response.status_code == 403
