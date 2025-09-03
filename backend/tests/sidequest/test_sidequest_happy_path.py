import json
import uuid
from unittest.mock import Mock

from backend.extensions import db
from backend.models import User
from backend.sidequest.models import SideQuestUser, QuestStatus, QuestRating
from backend.sidequest.services import QuestService


def test_anonymous_signin_creates_profile(client):
    device_uuid = str(uuid.uuid4())
    res = client.post(
        "/api/sidequest/auth/anonymous/signin",
        json={"device_uuid": device_uuid},
    )
    assert res.status_code == 200
    user = User.query.filter_by(anon_id=device_uuid).first()
    assert SideQuestUser.query.filter_by(user_id=user.id).first()


def test_preferences_endpoints(client, test_sidequest_user, auth_headers):
    res = client.get("/api/sidequest/me", headers=auth_headers)
    assert res.status_code == 200
    res = client.put(
        "/api/sidequest/me",
        json={"categories": ["social"], "difficulty": "hard"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["preferences"]["categories"] == ["social"]
    res = client.post("/api/sidequest/onboarding/complete", headers=auth_headers)
    assert res.status_code == 200


def test_board_generation_and_completion(app, test_sidequest_user):
    with app.app_context():
        service = QuestService(db.session)
        mock_client = Mock()
        mock_client.chat.return_value = json.dumps(
            {
                "quests": [
                    {
                        "text": "Walk the dog for 5 minutes",
                        "category": "fitness",
                        "estimated_time": "5 minutes",
                        "difficulty": "easy",
                        "tags": ["fitness"],
                    }
                ]
            }
        )
        service.quest_generation_service.client = mock_client
        board = service.refresh_board(test_sidequest_user.user_id)
        print(board.quests.all())
        quest = board.quests.first()
        quest = service.update_quest_status(quest.id, "accepted")
        quest = service.update_quest_status(
            quest.id,
            "completed",
            {
                "feedback": {
                    "rating": QuestRating.THUMBS_UP,
                    "comment": "ok",
                    "time_spent": 5,
                }
            },
        )
        assert quest.status == QuestStatus.COMPLETED
        assert quest.feedback_rating == QuestRating.THUMBS_UP
        assert quest.text == "Walk the dog for 5 minutes"


def test_health_endpoint(client):
    assert client.get("/api/sidequest/health").status_code == 200
