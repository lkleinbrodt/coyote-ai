#!/usr/bin/env python3
"""
Standalone Touchstone Discovery Script

This script uses Playwright to discover plan IDs and session hashes from Touchstone gym pages
and stores the results to S3. This is designed to run as a cron job on your local machine.

Usage:
    python discovery_script.py [--bucket BUCKET_NAME] [--key S3_KEY]

Environment Variables:
    AWS_ACCESS_KEY_ID: AWS access key
    AWS_SECRET_ACCESS_KEY: AWS secret key
    OPENAI_API_KEY: OpenAI API key for categorization (optional)
"""

import json
import time
import logging
import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime

# Add the backend directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.s3 import S3
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Gym pages configuration
GYM_PAGES = {
    "ironworks": "https://portal.touchstoneclimbing.com/ironworks/n/calendar",
    "power": "https://portal.touchstoneclimbing.com/power/n/calendar",
    "pacificpipe": "https://portal.touchstoneclimbing.com/pacificpipe/n/calendar",
}

# Default S3 configuration
DEFAULT_BUCKET = "landon-general-storage"
DEFAULT_S3_KEY = "touchstone/discovery.json"


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

    logger.info(
        f"Discovery complete for {gym}: {len(plan_ids)} plan IDs, {len(hashes)} hashes"
    )
    return {"plan_ids": plan_ids, "hashes": hashes}


def ensure_chromium():
    """Install Chromium if it's missing."""
    logger.info("Installing Chromium browser...")
    import subprocess

    subprocess.check_call(["python", "-m", "playwright", "install", "chromium"])
    logger.info("Chromium installation complete")


def refresh_discovery() -> dict:
    """Refresh discovery data using Playwright."""
    logger.info("Refreshing discovery via Playwright…")
    gyms = {}
    for gym, url in GYM_PAGES.items():
        gyms[gym] = discover_for_gym(gym, url)
        time.sleep(0.3)

    # Convert sets to lists for JSON serialization
    result = {
        "generated_at": int(time.time()),
        "gyms": {
            gym: {
                "plan_ids": sorted(list(info.get("plan_ids", []))),
                "hashes": sorted(list(info.get("hashes", []))),
            }
            for gym, info in gyms.items()
        },
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Touchstone Discovery Script")
    parser.add_argument(
        "--bucket",
        default=DEFAULT_BUCKET,
        help=f"S3 bucket name (default: {DEFAULT_BUCKET})",
    )
    parser.add_argument(
        "--key",
        default=DEFAULT_S3_KEY,
        help=f"S3 key for discovery data (default: {DEFAULT_S3_KEY})",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run discovery but don't upload to S3"
    )

    args = parser.parse_args()

    # Validate AWS credentials
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
        logger.error(
            "AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
        )
        sys.exit(1)

    try:
        # Run discovery
        logger.info("Starting Touchstone discovery...")
        discovery_data = refresh_discovery()

        logger.info(f"Discovery completed for {len(discovery_data['gyms'])} gyms")
        for gym, info in discovery_data["gyms"].items():
            logger.info(
                f"  {gym}: {len(info['plan_ids'])} plan IDs, {len(info['hashes'])} hashes"
            )

        if args.dry_run:
            logger.info("Dry run mode - not uploading to S3")
            print(json.dumps(discovery_data, indent=2))
        else:
            # Upload to S3
            logger.info(f"Uploading discovery data to s3://{args.bucket}/{args.key}")
            s3 = S3(args.bucket)
            s3.save_json(discovery_data, args.key)
            logger.info("Discovery data uploaded successfully")

    except Exception as e:
        logger.exception(f"Discovery failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
