#!/usr/bin/env python3
"""
Standalone Touchstone Discovery Script

This script uses Playwright to discover facility IDs and plan IDs from Touchstone gym pages
and stores the results to S3. This is designed to run as a cron job on your local machine.

The script captures:
- facility_id: Unique identifier for each gym (used in API queries)
- plan_ids: List of plan IDs for classes/programs at that gym

Usage:
    python discovery_script.py [--bucket BUCKET_NAME] [--key S3_KEY]

Environment Variables:
    AWS_ACCESS_KEY_ID: AWS access key
    AWS_SECRET_ACCESS_KEY: AWS secret key
"""

import json
import time
import logging
import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add the backend directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.src.s3 import S3
from backend.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Gym pages configuration
GYM_PAGES = {
    "Ironworks": "https://portal.touchstoneclimbing.com/ironworks/n/calendar",
    "Pacific Pipe": "https://portal.touchstoneclimbing.com/pacificpipe/n/calendar",
    "Great Western Power": "https://portal.touchstoneclimbing.com/power/n/calendar",
}

# Default S3 configuration
DEFAULT_BUCKET = "landon-general-storage"
DEFAULT_S3_KEY = "touchstone/discovery.json"


def discover_for_gym(gym: str, page_url: str) -> dict:
    """
    Open the gym page, intercept network:
      - collect the facilityId from StorefrontCalendarPlanQuery
      - collect the 'ids' array sent with StorefrontCalendarPlanQuery (plan IDs)
    Returns {'facility_id': str, 'plan_ids': list}
    """
    logger.info(f"Discovering facility ID and plan IDs for {gym} from {page_url}")
    from playwright.sync_api import sync_playwright
    from playwright._impl._errors import Error as PWError

    facility_id: str = ""
    plan_ids: List[str] = []

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
                            # Capture facility ID
                            nonlocal facility_id
                            input_data = vars.get("input") or {}
                            fid = input_data.get("facilityId")
                            if fid and not facility_id:
                                facility_id = fid
                                logger.info(f"Found facility ID for {gym}: {fid}")

                            # Capture plan IDs
                            ids = vars.get("ids") or []
                            logger.info(
                                f"Found {len(ids)} plan IDs in request for {gym}"
                            )
                            for pid in ids:
                                if pid not in plan_ids:
                                    plan_ids.append(pid)
                    except Exception as e:
                        logger.info(f"Error parsing request for {gym}: {e}")

            # Only need to listen to requests now, not responses
            page.on("request", on_request)

            # Load and nudge a bit so the app fires its queries
            logger.info(f"Loading page for {gym}")
            page.goto(page_url, wait_until="networkidle")
            page.wait_for_timeout(800)
            # Try paging a week to force additional loads
            logger.info(f"Triggering additional loads for {gym}")
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
        f"Discovery complete for {gym}: facility_id={facility_id}, {len(plan_ids)} plan IDs"
    )
    return {"facility_id": facility_id, "plan_ids": plan_ids}


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
                "facility_id": info.get("facility_id", ""),
                "plan_ids": sorted(list(info.get("plan_ids", []))),
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
                f"  {gym}: facility_id={info['facility_id']}, {len(info['plan_ids'])} plan IDs"
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
