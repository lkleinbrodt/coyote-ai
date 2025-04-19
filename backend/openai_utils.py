import os
from typing import Any, Dict, Optional

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

NANO = "gpt-4.1-nano-2025-04-14"
MINI = "gpt-4o-mini-2024-07-18"


def extract_number_from_text(text: str, context: Optional[str] = None) -> float:
    """
    Extract a numerical value from text using OpenAI.

    Args:
        text: The text to extract the number from
        context: Optional context to help with extraction (e.g., "cups of food")

    Returns:
        float: The extracted number
    """
    prompt = f"""Extract a numerical value from the following text. 
    Return ONLY the number as a float, no other text or explanation.
    If no number is found, return 0.0.
    If multiple numbers are found, return the most relevant one.
    If the text indicates a negative value, return a negative number.
    
    Example: user says "I ate 2 cups of food", output should be 2.0
    
    Context: {context or 'general'}
    Text: {text}"""

    response = client.chat.completions.create(
        model=NANO,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts numerical values from text. Always respond with just the number as a float.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,  # Low temperature for consistent numerical output
    )

    try:
        return float(response.choices[0].message.content.strip())
    except (ValueError, AttributeError):
        return 0.0


def get_simple_response(prompt: str, system_message: Optional[str] = None) -> str:
    """
    Get a simple text response from OpenAI.

    Args:
        prompt: The user's prompt
        system_message: Optional system message to set the context

    Returns:
        str: The response text
    """
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=NANO,
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def extract_structured_data(text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract structured data from text according to a schema.

    Args:
        text: The text to extract data from
        schema: A dictionary describing the expected structure and types

    Returns:
        Dict[str, Any]: The extracted data
    """
    prompt = f"""Extract structured data from the following text according to this schema.
    Return ONLY a JSON object matching the schema, no other text.
    
    Schema: {schema}
    Text: {text}"""

    response = client.chat.completions.create(
        model=MINI,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts structured data from text. Always respond with valid JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    try:
        import json

        return json.loads(response.choices[0].message.content.strip())
    except (json.JSONDecodeError, AttributeError):
        return {}
