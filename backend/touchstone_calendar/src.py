# touchstone_consolidate.py
#
# Configuration:
# - DAYS_AHEAD: Number of days to fetch ahead from today (default: 7)
# - CATEGORIES: List of categories for LLM classification
# - GYM_PAGES: Dictionary of gym names to their calendar page URLs
# - OUTPUT_CSV: Name of the output CSV file (default: touchstone_calendar.csv)
# - OUTPUT_ICS: Name of the output ICS file (default: touchstone_calendar.ics)
# - S3_BUCKET: S3 bucket for discovery data (default: landon-general-storage)
# - S3_DISCOVERY_KEY: S3 key for discovery data (default: touchstone/discovery.json)
#
# Features:
# - Fetches calendar events from multiple Touchstone gyms using facility IDs
# - Each gym has a unique facility_id that ensures gym-specific data
# - Categorizes events using OpenAI API (Yoga, Climbing, Fitness, etc.)
# - Generates direct registration links for each event
# - Includes backup calendar links for each gym location
# - Exports to CSV and ICS formats
# - Loads discovery data from S3 (facility_id + plan_ids per gym)
#
# Requirements:
# - Set OPENAI_API_KEY environment variable for categorization
# - Set AWS credentials for S3 access
# - Run discovery_script.py to populate S3 with facility IDs and plan IDs
# - Install dependencies: pip install -r requirements.txt

import json, time, csv, re, requests, logging
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional, Set
from functools import lru_cache
import openai
import os
from backend.config import Config
from backend.src.s3 import S3

TOUCHSTONE_DIR = Config.BACKEND_DIR / "touchstone_calendar"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------- Config ----------
URL = "https://portal.touchstoneclimbing.com/graphql-public"

GYM_PAGES = {
    "ironworks": "https://portal.touchstoneclimbing.com/ironworks/n/calendar",
    "pacificpipe": "https://portal.touchstoneclimbing.com/pacificpipe/n/calendar",
}

# Categories for classification
CATEGORIES = ["Yoga", "Climbing", "Fitness", "Youth Programs", "Gym Events"]

# Cache file for categorizations
CATEGORY_CACHE_FILE = TOUCHSTONE_DIR / "touchstone_categories.json"

# Date range configuration
DAYS_AHEAD = 7  # Number of days to fetch ahead from today

# Output file configuration
OUTPUT_CSV = TOUCHSTONE_DIR / "touchstone_calendar.csv"
OUTPUT_ICS = TOUCHSTONE_DIR / "touchstone_calendar.ics"

# S3 configuration for discovery data
S3_BUCKET = os.environ.get("TOUCHSTONE_S3_BUCKET", "landon-general-storage")
S3_DISCOVERY_KEY = os.environ.get(
    "TOUCHSTONE_S3_DISCOVERY_KEY", "touchstone/discovery.json"
)

# ---------- GraphQL ----------
CAL_Q = """
query StorefrontCalendarQuery($input: CalendarFilter) {
  calendar(input: $input) {
    courseId
    sessionGraphId
    sessionFacilityHash
    startLocal
    endLocal
    publicTitle
    capacityText
    instructorText
    planId
  }
}
"""


def gql(query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug(f"Making GraphQL request with variables: {variables}")
    r = requests.post(URL, json={"query": query, "variables": variables}, timeout=25)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        logger.error(f"GraphQL errors: {data['errors']}")
        raise RuntimeError(data["errors"])
    return data["data"]


# ---------- S3 Discovery Loading ----------
def load_discovery_from_s3() -> dict:
    """
    Load discovery data from S3.
    Returns discovery data with gym facility IDs and plan IDs.
    """
    logger.info(f"Loading discovery data from s3://{S3_BUCKET}/{S3_DISCOVERY_KEY}")

    try:
        s3 = S3(S3_BUCKET)
        discovery_data = s3.load_json(S3_DISCOVERY_KEY)

        logger.info(
            f"Loaded discovery data for {len(discovery_data.get('gyms', {}))} gyms"
        )
        return discovery_data

    except Exception as e:
        logger.error(f"Failed to load discovery data from S3: {e}")
        raise RuntimeError(f"Could not load discovery data from S3: {e}")


# ---------- Fetch calendar with chunked plan IDs ----------
def fetch_calendar_window(
    start_d: str, end_d: str, facility_id: str, plan_ids: List[str]
) -> List[Dict[str, Any]]:
    logger.info(
        f"Fetching calendar for facility {facility_id}: {len(plan_ids)} plans from {start_d} to {end_d}"
    )
    all_rows: List[Dict[str, Any]] = []

    def try_chunk(ids: List[str]) -> List[Dict[str, Any]]:
        inp = {
            "facilityId": [facility_id],  # Use gym-specific facility ID
            "startDate": start_d,
            "endDate": end_d,
            "planId": ids,
        }
        return gql(CAL_Q, {"input": inp}).get("calendar") or []

    chunk = 100
    i = 0
    chunk_count = 0
    while i < len(plan_ids):
        sub = plan_ids[i : i + chunk]
        chunk_count += 1
        logger.debug(f"Processing chunk {chunk_count} with {len(sub)} plan IDs")
        try:
            rows = try_chunk(sub)
            all_rows.extend(rows)
            logger.debug(f"Chunk {chunk_count} returned {len(rows)} calendar entries")
            i += chunk
        except Exception as e:
            logger.warning(f"Chunk {chunk_count} failed: {e}")
            if chunk == 1:
                logger.warning(f"Skipping bad plan ID at index {i}")
                i += 1  # skip bad id
            else:
                chunk = max(1, chunk // 2)
                logger.info(f"Reducing chunk size to {chunk} and retrying")
                time.sleep(0.25)
    logger.info(
        f"Calendar fetch complete: {len(all_rows)} total entries from {chunk_count} chunks"
    )
    return all_rows


def fetch_calendar_for_gym(
    gym: str, start_d: str, end_d: str, discovery_data: dict
) -> List[Dict[str, Any]]:
    """
    Fetch calendar data for a specific gym using facility ID and plan IDs.
    The API returns only gym-specific data when given the correct facility ID.
    """
    if gym not in discovery_data.get("gyms", {}):
        logger.error(f"Gym '{gym}' not found in discovery data")
        return []

    gym_info = discovery_data["gyms"][gym]
    facility_id = gym_info.get("facility_id", "")
    plan_ids = list(gym_info.get("plan_ids", []))

    if not facility_id:
        logger.error(f"No facility ID found for gym '{gym}'")
        return []

    if not plan_ids:
        logger.warning(f"No plan IDs found for gym '{gym}'")
        return []

    logger.info(
        f"Fetching calendar for {gym} (facility: {facility_id}) with {len(plan_ids)} plan IDs"
    )

    # Fetch data using facility ID and plan IDs - API handles gym filtering
    rows = fetch_calendar_window(start_d, end_d, facility_id, plan_ids)
    logger.info(f"Fetched {len(rows)} entries for {gym}")

    return rows


def daterange_weeks(start: date, end: date):
    cur = start
    while cur <= end:
        nxt = min(cur + timedelta(days=6), end)
        yield cur.isoformat(), nxt.isoformat()
        cur = nxt + timedelta(days=1)


def load_category_cache() -> Dict[str, str]:
    """Load the category cache from file."""
    cache_path = Path(CATEGORY_CACHE_FILE)
    if cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading category cache: {e}")
    return {}


def save_category_cache(cache: Dict[str, str]):
    """Save the category cache to file."""
    try:
        with open(CATEGORY_CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.warning(f"Error saving category cache: {e}")


# ---------- Discovery Management ----------


def categorize_title(title: str, cache: Dict[str, str]) -> str:
    """
    Categorize a publicTitle using OpenAI API with caching.
    Returns one of the predefined categories.
    """
    default_category = "Unknown"
    if not title or not title.strip():
        return default_category  # Default category

    # Check cache first
    if title in cache:
        return cache[title]

    try:
        # Initialize OpenAI client (you'll need to set OPENAI_API_KEY environment variable)
        client = openai.OpenAI()

        prompt = f"""
        Categorize this gym class/event title into exactly one of these categories:
        {', '.join(CATEGORIES)}
        
        Title: "{title}"
        
        Return only the category name, nothing else.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.1,
        )

        category = response.choices[0].message.content.strip()

        # Validate category
        if category in CATEGORIES:
            cache[title] = category
            logger.debug(f"Categorized '{title}' as '{category}'")
            return category
        else:
            logger.warning(
                f"Invalid category '{category}' for '{title}', using default"
            )
            cache[title] = default_category
            return default_category

    except Exception as e:
        logger.warning(f"Error categorizing '{title}': {e}, using default")
        cache[title] = default_category
        return default_category


def generate_registration_link(
    gym: str, title: str, start_local: str, course_id: str, session_id: str
) -> str:
    """
    Generate a registration link for a Touchstone event.
    Format: https://portal.touchstoneclimbing.com/{gym}/programs/{slug}?date={date}&course={course}&session={session}
    """
    if not all([gym, title, start_local, course_id, session_id]):
        return ""

    try:
        # Extract date from start_local (format: "2025-10-07 10:00:00")
        date_str = start_local[:10] if start_local else ""
        if not date_str:
            return ""

        # Create a URL-friendly slug from the title
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        slug = re.sub(r"[^a-z0-9\s-]", "", title.lower())
        slug = re.sub(r"\s+", "-", slug.strip())

        # Build the registration link
        base_url = f"https://portal.touchstoneclimbing.com/{gym}/programs/{slug}"
        params = f"date={date_str}&course={course_id}&session={session_id}"

        return f"{base_url}?{params}"

    except Exception as e:
        logger.debug(f"Error generating registration link: {e}")
        return ""


def generate_calendar_link(gym: str) -> str:
    """
    Generate a backup calendar link for a Touchstone gym.
    Format: https://portal.touchstoneclimbing.com/{gym}/n/calendar
    """
    return f"https://portal.touchstoneclimbing.com/{gym}/n/calendar"


# ---------- Writers ----------
def write_csv(rows: List[Dict[str, Any]], path: str):
    logger.info(f"Writing {len(rows)} rows to CSV: {path}")
    cols = [
        "gym",
        "startLocal",
        "endLocal",
        "publicTitle",
        "category",
        "capacityText",
        "instructorText",
        "planId",
        "courseId",
        "sessionGraphId",
        "registrationLink",
        "calendarLink",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})
    logger.info(f"CSV file written successfully: {path}")


def write_ics(rows: List[Dict[str, Any]], path: str, tzname="America/Los_Angeles"):
    logger.info(f"Writing {len(rows)} rows to ICS calendar: {path}")
    TZ = ZoneInfo(tzname)

    def to_utc(s: str) -> Optional[str]:
        try:
            dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
            return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        except Exception:
            return None

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Touchstone Consolidator//EN"]
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    valid_events = 0
    for idx, r in enumerate(rows, 1):
        ds = to_utc(r["startLocal"])
        de = to_utc(r["endLocal"])
        if not ds:
            continue
        valid_events += 1
        summary = f"[{r.get('gym','')}] {r.get('publicTitle','')}"
        desc = []
        if r.get("instructorText"):
            desc.append(f"Instructor: {r['instructorText']}")
        if r.get("capacityText"):
            desc.append(f"Capacity: {r['capacityText']}")
        if r.get("registrationLink"):
            desc.append(f"Register: {r['registrationLink']}")
        if r.get("calendarLink"):
            desc.append(f"Calendar: {r['calendarLink']}")
        lines += [
            "BEGIN:VEVENT",
            f"UID:{idx}-{r.get('gym','unknown')}@touchstone",
            f"DTSTAMP:{now}",
            f"DTSTART:{ds}",
            *([f"DTEND:{de}"] if de else []),
            f"SUMMARY:{summary}",
            f"LOCATION:{r.get('gym','')}",
            "DESCRIPTION:" + "\\n".join(desc),
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")

    # Atomic write: write to temp file first, then rename
    path_obj = Path(path)
    tmp_path = path_obj.with_suffix(".ics.tmp")

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        # Atomic rename on the same filesystem
        tmp_path.replace(path_obj)
        logger.info(
            f"ICS calendar written successfully: {path} with {valid_events} valid events"
        )
    except Exception as e:
        # Clean up temp file if it exists
        if tmp_path.exists():
            tmp_path.unlink()
        raise e


def generate_ics():
    START = date.today()
    END = START + timedelta(days=DAYS_AHEAD)

    logger.info(f"Starting Touchstone calendar consolidation from {START} to {END}")
    logger.info(f"Processing {len(GYM_PAGES)} gyms: {list(GYM_PAGES.keys())}")
    logger.info(
        f"Fetching {DAYS_AHEAD} days ahead (configurable via DAYS_AHEAD variable)"
    )

    # 1) Load discovery data from S3
    try:
        discovery_data = load_discovery_from_s3()
        discovery = discovery_data["gyms"]
    except Exception as e:
        logger.error(f"Failed to load discovery data: {e}")
        raise RuntimeError(f"Could not load discovery data from S3: {e}")

    # 2) Load category cache and fetch sessions per gym with those plan IDs
    category_cache = load_category_cache()
    logger.info(f"Loaded {len(category_cache)} cached categorizations")

    all_rows: List[Dict[str, Any]] = []
    # Only process gyms we want (exclude power)
    for gym in GYM_PAGES.keys():
        if gym not in discovery:
            logger.warning(f"Gym '{gym}' not found in discovery data, skipping")
            continue
        info = discovery[gym]
        logger.info(f"Processing gym: {gym}")

        facility_id = info.get("facility_id", "")
        plan_ids = sorted(set(info.get("plan_ids", [])))

        if not facility_id:
            logger.error(f"{gym}: no facility ID discovered; skipping")
            continue
        if not plan_ids:
            logger.warning(f"{gym}: no plan IDs discovered; skipping")
            continue

        logger.info(
            f"{gym}: using facility_id={facility_id} with {len(plan_ids)} plan IDs"
        )

        gym_rows: List[Dict[str, Any]] = []
        week_count = 0
        for s, e in daterange_weeks(START, END):
            week_count += 1
            logger.info(f"Fetching week {week_count} for {gym}: {s} to {e}")
            rows = fetch_calendar_window(s, e, facility_id, plan_ids)

            logger.info(f"Week {week_count} for {gym}: {len(rows)} entries fetched")
            for r in rows:
                r["gym"] = gym
                # Add category using LLM
                title = r.get("publicTitle", "")
                category = categorize_title(title, category_cache)
                r["category"] = category

                # Generate registration link
                course_id = r.get("courseId", "")
                session_id = r.get("sessionGraphId", "")
                start_local = r.get("startLocal", "")
                registration_link = generate_registration_link(
                    gym, title, start_local, course_id, session_id
                )
                r["registrationLink"] = registration_link

                # Generate backup calendar link
                calendar_link = generate_calendar_link(gym)
                r["calendarLink"] = calendar_link

            gym_rows.extend(rows)
            logger.debug(f"Week {week_count} for {gym}: {len(rows)} entries added")
            time.sleep(0.2)

        logger.info(f"Completed {gym}: {len(gym_rows)} total entries")

        # Log warning if no data found for a gym
        if len(gym_rows) == 0:
            logger.warning(
                f"{gym}: 0 rows after filtering — discovery data may be stale. "
                f"Run discovery_script.py to refresh data."
            )

        all_rows.extend(gym_rows)

    # 3) De-dupe + sort
    logger.info("Deduplicating entries across gyms and time windows")
    seen = set()
    uniq: List[Dict[str, Any]] = []
    for r in all_rows:
        key = (
            r.get("startLocal"),
            r.get("endLocal"),
            r.get("publicTitle"),
            r.get("gym"),
        )
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    all_rows = uniq
    logger.info(f"After deduplication: {len(all_rows)} unique entries")

    def keyer(r):
        try:
            return datetime.strptime(r["startLocal"], "%Y-%m-%d %H:%M:%S")
        except:
            return datetime.max

    all_rows.sort(key=keyer)

    # Save category cache
    save_category_cache(category_cache)
    logger.info(f"Saved {len(category_cache)} categorizations to cache")

    write_csv(all_rows, OUTPUT_CSV)
    write_ics(all_rows, OUTPUT_ICS)
    logger.info(
        f"Script completed successfully. Rows: {len(all_rows)} → {OUTPUT_CSV} / {OUTPUT_ICS}"
    )
    print(f"Done. Rows: {len(all_rows)} → {OUTPUT_CSV} / {OUTPUT_ICS}")

    return OUTPUT_ICS


if __name__ == "__main__":
    generate_ics()
