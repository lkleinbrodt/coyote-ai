from openai import OpenAI
from os import getenv
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# TODO: make this way better

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=getenv("OPENROUTER_API_KEY"),
)


def get_completion(messages: List[Dict[str, str]]) -> str:
    completion = client.chat.completions.create(
        model="meta-llama/llama-3.2-3b-instruct:free",
        # extra_headers={
        #     "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
        #     "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
        # },
        # pass extra_body to access OpenRouter-only arguments.
        # extra_body={
        # "models": [
        #   "openai/gpt-4o",
        #   "mistralai/mixtral-8x22b-instruct"
        # ]
        # },
        messages=messages,
    )

    return completion.choices[0].message.content


"""
TODO: a class to do something cool
"""
