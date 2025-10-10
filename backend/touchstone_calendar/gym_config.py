"""Shared gym configuration for Touchstone calendar system."""

GYM_CONFIG = {
    "Ironworks": {
        "url": "https://portal.touchstoneclimbing.com/ironworks/n/calendar",
        "slug": "ironworks",
    },
    "Pacific Pipe": {
        "url": "https://portal.touchstoneclimbing.com/pacific/n/calendar",
        "slug": "pacific",
    },
    "Great Western Power": {
        "url": "https://portal.touchstoneclimbing.com/power/n/calendar",
        "slug": "power",
    },
}


def get_gym_names():
    return list(GYM_CONFIG.keys())


def get_gym_url(gym_name: str) -> str:
    return GYM_CONFIG.get(gym_name, {}).get("url", "")


def get_gym_slug(gym_name: str) -> str:
    return GYM_CONFIG.get(gym_name, {}).get("slug", gym_name.lower().replace(" ", ""))


def get_gym_pages():
    return {name: config["url"] for name, config in GYM_CONFIG.items()}


def get_gym_url_slugs():
    return {name: config["slug"] for name, config in GYM_CONFIG.items()}
