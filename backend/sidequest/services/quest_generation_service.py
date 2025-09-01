import json
import random
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from openai import OpenAI
from sqlalchemy.orm import Session

from backend.extensions import create_logger
from backend.sidequest.fallback_quests import fallback_quests

from backend.sidequest.models import (
    QuestCategory,
    QuestDifficulty,
    QuestGenerationLog,
)
import logging

logger = logging.getLogger(__name__)


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
        self.fallback_quests = fallback_quests

    def _serialize_datetime_objects(self, data: Any) -> Any:
        """Recursively serialize datetime objects to ISO format strings"""
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {
                key: self._serialize_datetime_objects(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._serialize_datetime_objects(item) for item in data]
        else:
            return data

    def generate_quests(
        self,
        user_id: int,
        preferences: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        n_quests: int = 3,
    ) -> List[Dict[str, Any]]:
        """Generate n_quests personalized daily quests for a user"""
        start_time = time.time()
        fallback_used = False
        model_used = None
        tokens_used = None

        try:
            # Try LLM generation first
            quests = self._generate_with_llm(preferences, context, n_quests)
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
            quests = self._generate_fallback_quests(preferences, n_quests)
            fallback_used = True
            model_used = None

        # Create quest objects and save to database
        # add to quest board

        quest_data = []
        for quest in quests:
            quest["model_used"] = model_used
            quest["fallback_used"] = fallback_used
            quest_data.append(quest)

        generation_time_ms = int((time.time() - start_time) * 1000)

        # Ensure datetime objects are serialized before storing in JSON columns
        serialized_preferences = self._serialize_datetime_objects(preferences)
        serialized_context = (
            self._serialize_datetime_objects(context) if context else None
        )

        log_entry = QuestGenerationLog(
            user_id=user_id,
            request_preferences=serialized_preferences,
            context_data=serialized_context,
            quests_generated=len(quest_data),
            model_used=model_used,
            fallback_used=fallback_used,
            generation_time_ms=generation_time_ms,
            tokens_used=tokens_used,
        )
        self.db.add(log_entry)
        return quest_data

    def _generate_with_llm(
        self,
        preferences: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        n_quests: int = 3,
    ) -> List[Dict[str, Any]]:
        """Generate quests using OpenAI API"""
        prompt = self._build_quest_generation_prompt(preferences, context, n_quests)

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
            return quests[:n_quests]  # Ensure we only return n_quests quests

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise

    def _build_quest_generation_prompt(
        self,
        preferences: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        n_quests: int = 3,
    ) -> str:
        """Build the prompt for quest generation"""
        categories = preferences.get("categories", [])
        difficulty = preferences.get("difficulty", "medium")
        max_time = preferences.get("max_time", 15)

        context_str = ""
        if context:
            context = self._serialize_datetime_objects(context)
            context_str = f"\nContext: {json.dumps(context, indent=2)}"
        user_custom_prompt = ""
        return f"""
You are SideQuest’s quest designer. Generate {n_quests} personalized daily quests that feel like **meaningful side adventures** — concrete, specific, and effortful — bringing novelty, reflection, or discovery into the user’s day. Never output chores or filler.

User Preferences:

- Categories: {', '.join(categories)}
- Difficulty: {difficulty}
- Maximum time: {max_time} minutes

{user_custom_prompt}

{context_str}

## Design Guide

### Core Principles

- **Concrete & specific**: no ambiguity; directly executable.
- **Memorable effort**: feels like a mini-adventure/test.
- **Structured reflection**: include records, constraints, or outputs.
- **Exploration & novelty**: new places, sky, culture.
- **Focused learning**: targeted, speak/repeat/record.
- **Guided creativity**: provide constraints, not freeform.
- **Assignment over choice**: model decides specifics.

### Avoid

- Vague/shallow (“notice the air”).
- Trivial chores (“wash 5 dishes”).
- Open-ended choice (“practice a skill of your choice”).
- Contrived roleplay (“invent a superhero name”).
- Fitness busywork (“10 lunges in hallway”).
- Low-impact media (“listen to a random song”).
- Sky prompts without action (“notice the moon”).

### Anti-Mode-Collapse Rules

1. **Mix of time scales per batch**
   - Micro (1–5 min): ~30%
   - Medium (10–30 min): ~50%
   - Ambitious (1+ hr / multi-step): ~20% (`"ambitious": true`)  
     Ambitious quests may exceed {max_time}.
2. **Category coverage**  
   Cover most of: fitness, social, mindfulness, chores (quest-framed), hobbies, outdoors, learning, creativity.  
   Do not over-index on fitness/micro-mindfulness.
3. **Boundary-pushing quota**  
   ≥20% should feel unusual, adventurous, or experimental.
4. **Quest chains**  
   Occasionally create 2–3 step arcs across the day (morning → afternoon → evening).
5. **External anchors/randomness**  
   Tie to date, weather, dice rolls, holidays, or local context.
6. **Assignment over choice**  
   Always assign specifics.
7. **No repeated skeletons**  
   Avoid duplicate structures in a batch.

### JSON Output Format

Return a JSON object with exactly this structure:

{{
  "quests": [
    {{
      "text": "Quest description",
      "category": "fitness|social|mindfulness|chores|hobbies|outdoors|learning|creativity",
      "estimated_time": "X-Y minutes",
      "difficulty": "easy|medium|hard",
      "ambitious": true|false,
      "tags": ["tag1", "tag2", "tag3"]
    }}
]
}}

### Additional Instructions

- Always respect the user’s selected categories; never invent new ones.
- Match difficulty to {difficulty}.
- Time estimates must be realistic.
- Each quest should be fun, creative, and engaging.
- Ensure variety, ambition, and novelty per the above rules.
- Each quest should be achievable within {max_time} minutes
- Match the user's preferred difficulty level
- Add relevant tags for categorization

Generate quests now.
"""

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
        self, preferences: Dict[str, Any], n_quests: int = 3
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
        if len(available_quests) < n_quests:
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
                    if len(available_quests) >= n_quests:
                        break

        # Randomly select n_quests quests
        selected_quests = random.sample(
            available_quests, min(n_quests, len(available_quests))
        )
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
