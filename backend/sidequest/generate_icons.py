"""
This script will generate icons for the quest categories.
1. get all the categories
For each category:
    2. get enough example quests for each category (if you dont have enough, generate more just for this purpose)
    3. Using thoses quests and other prompts, craft a perfect prompt go give to a AI image generator to generate an icon for the category
    4. save to filesystem
"""

import re
from textwrap import shorten
from dataclasses import dataclass
from typing import List, Dict
import time
import sys
import os

from backend.sidequest.models import QuestCategory, SideQuest
from backend.sidequest.services import QuestGenerationService
from backend.extensions import db
from app import deploy_app
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


# --- Config ------------------------------------------------------------------

CATEGORY_STYLE = {
    QuestCategory.FITNESS: {
        "mascot": "red panda",
        "prop": "dumbbell or jump rope",
        "palette": "lime green and teal",
    },
    QuestCategory.MINDFULNESS: {
        "mascot": "koala",
        "prop": "yoga mat or lotus",
        "palette": "lavender and mint",
    },
    QuestCategory.LEARNING: {
        "mascot": "owl",
        "prop": "book or glasses",
        "palette": "royal blue and gold",
    },
    QuestCategory.CHORES: {
        "mascot": "beaver",
        "prop": "broom or potted plant",
        "palette": "sage and sand",
    },
    QuestCategory.SOCIAL: {
        "mascot": "capybara",
        "prop": "heart or envelope",
        "palette": "peach and rose",
    },
    QuestCategory.OUTDOORS: {
        "mascot": "otter",
        "prop": "leaf or water bottle",
        "palette": "emerald and sky blue",
    },
    QuestCategory.CREATIVITY: {
        "mascot": "cat",
        "prop": "paintbrush or guitar",
        "palette": "magenta and cyan",
    },
    QuestCategory.HOBBIES: {
        "mascot": "fox",
        "prop": "checklist or alarm clock",
        "palette": "orange and cobalt",
    },
}

NEGATIVE_PROMPT = (
    "text, typography, caption, watermark, signature, logo, photorealistic, hyperreal, 3d render, "
    "gore, horror, creepy, lowres, blurry, noisy background, busy scene, harsh shadows, dark mood, "
    "grayscale, extra limbs, distorted hands, deformed"
)

# --- Light keywording from quests --------------------------------------------

ACTION_VERBS = (
    "stretch|meditate|breathe|walk|run|jog|cycle|pushup|push-ups|pullup|lift|yoga|hydrate|read|learn|study|"
    "organize|tidy|clean|declutter|call|text|message|thank|draw|paint|write|play|practice|cook|bake|hike|"
    "journal|focus|plan|review|review|sing|dance"
)


def extract_keywords(quests: List[str], max_len: int = 80) -> str:
    """Extract action verbs and props from quest descriptions"""
    verbs = set()
    nouns = set()
    for q in quests:
        ql = q.lower()
        # verbs
        for m in re.findall(ACTION_VERBS, ql):
            verbs.add(m)
        # crude noun-ish picks: words after "a", "the", "your", "some"
        for m in re.findall(r"\b(?:a|an|the|your|some)\s+([a-z\-']{3,})", ql):
            if m not in verbs and len(m) < 18:
                nouns.add(m)
    bits = []
    if verbs:
        bits.append("actions: " + ", ".join(sorted(verbs)))
    if nouns:
        bits.append("props: " + ", ".join(sorted(list(nouns))[:8]))
    return shorten("; ".join(bits), width=max_len, placeholder="…")


# --- Prompt builders ----------------------------------------------------------


@dataclass
class PromptBundle:
    """Container for all prompt variations and parameters"""

    sd_prompt: str
    sd_negative: str
    sd_params: Dict
    mj_prompt: str
    mj_params: Dict
    dalle_prompt: str
    dalle_params: Dict


def _style_block(cat: QuestCategory) -> Dict:
    """Get style configuration for a category"""
    return CATEGORY_STYLE.get(
        cat,
        {
            "mascot": "friendly animal",
            "prop": "relevant prop",
            "palette": "cheerful pastels",
        },
    )


def craft_prompt_from_examples(
    category: QuestCategory, example_quests: List[str]
) -> PromptBundle:
    """Craft engine-specific prompts from category and example quests"""
    style = _style_block(category)
    kw = extract_keywords(example_quests)

    base_desc = (
        f"cute, playful icon of a {style['mascot']} with a {style['prop']} "
        f"inside a soft rounded badge; cozy lighting, soft shading, clean silhouette, "
        f"high readability at small size; gradient background in {style['palette']}; "
        f"no text."
    )

    # Tailor per engine
    sd_prompt = (
        f"{base_desc} style: whimsical, kawaii, minimal background, vector-like clarity, "
        f"smooth edges, subtle rim light, crisp details. {kw}"
    )

    sd_params = {
        "width": 1024,
        "height": 1024,
        "cfg_scale": 6.5,  # conservative to respect prompt
        "steps": 28,  # SDXL sweet spot
        "sampler": "DPM++ 2M Karras",
        "seed": -1,  # set specific seed for deterministic runs
        "enable_hr": False,
        "restore_faces": False,
        "clip_skip": 2,
    }

    mj_prompt = (
        f"{base_desc}, simple background, flat illustration with soft shading, "
        f"vector icon feel, bold readable silhouette, high contrast, {kw} --no text --no watermark"
    )
    mj_params = {"aspect": "1:1", "style": "4c", "quality": "high"}

    dalle_prompt = (
        f"{base_desc} No background. icon style. white background. Friendly, charming, minimal composition. Focus on the single mascot and one prop. "
        f"Soft gradient badge, clean edges, high contrast. Avoid text, signatures, or logos. {kw}"
    )
    dalle_params = {"size": "1024x1024", "background": "transparent"}

    return PromptBundle(
        sd_prompt=sd_prompt,
        sd_negative=NEGATIVE_PROMPT,
        sd_params=sd_params,
        mj_prompt=mj_prompt,
        mj_params=mj_params,
        dalle_prompt=dalle_prompt,
        dalle_params=dalle_params,
    )


def get_all_categories():
    """Get all the categories"""
    return list(QuestCategory)


def get_enough_example_quests_for_category(category: QuestCategory):
    """Get enough example quests for the category"""
    existing_quests = SideQuest.query.filter_by(category=category).all()
    if len(existing_quests) >= 3:
        return existing_quests
    else:
        return existing_quests + QuestGenerationService(
            db_session=db.session
        )._generate_with_llm(
            {
                "categories": [category],
                "difficulty": "easy",
                "max_time": 15,
            }
        )


def craft_perfect_prompt_for_category(category: QuestCategory):
    """Craft a perfect prompt for the category.

    The goal is to create an image that is: fun! cute! adventerous, adorable. we want the user to be amused and light-hearted by this imagery.
    this image/icon/character will be displayed on a quest card in the app, representing this category.
    """
    quests = get_enough_example_quests_for_category(category)

    # Extract quest text for prompt generation
    quest_texts = []
    for quest in quests:
        if hasattr(quest, "text") and quest.text:
            quest_texts.append(quest.text)
        elif hasattr(quest, "title") and quest.title:
            quest_texts.append(quest.title)
        elif hasattr(quest, "description") and quest.description:
            quest_texts.append(quest.description)

    # Keep it manageable - no more than 6 examples
    quest_texts = quest_texts[:6]

    # Generate the prompt bundle
    bundle = craft_prompt_from_examples(category, quest_texts)

    return {
        "stable_diffusion": {
            "positive": bundle.sd_prompt,
            "negative": bundle.sd_negative,
            "params": bundle.sd_params,
        },
        "midjourney": {
            "prompt": bundle.mj_prompt,
            "params": bundle.mj_params,
        },
        "dalle": {
            "prompt": bundle.dalle_prompt,
            "params": bundle.dalle_params,
        },
        "meta": {
            "category": category.value,
            "examples": quest_texts,
        },
    }


def get_filename_for_category(category: QuestCategory):
    """create thef filename for the next icon in the category
    the output dir will already have icons in it so we need to increment the number
    so {category.value}_1.png,... etc
    """
    base_dir = "icons" + "/" + category.value
    os.makedirs(base_dir, exist_ok=True)
    existing_icons = os.listdir(base_dir)
    if existing_icons:
        return f"{base_dir}/{category.value}_{len(existing_icons) + 1}.png"
    else:
        return f"{base_dir}/{category.value}_1.png"


def generate_icon_for_category(category: QuestCategory):
    """Generate an icon for the category"""
    prompt_data = craft_perfect_prompt_for_category(category)

    # Use DALL-E prompt for now (can be extended to support other engines)
    dalle_prompt = prompt_data["dalle"]["prompt"]
    logger.info(dalle_prompt)
    filename = get_filename_for_category(category)
    # Generate filename based on category

    # Generate the image
    generate_from_prompt(dalle_prompt, filename)

    return filename


from openai import OpenAI
import base64
import os
import requests


def dalle_image_generator(prompt: str, filename: str):
    """Generate image from prompt using DALL-E"""
    client = OpenAI()
    result = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
    )
    # DALL-E 3 returns URLs, not base64
    image_url = result.data[0].url

    # Download the image
    import requests

    response = requests.get(image_url)
    if response.status_code == 200:
        # Save the image to a file
        with open(filename, "wb") as f:
            f.write(response.content)
        logger.info(f"Generated icon saved to: {filename}")
    else:
        logger.error(f"Failed to download image: {response.status_code}")


def image1_generator(prompt: str, filename: str):
    """Generate image from prompt using Image1"""
    client = OpenAI()
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="medium",
        background="transparent",
    )

    image_base64 = result.json()["data"][0]["b64_json"]
    image_bytes = base64.b64decode(image_base64)

    if image_bytes:
        # Save the image to a file
        with open(filename, "wb") as f:
            f.write(image_bytes)
        logger.info(f"Generated icon saved to: {filename}")
    else:
        logger.error(f"Failed to download image: {result.json()}")


def generate_from_prompt(prompt: str, filename: str):
    """Generate image from prompt using DALL-E"""

    # Ensure the icons directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    dalle_image_generator(prompt, filename)


def main():
    """Main function to generate icons for all categories"""
    logger.info("Generating icons for all categories...")

    app = deploy_app()

    logger.info("App deployed")
    with app.app_context():
        categories = get_all_categories()

        logger.info(f"Generating icons for {len(categories)} categories...")

        for category in categories:
            logger.info(f"\nGenerating icon for {category.value}...")
            try:
                filename = generate_icon_for_category(category)
                logger.info(f"✓ Successfully generated {filename}")
            except Exception as e:

                logger.exception(
                    f"✗ Failed to generate icon for {category.value}: {str(e)}"
                )
                raise e

        logger.info("\nIcon generation complete!")


if __name__ == "__main__":
    main()
