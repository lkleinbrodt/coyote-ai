import json
import random
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openai import OpenAI
from sqlalchemy.orm import Session

from backend.extensions import create_logger

from backend.sidequest.models import (
    QuestCategory,
    QuestDifficulty,
    QuestGenerationLog,
    QuestBoard,
    SideQuest,
    SideQuestUser,
)
from backend.models import User


logger = create_logger(__name__)


class QuestGenerationService:
    """Service for generating personalized quests using LLM or fallback system"""

    def __init__(self, db_session: Session, openai_api_key: str = None):
        self.db = db_session
        from backend.src.OpenRouter import OpenRouterClient

        self.model = "meta-llama/llama-3.3-70b-instruct"

        self.client = OpenRouterClient(
            default_model=self.model,
        )

        # Fallback quest templates for when LLM is unavailable
        self.fallback_quests = self._initialize_fallback_quests()

    def _initialize_fallback_quests(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize curated fallback quests for each category"""
        return {
            "fitness": [
                {
                    "text": "Do 10 jumping jacks and 5 push-ups",
                    "category": "fitness",
                    "estimated_time": "3-5 minutes",
                    "difficulty": "easy",
                    "tags": ["exercise", "quick", "energy"],
                },
                {
                    "text": "Take a 10-minute walk around your neighborhood",
                    "category": "fitness",
                    "estimated_time": "10 minutes",
                    "difficulty": "easy",
                    "tags": ["walking", "outdoors", "fresh air"],
                },
                {
                    "text": "Do a 5-minute stretching routine focusing on your back and shoulders",
                    "category": "fitness",
                    "estimated_time": "5 minutes",
                    "difficulty": "easy",
                    "tags": ["stretching", "flexibility", "wellness"],
                },
            ],
            "social": [
                {
                    "text": "Send a thoughtful message to someone you haven't talked to in a while",
                    "category": "social",
                    "estimated_time": "5 minutes",
                    "difficulty": "easy",
                    "tags": ["connection", "communication", "relationships"],
                },
                {
                    "text": "Compliment a stranger or service worker genuinely",
                    "category": "social",
                    "estimated_time": "2 minutes",
                    "difficulty": "medium",
                    "tags": ["kindness", "social skills", "confidence"],
                },
            ],
            "mindfulness": [
                {
                    "text": "Take 5 deep breaths and notice how your body feels",
                    "category": "mindfulness",
                    "estimated_time": "2 minutes",
                    "difficulty": "easy",
                    "tags": ["breathing", "awareness", "calm"],
                },
                {
                    "text": "Look out the window and observe 3 things you've never noticed before",
                    "category": "mindfulness",
                    "estimated_time": "3 minutes",
                    "difficulty": "easy",
                    "tags": ["observation", "awareness", "curiosity"],
                },
            ],
            "chores": [
                {
                    "text": "Organize one drawer or shelf in your home",
                    "category": "chores",
                    "estimated_time": "10 minutes",
                    "difficulty": "easy",
                    "tags": ["organization", "tidiness", "home"],
                },
                {
                    "text": "Wash 5 dishes or put away 5 items",
                    "category": "chores",
                    "estimated_time": "5 minutes",
                    "difficulty": "easy",
                    "tags": ["cleaning", "maintenance", "responsibility"],
                },
            ],
            "hobbies": [
                {
                    "text": "Draw a simple doodle or sketch for 5 minutes",
                    "category": "hobbies",
                    "estimated_time": "5 minutes",
                    "difficulty": "easy",
                    "tags": ["creativity", "art", "expression"],
                },
                {
                    "text": "Learn one new fact about a topic you're curious about",
                    "category": "hobbies",
                    "estimated_time": "5 minutes",
                    "difficulty": "easy",
                    "tags": ["learning", "curiosity", "knowledge"],
                },
            ],
            "outdoors": [
                {
                    "text": "Step outside and feel the temperature and air for 2 minutes",
                    "category": "outdoors",
                    "estimated_time": "2 minutes",
                    "difficulty": "easy",
                    "tags": ["nature", "awareness", "sensory"],
                },
                {
                    "text": "Find and photograph something beautiful in your immediate surroundings",
                    "category": "outdoors",
                    "estimated_time": "8 minutes",
                    "difficulty": "medium",
                    "tags": ["photography", "beauty", "observation"],
                },
            ],
            "learning": [
                {
                    "text": "Look up the meaning of a word you've heard but don't know",
                    "category": "learning",
                    "estimated_time": "3 minutes",
                    "difficulty": "easy",
                    "tags": ["vocabulary", "knowledge", "curiosity"],
                },
                {
                    "text": "Watch a 5-minute educational video on a topic you're interested in",
                    "category": "learning",
                    "estimated_time": "5 minutes",
                    "difficulty": "easy",
                    "tags": ["education", "video", "learning"],
                },
            ],
            "creativity": [
                {
                    "text": "Write down 3 creative ideas for something you could make or do",
                    "category": "creativity",
                    "estimated_time": "5 minutes",
                    "difficulty": "easy",
                    "tags": ["ideation", "creativity", "planning"],
                },
                {
                    "text": "Rearrange 3 items in your space to create a more pleasing arrangement",
                    "category": "creativity",
                    "estimated_time": "7 minutes",
                    "difficulty": "medium",
                    "tags": ["design", "aesthetics", "space"],
                },
            ],
        }

    def generate_daily_quests(
        self,
        user_id: int,
        preferences: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        add_to_board: bool = True,
    ) -> List[SideQuest]:
        """Generate 3 personalized daily quests for a user"""
        start_time = time.time()
        fallback_used = False
        model_used = None
        tokens_used = None

        try:
            # Try LLM generation first
            quests = self._generate_with_llm(preferences, context)
            model_used = self.model
            fallback_used = False

            if quests:
                logger.info(
                    f"Successfully generated {len(quests)} quests using LLM for user {user_id}"
                )
            else:
                raise Exception("LLM generation returned no quests")

        except Exception as e:
            logger.warning(
                f"LLM generation failed for user {user_id}: {str(e)}. Using fallback."
            )
            # Fall back to curated quests
            quests = self._generate_fallback_quests(preferences)
            fallback_used = True
            model_used = None

        # Create quest objects and save to database
        # add to quest board
        if add_to_board:
            quest_board = self.db.query(QuestBoard).filter_by(user_id=user_id).first()
            if quest_board:
                quest_board_id = quest_board.id
            else:
                quest_board = QuestBoard(user_id=user_id)
                self.db.add(quest_board)
                self.db.commit()
                self.db.refresh(quest_board)
                quest_board_id = quest_board.id
        else:
            quest_board_id = None
        quest_objects = []
        for quest_data in quests:
            quest = SideQuest(
                user_id=user_id,
                text=quest_data["text"],
                category=QuestCategory(quest_data["category"]),
                estimated_time=quest_data["estimated_time"],
                difficulty=QuestDifficulty(quest_data["difficulty"]),
                tags=quest_data["tags"],
                model_used=model_used,
                fallback_used=fallback_used,
                quest_board_id=quest_board_id,
            )
            self.db.add(quest)
            quest_objects.append(quest)

        # Update user's last quest generation time
        user_profile = self.db.query(SideQuestUser).filter_by(user_id=user_id).first()
        if user_profile:
            user_profile.last_quest_generation = datetime.now()

        # Log the generation request
        generation_time_ms = int((time.time() - start_time) * 1000)
        log_entry = QuestGenerationLog(
            user_id=user_id,
            request_preferences=preferences,
            context_data=context,
            quests_generated=len(quest_objects),
            model_used=model_used,
            fallback_used=fallback_used,
            generation_time_ms=generation_time_ms,
            tokens_used=tokens_used,
        )
        self.db.add(log_entry)

        # Commit all changes
        self.db.commit()

        logger.info(
            f"Generated {len(quest_objects)} quests for user {user_id} in {generation_time_ms}ms"
        )
        return quest_objects

    def _generate_with_llm(
        self, preferences: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate quests using OpenAI API"""
        prompt = self._build_quest_generation_prompt(preferences, context)

        try:
            content = self.client.chat(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative quest generator for SideQuest, an app that provides personalized daily challenges. Generate fun, achievable quests that match user preferences.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=1000,
                response_format={"type": "json_object"},
            )
            try:
                quests_data = json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {content}")
                raise Exception("Invalid JSON response from LLM")

            # Validate and format the response
            quests = []
            for quest in quests_data.get("quests", []):
                if self._validate_quest_data(quest):
                    quests.append(quest)

            return quests[:3]  # Ensure we only return 3 quests

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise

    def _build_quest_generation_prompt(
        self, preferences: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for quest generation"""
        categories = preferences.get("categories", [])
        difficulty = preferences.get("difficulty", "medium")
        max_time = preferences.get("max_time", 15)

        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context, indent=2)}"

        return f"""Generate 3 personalized daily quests for SideQuest based on these preferences:

User Preferences:
- Categories: {', '.join(categories)}
- Difficulty: {difficulty}
- Maximum time: {max_time} minutes
- Include completed: {preferences.get('include_completed', True)}
- Include skipped: {preferences.get('include_skipped', True)}

{context_str}

Requirements:
1. Each quest should be achievable within {max_time} minutes
2. Match the user's preferred difficulty level
3. Use categories from their preferences
4. Make quests fun, creative, and engaging
5. Include realistic time estimates
6. Add relevant tags for categorization

Return a JSON object with this structure:
{{
  "quests": [
    {{
      "text": "Quest description",
      "category": "one_of_user_categories",
      "estimated_time": "X-Y minutes",
      "difficulty": "easy|medium|hard",
      "tags": ["tag1", "tag2", "tag3"]
    }}
  ]
}}

Generate quests that will bring joy and novelty to the user's day!"""

    def _validate_quest_data(self, quest: Dict[str, Any]) -> bool:
        """Validate quest data from LLM response"""
        required_fields = ["text", "category", "estimated_time", "difficulty", "tags"]

        # Check required fields
        for field in required_fields:
            if field not in quest:
                logger.warning(f"Quest missing required field: {field}")
                return False

        # Validate category
        try:
            QuestCategory(quest["category"])
        except ValueError:
            logger.warning(f"Invalid quest category: {quest['category']}")
            return False

        # Validate difficulty
        try:
            QuestDifficulty(quest["difficulty"])
        except ValueError:
            logger.warning(f"Invalid quest difficulty: {quest['difficulty']}")
            return False

        # Validate text length
        if len(quest["text"]) < 10 or len(quest["text"]) > 500:
            logger.warning(f"Quest text length invalid: {len(quest['text'])}")
            return False

        return True

    def _generate_fallback_quests(
        self, preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate quests using fallback system when LLM is unavailable"""
        categories = preferences.get("categories", list(self.fallback_quests.keys()))
        difficulty = preferences.get("difficulty", "medium")
        max_time = preferences.get("max_time", 15)

        # Filter fallback quests by user preferences
        available_quests = []
        for category in categories:
            if category in self.fallback_quests:
                category_quests = self.fallback_quests[category]
                # Filter by difficulty and time constraints
                filtered_quests = [
                    q
                    for q in category_quests
                    if q["difficulty"] == difficulty
                    and self._parse_time_estimate(q["estimated_time"]) <= max_time
                ]
                available_quests.extend(filtered_quests)

        # If we don't have enough quests, add some from other categories
        if len(available_quests) < 3:
            all_quests = []
            for quests in self.fallback_quests.values():
                all_quests.extend(quests)

            # Add quests that match difficulty and time constraints
            for quest in all_quests:
                if (
                    quest["difficulty"] == difficulty
                    and self._parse_time_estimate(quest["estimated_time"]) <= max_time
                    and quest not in available_quests
                ):
                    available_quests.append(quest)
                    if len(available_quests) >= 3:
                        break

        # Randomly select 3 quests
        selected_quests = random.sample(available_quests, min(3, len(available_quests)))
        logger.info(f"Generated {len(selected_quests)} fallback quests")

        return selected_quests

    def _parse_time_estimate(self, time_str: str) -> int:
        """Parse time estimate string to minutes"""
        try:
            # Handle formats like "5-10 minutes", "3 minutes", "5-7 min"
            time_str = (
                time_str.lower().replace("minutes", "").replace("min", "").strip()
            )
            if "-" in time_str:
                parts = time_str.split("-")
                return int(parts[1])  # Use the higher estimate
            else:
                return int(time_str)
        except (ValueError, IndexError):
            return 15  # Default fallback
