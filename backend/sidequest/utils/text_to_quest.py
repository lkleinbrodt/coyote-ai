"""
Point is to take a file with just the text for quests
and get an LLM to generate all the relevant metadta for each one
(like category, estimated time, etc)
and put it into a json format
and write to a file
this will make it trivial to ingest into the database when ready
"""

import os
from backend.config import Config
import json
import hashlib
import logging
import sys
from backend.sidequest.models import QuestTemplate
from backend.extensions import db
from app import deploy_app

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

INPUT_TEXT_PATH = Config.BACKEND_DIR / "sidequest" / "quests.txt"
OUTPUT_QUEST_PATH = Config.BACKEND_DIR / "sidequest" / "quests.json"


def generate_quest_data():
    quests = []
    with open(INPUT_TEXT_PATH, "r") as f:
        for line in f:
            quests.append(line.strip())

    from backend.src.OpenRouter import OpenRouterClient

    # if output json already exists, load it, otherwise initialize as empty
    if os.path.exists(OUTPUT_QUEST_PATH):
        with open(OUTPUT_QUEST_PATH, "r") as f:
            quest_datas = json.load(f)
    else:
        logger.info(f"Output json does not exist, initializing empty")
        quest_datas = {}

    client = OpenRouterClient()

    for quest in quests:
        quest_hash = hashlib.sha256(quest.encode()).hexdigest()
        if quest_hash in quest_datas:
            logger.info(f"Quest {quest_hash} already exists, skipping")
            if quest_datas[quest_hash].get("text") is None:
                quest_datas[quest_hash]["text"] = quest
            continue
        logger.info(f"Processing quest {quest_hash}")
        ###
        prompt = f"""
        You are part of a data ingestion chain and your job is to create a json object that contains metadta about a given prompt.
        The Json 
        {{
            "category": "fitness|social|mindfulness|chores|hobbies|outdoors|learning|creativity",
            "estimated_time": "X-Y minutes",
            "difficulty": "easy|medium|hard",
            "ambitious": true|false,
            "tags": ["tag1", "tag2", "tag3"]
        ]
        }}
        
        Here are some examples:
        "text": "Do 100 push-ups throughout the day",
        {{
            "category": "fitness",
            "estimated_time": "20 minutes",
            "difficulty": "hard",
            "tags": ["exercise", "energy", "fitness"],
        }},
        text: "Take 5 deep breaths and notice how your body feels",
        {{
            "category": "mindfulness",
            "estimated_time": "2 minutes",
            "difficulty": "easy",
            "tags": ["breathing", "awareness", "calm"],
        }},
        text: "Look out the window and observe 3 things you've never noticed before",
        {{
            "category": "mindfulness",
            "estimated_time": "3 minutes",
            "difficulty": "easy",
            "tags": ["observation", "awareness", "curiosity"],
        }},
        Your response must be valid json. The category must be one of the established categories: fitness, social, mindfulness, chores, hobbies, outdoors, learning, creativity.
        No restriction on tags, they can be anything.
        
        Here is the prompt for you to describe:
        {quest}
        """
        content = client.chat(
            messages=[
                {
                    "role": "system",
                    "content": "You are a prompt describer that takes in some text and outputs relevant metadata.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        try:
            quest_data = json.loads(content)
            logger.info(f"Quest {quest_hash} data: {quest_data}")
        except json.JSONDecodeError:
            print(f"Error parsing JSON response: {content}")
            print(f"Raw response: {content}")
            raise

        # hash the quest
        quest_data["text"] = quest
        quest_datas[quest_hash] = quest_data

    with open(OUTPUT_QUEST_PATH, "w") as f:
        json.dump(quest_datas, f)

    return quest_datas


def ingest_quests_to_db(quest_datas):

    for quest_hash, quest_data in quest_datas.items():
        if db.session.query(QuestTemplate).filter_by(text=quest_data["text"]).first():
            logger.info(f"Quest {quest_hash} already exists, skipping")
            continue
        logger.info(f"Ingesting quest {quest_hash}")
        try:
            quest = QuestTemplate(
                text=quest_data["text"],
                category=quest_data["category"],
                estimated_time=quest_data["estimated_time"],
                difficulty=quest_data["difficulty"],
                tags=quest_data["tags"],
            )
            db.session.add(quest)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error ingesting quest {quest_hash}: {e}")
            continue
        logger.info(f"Ingested quest {quest_hash}")


def main():
    quest_datas = generate_quest_data()
    ingest_quests_to_db(quest_datas)


if __name__ == "__main__":
    app = deploy_app()
    with app.app_context():
        main()
