# touchstone_consolidate.py
#
# Fetches calendar events from multiple Touchstone gyms using facility IDs
# Categorizes events using OpenAI API and generates registration links
# Exports to CSV and ICS formats, loads discovery data from S3
#
# Requirements:
# - Set OPENAI_API_KEY environment variable for categorization
# - Set AWS credentials for S3 access
# - Run discovery_script.py to populate S3 with facility IDs and plan IDs

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
from backend.touchstone_calendar.gym_config import get_gym_pages, get_gym_url_slugs

TOUCHSTONE_DIR = Config.BACKEND_DIR / "touchstone_calendar"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

URL = "https://portal.touchstoneclimbing.com/graphql-public"
GYM_PAGES = get_gym_pages()
CATEGORIES = ["Yoga", "Climbing", "Fitness", "Youth Programs", "Gym Events"]
DAYS_AHEAD = 7
OUTPUT_CSV = TOUCHSTONE_DIR / "touchstone_calendar.csv"
OUTPUT_ICS = TOUCHSTONE_DIR / "touchstone_calendar.ics"

S3_BUCKET = os.environ.get("TOUCHSTONE_S3_BUCKET", "landon-general-storage")
S3_DISCOVERY_KEY = os.environ.get(
    "TOUCHSTONE_S3_DISCOVERY_KEY", "touchstone/discovery.json"
)
S3_CATEGORY_CACHE_KEY = os.environ.get(
    "TOUCHSTONE_S3_CATEGORY_CACHE_KEY", "touchstone/category_cache.json"
)
MAX_CACHE_EVENTS = 200
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
    rows = fetch_calendar_window(start_d, end_d, facility_id, plan_ids)
    logger.info(f"Fetched {len(rows)} entries for {gym}")

    return rows


def daterange_weeks(start: date, end: date):
    cur = start
    while cur <= end:
        nxt = min(cur + timedelta(days=6), end)
        yield cur.isoformat(), nxt.isoformat()
        cur = nxt + timedelta(days=1)


def load_category_cache_from_s3() -> Dict[str, str]:
    logger.info(f"Loading category cache from s3://{S3_BUCKET}/{S3_CATEGORY_CACHE_KEY}")

    try:
        s3 = S3(S3_BUCKET)
        if s3.exists(S3_CATEGORY_CACHE_KEY):
            cache_data = s3.load_json(S3_CATEGORY_CACHE_KEY)
            logger.info(f"Loaded {len(cache_data)} cached categorizations from S3")
            return cache_data
        else:
            logger.info("No category cache found in S3, starting with empty cache")
            return {}
    except Exception as e:
        logger.warning(f"Error loading category cache from S3: {e}")
        return {}


def save_category_cache_to_s3(cache: Dict[str, str]):
    try:
        if len(cache) > MAX_CACHE_EVENTS:
            logger.info(
                f"Cache has {len(cache)} entries, pruning to {MAX_CACHE_EVENTS}"
            )
            cache_items = list(cache.items())
            cache_items.sort(key=lambda x: x[0])
            pruned_items = cache_items[-MAX_CACHE_EVENTS:]
            cache = dict(pruned_items)
            logger.info(f"Pruned cache to {len(cache)} entries")

        s3 = S3(S3_BUCKET)
        s3.save_json(cache, S3_CATEGORY_CACHE_KEY)
        logger.info(f"Saved {len(cache)} categorizations to S3 cache")
    except Exception as e:
        logger.warning(f"Error saving category cache to S3: {e}")


# ---------- Discovery Management ----------


def categorize_title(title: str, cache: Dict[str, str]) -> str:
    default_category = "Unknown"
    if not title or not title.strip():
        return default_category

    if title in cache:
        return cache[title]

    try:
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


GYM_URL_SLUGS = get_gym_url_slugs()


def get_gym_url_slug(gym_name: str) -> str:
    return GYM_URL_SLUGS.get(gym_name, gym_name.lower().replace(" ", ""))


def generate_registration_link(
    gym: str, title: str, start_local: str, course_id: str, session_id: str
) -> str:
    if not all([gym, title, start_local, course_id, session_id]):
        return ""

    try:
        date_str = start_local[:10] if start_local else ""
        if not date_str:
            return ""

        gym_slug = get_gym_url_slug(gym)
        slug = re.sub(r"[^a-z0-9\s-]", "", title.lower())
        slug = re.sub(r"\s+", "-", slug.strip())

        base_url = f"https://portal.touchstoneclimbing.com/{gym_slug}/programs/{slug}"
        params = f"date={date_str}&course={course_id}&session={session_id}"
        return f"{base_url}?{params}"

    except Exception as e:
        logger.debug(f"Error generating registration link: {e}")
        return ""


def generate_calendar_link(gym: str) -> str:
    gym_slug = get_gym_url_slug(gym)
    return f"https://portal.touchstoneclimbing.com/{gym_slug}/n/calendar"


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
    category_cache = load_category_cache_from_s3()
    logger.info(f"Loaded {len(category_cache)} cached categorizations")

    all_rows: List[Dict[str, Any]] = []
    # Process all gyms defined in GYM_PAGES
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

    # Save category cache to S3
    save_category_cache_to_s3(category_cache)
    logger.info(f"Saved {len(category_cache)} categorizations to S3 cache")

    write_csv(all_rows, OUTPUT_CSV)
    write_ics(all_rows, OUTPUT_ICS)
    logger.info(
        f"Script completed successfully. Rows: {len(all_rows)} → {OUTPUT_CSV} / {OUTPUT_ICS}"
    )
    print(f"Done. Rows: {len(all_rows)} → {OUTPUT_CSV} / {OUTPUT_ICS}")

    return OUTPUT_ICS


if __name__ == "__main__":
    generate_ics()
