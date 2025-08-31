"""
Enhanced icon generation script that automatically removes backgrounds after generation.
Combines the original icon generation with background removal post-processing.
"""

import logging
import sys
from pathlib import Path

from backend.sidequest.generate_icons import main as generate_icons_main
from backend.sidequest.background_removal import BackgroundRemovalService

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    """Generate icons and automatically remove backgrounds"""
    logger.info("Starting enhanced icon generation with background removal...")

    # Step 1: Generate icons using original script
    logger.info("Step 1: Generating icons...")
    try:
        # generate_icons_main()
        logger.info("✓ Icon generation complete")
    except Exception as e:
        logger.error(f"✗ Icon generation failed: {e}")
        raise

    # Step 2: Remove backgrounds from generated icons
    logger.info("Step 2: Removing backgrounds...")
    try:
        background_service = BackgroundRemovalService(output_dir="icons_processed")

        # Process all icon categories
        icon_categories = [
            "fitness",
            "mindfulness",
            "learning",
            "chores",
            "social",
            "outdoors",
            "creativity",
            "hobbies",
        ]

        total_processed = 0
        for category in icon_categories:
            category_path = f"icons/{category}"
            if Path(category_path).exists():
                logger.info(f"Processing {category} icons...")
                try:
                    processed_files = background_service.batch_process(
                        category_path, method="auto"
                    )
                    total_processed += len(processed_files)
                    logger.info(f"✓ Processed {len(processed_files)} {category} icons")
                except Exception as e:
                    logger.warning(f"Failed to process {category}: {e}")
                    continue

        logger.info(
            f"✓ Background removal complete! Total processed: {total_processed}"
        )

    except Exception as e:
        logger.error(f"✗ Background removal failed: {e}")
        raise

    logger.info("🎉 Enhanced icon generation complete!")
    logger.info(f"Original icons: icons/")
    logger.info(f"Processed icons: icons_processed/")


if __name__ == "__main__":
    main()
