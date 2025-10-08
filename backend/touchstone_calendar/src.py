# touchstone_consolidate.py
#
# Configuration:
# - DAYS_AHEAD: Number of days to fetch ahead from today (default: 7)
# - CATEGORIES: List of categories for LLM classification
# - GYM_PAGES: Dictionary of gym names to their calendar page URLs
# - OUTPUT_CSV: Name of the output CSV file (default: touchstone_calendar.csv)
# - OUTPUT_ICS: Name of the output ICS file (default: touchstone_calendar.ics)
#
# Features:
# - Fetches calendar events from multiple Touchstone gyms
# - Categorizes events using OpenAI API (Yoga, Climbing, Fitness, etc.)
# - Generates direct registration links for each event
# - Includes backup calendar links for each gym location
# - Exports to CSV and ICS formats
#
# Requirements:
# - Set OPENAI_API_KEY environment variable for categorization
# - Install dependencies: pip install -r requirements_touchstone.txt

import json, time, csv, re, requests, logging
from pathlib import Path
from datetime import date, timedelta, datetime, timezone
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional, Set
from functools import lru_cache
import openai
import subprocess
import os
from backend.config import Config

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
FACILITY_ID = "RmFjaWxpdHk6MTMwNw=="

GYM_PAGES = {
    "ironworks": "https://portal.touchstoneclimbing.com/ironworks/n/calendar",
    "power": "https://portal.touchstoneclimbing.com/power/n/calendar",
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

# Discovery caching configuration
DISCOVERY_TTL_SECONDS = 24 * 60 * 60  # 1 day
DISCOVERY_FILE = TOUCHSTONE_DIR / "touchstone_discovery.json"

# Playwright browser configuration
BROWSERS_PATH = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/app/ms-playwright")
# Fallback to default Playwright cache location if custom path doesn't work
DEFAULT_BROWSERS_PATH = os.path.expanduser("~/.cache/ms-playwright")

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


# ---------- Discovery via Playwright ----------
def discover_for_gym(gym: str, page_url: str) -> dict:
    """
    Open the gym page, intercept network:
      - collect the 'ids' array sent with StorefrontCalendarPlanQuery (plan IDs)
      - collect all sessionFacilityHash values returned by StorefrontCalendarQuery
    Returns {'plan_ids': set(...), 'hashes': set(...)}
    """
    logger.info(f"Discovering plan IDs and hashes for {gym} from {page_url}")
    from playwright.sync_api import sync_playwright
    from playwright._impl._errors import Error as PWError

    plan_ids: Set[str] = set()
    hashes: Set[str] = set()

    def run_discovery():
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            page = browser.new_page()

            def on_request(req):
                if req.url.endswith("/graphql-public") and req.method == "POST":
                    try:
                        body = req.post_data_json
                        q = (body or {}).get("query", "")
                        vars = (body or {}).get("variables") or {}
                        if "StorefrontCalendarPlanQuery" in q:
                            ids = vars.get("ids") or []
                            logger.debug(
                                f"Found {len(ids)} plan IDs in request for {gym}"
                            )
                            for pid in ids:
                                plan_ids.add(pid)
                    except Exception as e:
                        logger.debug(f"Error parsing request for {gym}: {e}")

            def on_response(resp):
                if (
                    resp.url.endswith("/graphql-public")
                    and resp.request.method == "POST"
                ):
                    try:
                        j = resp.json()
                        cal = ((j or {}).get("data") or {}).get("calendar") or []
                        logger.debug(
                            f"Found {len(cal)} calendar entries in response for {gym}"
                        )
                        for it in cal:
                            h = it.get("sessionFacilityHash")
                            if h:
                                hashes.add(h)
                    except Exception as e:
                        logger.debug(f"Error parsing response for {gym}: {e}")

            page.on("request", on_request)
            page.on("response", on_response)

            # Load and nudge a bit so the app fires its queries
            logger.debug(f"Loading page for {gym}")
            page.goto(page_url, wait_until="networkidle")
            page.wait_for_timeout(800)
            # Try paging a week to force additional loads
            logger.debug(f"Triggering additional loads for {gym}")
            page.keyboard.press("PageDown")
            page.wait_for_timeout(800)

            page.close()
            browser.close()

    try:
        run_discovery()
    except PWError as e:
        if "Executable doesn't exist" in str(e):
            logger.warning("Chromium not found, installing...")
            ensure_chromium()
            run_discovery()
        else:
            raise
    except Exception as e:
        # If Playwright completely fails (e.g., missing system dependencies in container)
        logger.error(f"Playwright discovery failed for {gym}: {e}")
        logger.warning(
            f"Falling back to empty discovery for {gym} - calendar may include events from other gyms"
        )
        # Return empty sets - the system will still work but may include events from other gyms
        return {"plan_ids": set(), "hashes": set()}

    logger.info(
        f"Discovery complete for {gym}: {len(plan_ids)} plan IDs, {len(hashes)} hashes"
    )
    return {"plan_ids": plan_ids, "hashes": hashes}


# ---------- Fetch calendar with chunked plan IDs ----------
def fetch_calendar_window(
    start_d: str, end_d: str, plan_ids: List[str]
) -> List[Dict[str, Any]]:
    logger.info(
        f"Fetching calendar for {len(plan_ids)} plans from {start_d} to {end_d}"
    )
    all_rows: List[Dict[str, Any]] = []

    def try_chunk(ids: List[str]) -> List[Dict[str, Any]]:
        inp = {
            "facilityId": [FACILITY_ID],
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


def daterange_weeks(start: date, end: date):
    cur = start
    while cur <= end:
        nxt = min(cur + timedelta(days=6), end)
        yield cur.isoformat(), nxt.isoformat()
        cur = nxt + timedelta(days=1)


def build_gym_keyset(
    gym: str, plan_ids: List[str], start_date: str, end_date: str
) -> Set[tuple]:
    """
    Build a keyset of (startLocal, endLocal, planId) tuples for sessions that belong to this gym.
    This is much more efficient than checking each session individually.
    """
    try:
        # Fetch all sessions for this gym's plan IDs
        rows = fetch_calendar_window(start_date, end_date, plan_ids)

        # Create keyset of sessions that belong to this gym
        keyset = set()
        for r in rows:
            key = (r.get("startLocal", ""), r.get("endLocal", ""), r.get("planId", ""))
            if all(key):  # Only add if all fields are present
                keyset.add(key)

        logger.debug(f"Built keyset for {gym}: {len(keyset)} unique sessions")
        return keyset
    except Exception as e:
        logger.warning(f"Error building keyset for {gym}: {e}")
        return set()


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


# ---------- Discovery Caching ----------


def _now_ts() -> int:
    """Get current timestamp."""
    return int(time.time())


def _load_discovery():
    """Load discovery data from cache file."""
    if not DISCOVERY_FILE.exists():
        return None
    try:
        data = json.loads(DISCOVERY_FILE.read_text())
        return data
    except Exception as e:
        logger.warning(f"Failed to load discovery: {e}")
        return None


def _save_discovery(d):
    """Save discovery data to cache file."""
    # ensure sets→lists for json
    out = {
        gym: {
            "plan_ids": sorted(list(info.get("plan_ids", []))),
            "hashes": sorted(list(info.get("hashes", []))),
        }
        for gym, info in d.get("gyms", {}).items()
    }
    payload = {
        "generated_at": _now_ts(),
        "gyms": out,
    }
    DISCOVERY_FILE.parent.mkdir(parents=True, exist_ok=True)
    DISCOVERY_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def _needs_discovery_refresh(doc, ttl_seconds=DISCOVERY_TTL_SECONDS) -> bool:
    """Check if discovery data needs refresh based on TTL."""
    if not doc:
        return True
    gen = int(doc.get("generated_at", 0))
    return (_now_ts() - gen) > ttl_seconds


def refresh_discovery() -> dict:
    """Refresh discovery data using Playwright."""
    logger.info("Refreshing discovery via Playwright…")
    gyms = {}
    for gym, url in GYM_PAGES.items():
        gyms[gym] = discover_for_gym(gym, url)
        time.sleep(0.3)
    return _save_discovery({"gyms": gyms})


# ---------- Playwright Browser Management ----------


def ensure_chromium():
    """Install Chromium if it's missing."""
    logger.info("Installing Chromium browser...")

    # Try custom path first
    try:
        subprocess.check_call(
            ["python", "-m", "playwright", "install", "chromium"],
            env={**os.environ, "PLAYWRIGHT_BROWSERS_PATH": BROWSERS_PATH},
        )
        logger.info("Chromium installation complete with custom path")
        return
    except Exception as e:
        logger.warning(f"Failed to install with custom path {BROWSERS_PATH}: {e}")

    # Fallback to default path
    try:
        subprocess.check_call(
            ["python", "-m", "playwright", "install", "chromium"],
            env={**os.environ, "PLAYWRIGHT_BROWSERS_PATH": DEFAULT_BROWSERS_PATH},
        )
        logger.info("Chromium installation complete with default path")
        return
    except Exception as e:
        logger.warning(
            f"Failed to install with default path {DEFAULT_BROWSERS_PATH}: {e}"
        )

    # If both fail, try without custom path (let Playwright use its default)
    try:
        subprocess.check_call(
            ["python", "-m", "playwright", "install", "chromium"],
        )
        logger.info("Chromium installation complete with Playwright default path")
    except Exception as e:
        logger.error(f"All Chromium installation attempts failed: {e}")
        raise


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

    # 1) Load discovery data with TTL-based caching
    doc = _load_discovery()
    if _needs_discovery_refresh(doc):
        logger.info("Discovery cache expired or missing, refreshing via Playwright...")
        try:
            doc = refresh_discovery()
        except Exception as e:
            logger.error(f"Discovery refresh failed: {e}")
            logger.warning(
                "Using empty discovery - calendar may include events from all gyms"
            )
            # Create a minimal discovery structure with empty data
            doc = {
                "generated_at": _now_ts(),
                "gyms": {
                    gym: {"plan_ids": [], "hashes": []} for gym in GYM_PAGES.keys()
                },
            }
    else:
        logger.info("Using cached discovery (fresh)")
    discovery = doc["gyms"]

    # 2) Load category cache and fetch sessions per gym with those plan IDs
    category_cache = load_category_cache()
    logger.info(f"Loaded {len(category_cache)} cached categorizations")

    # Check if we have any valid discovery data
    has_valid_discovery = any(info.get("plan_ids") for info in discovery.values())

    if not has_valid_discovery:
        logger.warning(
            "No valid discovery data found - this may be due to Playwright issues in containerized environment"
        )
        logger.warning(
            "Calendar generation will be skipped. Consider running in an environment with proper Playwright dependencies."
        )
        # Return early with empty results
        write_csv([], OUTPUT_CSV)
        write_ics([], OUTPUT_ICS)
        logger.info("Generated empty calendar files due to discovery failure")
        return OUTPUT_ICS

    all_rows: List[Dict[str, Any]] = []
    for gym, info in discovery.items():
        logger.info(f"Processing gym: {gym}")
        plan_ids = sorted(set(info.get("plan_ids", [])))
        allowed_hashes = set(info.get("hashes", []))

        if not plan_ids:
            logger.warning(f"{gym}: no plan ids discovered; trying fallback approach")
            # Fallback: try to use a generic approach or skip this gym
            # For now, we'll skip but log the issue
            logger.warning(
                f"{gym}: skipping due to no plan IDs - this may be due to Playwright issues in containerized environment"
            )
            continue
        if not allowed_hashes:
            logger.warning(
                f"{gym}: no hashes discovered; results may include other gyms (will not filter)"
            )

        logger.info(
            f"{gym}: using {len(plan_ids)} plan IDs and {len(allowed_hashes)} allowed hashes"
        )

        # Build authoritative keyset for this gym (much more efficient than per-session checks)
        logger.info(f"Building authoritative keyset for {gym}...")
        gym_keyset = build_gym_keyset(gym, plan_ids, START.isoformat(), END.isoformat())
        logger.info(f"Built keyset for {gym}: {len(gym_keyset)} unique sessions")

        gym_rows: List[Dict[str, Any]] = []
        week_count = 0
        for s, e in daterange_weeks(START, END):
            week_count += 1
            logger.info(f"Fetching week {week_count} for {gym}: {s} to {e}")
            rows = fetch_calendar_window(s, e, plan_ids)

            # Debug: inspect why matches might be zero (from the other AI's suggestion)
            if gym == "ironworks" and week_count == 1:
                hashes_seen = {
                    r.get("sessionFacilityHash")
                    for r in rows
                    if r.get("sessionFacilityHash")
                }
                intersection = len(hashes_seen & allowed_hashes)
                logger.info(
                    f"[debug] {gym}: fetched {len(rows)} rows; unique hashes in rows: {len(hashes_seen)}; "
                    f"intersection with allowed_hashes: {intersection}"
                )

            # Efficient keyset filtering - check each session against the gym's authoritative keyset
            original_count = len(rows)
            filtered = []
            for r in rows:
                key = (
                    r.get("startLocal", ""),
                    r.get("endLocal", ""),
                    r.get("planId", ""),
                )
                if key in gym_keyset:
                    filtered.append(r)
            rows = filtered
            logger.info(
                f"Week {week_count} for {gym}: {original_count} entries before filtering, {len(rows)} after keyset filtering"
            )
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

        # Self-heal if a gym collapses (no data)
        if len(gym_rows) == 0:
            logger.warning(
                f"{gym}: 0 rows after filtering — refreshing discovery for this gym and retrying once"
            )
            try:
                # refresh just this gym
                fresh = discover_for_gym(gym, GYM_PAGES[gym])
                # update in-memory discovery and persist to file
                doc["gyms"][gym] = fresh
                _save_discovery(doc)

                # re-run for this gym
                plan_ids = sorted(set(fresh.get("plan_ids", [])))
                gym_keyset = build_gym_keyset(
                    gym, plan_ids, START.isoformat(), END.isoformat()
                )
                retry_rows = []
                for s, e in daterange_weeks(START, END):
                    rows = fetch_calendar_window(s, e, plan_ids)
                    filtered = []
                    for r in rows:
                        key = (
                            r.get("startLocal", ""),
                            r.get("endLocal", ""),
                            r.get("planId", ""),
                        )
                        if key in gym_keyset:
                            filtered.append(r)
                    for r in filtered:
                        r["gym"] = gym
                        title = r.get("publicTitle", "")
                        r["category"] = categorize_title(title, category_cache)
                        r["registrationLink"] = generate_registration_link(
                            gym,
                            title,
                            r.get("startLocal", ""),
                            r.get("courseId", ""),
                            r.get("sessionGraphId", ""),
                        )
                        r["calendarLink"] = generate_calendar_link(gym)
                    retry_rows.extend(filtered)
                gym_rows = retry_rows
                logger.info(f"{gym}: after refresh, {len(gym_rows)} rows")
            except Exception as e:
                logger.warning(f"{gym}: refresh failed: {e}")

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
