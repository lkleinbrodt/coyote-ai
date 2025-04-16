import json
import os
from decimal import Decimal
from typing import Any, Dict, Tuple

from openai import OpenAI
from openai.types import CompletionUsage

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TITLE_MODEL = "gpt-4.1-nano-2025-04-14"
ANALYSIS_MODEL = "gpt-4o-mini-2024-07-18"


def transcribe_audio(audio_file: bytes) -> str:
    """Transcribe audio file using OpenAI's Whisper API"""
    response = client.audio.transcriptions.create(
        model="whisper-1", file=("audio.m4a", audio_file, "audio/m4a")
    )
    return response.text


def analyze_speech(transcript: str) -> Tuple[Dict[str, Any], Decimal]:
    """Analyze speech transcript using GPT-4. Returns (analysis_data, cost)"""
    prompt = f"""Analyze the following speech transcript and provide detailed feedback.
    Return ONLY a JSON object with the following structure, no other text:
    {{
        "clarity": float (0-10),
        "pace": float (0-10),
        "engagement": float (0-10),
        "overallScore": float (0-10),
        "suggestions": [string],
        "fillerWords": int,
        "toneAnalysis": {{
            "confidence": float (0-10),
            "enthusiasm": float (0-10),
            "professionalism": float (0-10)
        }},
        "contentStructure": {{
            "organization": float (0-10),
            "coherence": float (0-10),
            "keyPoints": [string]
        }}
    }}

    Transcript: {transcript}"""

    response = client.chat.completions.create(
        model=ANALYSIS_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional speech coach providing detailed analysis. Always respond with valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    response_text = response.choices[0].message.content
    try:
        # Find the first { and last } to extract the JSON object
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = response_text[start:end]
            analysis_data = json.loads(json_str)
            cost = OpenAICosts.calculate_gpt4_cost(ANALYSIS_MODEL, response.usage)
            return analysis_data, cost
        else:
            raise ValueError("No valid JSON found in response")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response_text}")
        raise


def get_title(transcript: str) -> Tuple[str, Decimal]:
    """Get a title for the speech recording. Returns (title, cost)"""
    prompt = f"""Generate a title for the following speech transcript. It will be used to identify the speech in the database and for the user to search for it. Be as short and concise as possible.
    Return ONLY a string with the title, no other text. Keep it short and concise.
    Transcript: {transcript}"""

    response = client.chat.completions.create(
        model=TITLE_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates titles for speech recordings.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    response_text = response.choices[0].message.content
    title = response_text.strip().replace('"', "")
    cost = OpenAICosts.calculate_gpt4_cost(TITLE_MODEL, response.usage)
    return title, cost


class ModerationResponse:
    """Represents the response from OpenAI's moderation endpoint"""

    def __init__(
        self,
        flagged: bool,
        categories: Dict[str, bool],
        category_scores: Dict[str, float],
    ):
        self.flagged = flagged
        self.categories = categories
        self.category_scores = category_scores

    def get_reason(self):
        """Get the reason for the moderation"""
        if not self.flagged:
            return None
        # get the category with the highest score
        highest_score_category = max(self.category_scores.items(), key=lambda x: x[1])[
            0
        ]
        return highest_score_category


def moderate_speech(transcript: str) -> ModerationResponse:
    response = client.moderations.create(input=transcript)
    return ModerationResponse(
        flagged=response.results[0].flagged,
        categories=response.results[0].categories,
        category_scores=response.results[0].category_scores,
    )


class OpenAIResponse:
    """Represents a response from OpenAI API with usage data"""

    def __init__(self, content: str, usage: CompletionUsage):
        self.content = content
        self.usage = usage


class OpenAICosts:
    """Configuration for OpenAI API costs"""

    PROFIT_MODIFIER = Decimal("1.25")

    # Cost per minute for Whisper API ($0.006 per second)
    WHISPER_COST_PER_MINUTE = Decimal("0.36") * PROFIT_MODIFIER  # $0.006 * 60

    # GPT-4 costs per 1M tokens
    GPT41_NANO_INPUT_COST = Decimal("0.1") * PROFIT_MODIFIER
    GPT41_NANO_OUTPUT_COST = Decimal("0.4") * PROFIT_MODIFIER
    GPT41_MINI_INPUT_COST = Decimal("0.4") * PROFIT_MODIFIER
    GPT41_MINI_OUTPUT_COST = Decimal("1.6") * PROFIT_MODIFIER

    @classmethod
    def calculate_gpt4_cost(cls, model: str, usage: CompletionUsage) -> Decimal:
        """Calculate cost for GPT-4 API usage based on actual token usage"""
        prompt_tokens = Decimal(str(usage.prompt_tokens))
        completion_tokens = Decimal(str(usage.completion_tokens))

        if model == TITLE_MODEL:
            input_cost = (prompt_tokens * cls.GPT41_NANO_INPUT_COST) / 1_000_000
            output_cost = (completion_tokens * cls.GPT41_NANO_OUTPUT_COST) / 1_000_000
        elif model == ANALYSIS_MODEL:
            input_cost = (prompt_tokens * cls.GPT41_MINI_INPUT_COST) / 1_000_000
            output_cost = (completion_tokens * cls.GPT41_MINI_OUTPUT_COST) / 1_000_000
        else:
            raise ValueError(f"Unknown model: {model}")

        return input_cost + output_cost

    @classmethod
    def calculate_whisper_cost(cls, duration_seconds: int) -> Decimal:
        """Calculate cost for Whisper API transcription"""
        return (Decimal(str(duration_seconds)) / 60) * cls.WHISPER_COST_PER_MINUTE

    @classmethod
    def calculate_moderation_cost(cls) -> Decimal:
        """Calculate cost for moderation API"""
        return Decimal("0.0001")  # $0.0001 per request

    @classmethod
    def estimate_analysis_cost(cls, duration_seconds: float) -> Decimal:
        """Estimate total cost for analysis based on duration"""
        # Calculate transcription cost
        transcription_cost = cls.calculate_whisper_cost(duration_seconds)

        # TODO: have a better way of estimating how much an analysis will cost based on the length of input
        # for now, let's use this logic
        # input: duration in seconds -> output: number of tokens
        # we can use that to estimate input cost
        # then we assume our output will be 1/2 of the input tokens
        # and we use that to estimate the output cost
        # we then add a small constant for the other costs

        # Convert float values to Decimal for consistent decimal arithmetic
        transcription_tokens = Decimal(str(duration_seconds * 3.5))
        analysis_tokens = transcription_tokens / 2
        title_tokens = Decimal("20")  # 10 * 2
        moderation_tokens = Decimal("20")  # 10 * 2

        analysis_input_cost = (
            transcription_tokens * cls.GPT41_MINI_INPUT_COST
        ) / 1_000_000
        analysis_output_cost = (
            analysis_tokens * cls.GPT41_MINI_OUTPUT_COST
        ) / 1_000_000
        title_input_cost = (
            transcription_tokens * cls.GPT41_NANO_INPUT_COST
        ) / 1_000_000
        title_output_cost = (title_tokens * cls.GPT41_NANO_OUTPUT_COST) / 1_000_000
        moderation_cost = cls.calculate_moderation_cost()

        return (
            transcription_cost
            + analysis_input_cost
            + analysis_output_cost
            + title_input_cost
            + title_output_cost
            + moderation_cost
        )
