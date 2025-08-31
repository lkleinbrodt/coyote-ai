"""
Background removal service for post-processing generated icons.
Removes unwanted backgrounds from AI-generated images to create clean, transparent icons.
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional, List
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

logger = logging.getLogger(__name__)


class BackgroundRemovalService:
    """Service for removing backgrounds from generated icons"""

    def __init__(self, output_dir: str = "icons_processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def process_icon(self, input_path: str, method: str = "auto") -> str:
        """
        Process an icon to remove its background

        Args:
            input_path: Path to input image
            method: Removal method ('simple', 'ai', 'auto')

        Returns:
            Path to processed image with transparent background
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input image not found: {input_path}")

        # Determine output path
        output_path = self.output_dir / f"{input_path.stem}_transparent.png"

        try:
            if method == "simple":
                self._remove_simple_background(input_path, output_path)
            elif method == "ai":
                self._remove_ai_background(input_path, output_path)
            elif method == "auto":
                self._auto_background_removal(input_path, output_path)
            else:
                raise ValueError(f"Unknown method: {method}")

            logger.info(f"Successfully processed {input_path} -> {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to process {input_path}: {e}")
            raise

    def _remove_simple_background(self, input_path: Path, output_path: Path):
        """Remove solid color backgrounds using color similarity"""
        with Image.open(input_path) as img:
            # Convert to RGBA if not already
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Get image data
            data = np.array(img)

            # Find the most common background color (usually edges)
            edge_colors = self._get_edge_colors(data)
            if edge_colors:
                # Use a more conservative approach - only remove from edges inward
                mask = self._create_edge_based_mask(data, edge_colors, tolerance=30)

                # Ensure we don't remove too much - keep at least 30% of the image
                foreground_ratio = np.sum(mask) / mask.size
                if foreground_ratio < 0.3:
                    logger.warning(
                        f"Too much content would be removed ({foreground_ratio:.1%}), using original image"
                    )
                    mask = np.ones_like(mask)

                data[:, :, 3] = mask * 255  # Set alpha channel

            # Save result
            result_img = Image.fromarray(data, "RGBA")
            result_img.save(output_path, "PNG")

    def _remove_ai_background(self, input_path: Path, output_path: Path):
        """Remove background using AI-powered rembg library"""
        try:
            # Try multiple import strategies for rembg
            try:
                import rembg

                logger.info("Successfully imported rembg")
            except ImportError:
                try:
                    # Try alternative import path
                    from rembg import remove

                    logger.info("Successfully imported rembg.remove")
                except ImportError:
                    raise ImportError("rembg not available")

            with open(input_path, "rb") as input_file:
                input_data = input_file.read()

            # Use the imported rembg function
            if "rembg" in locals():
                output_data = rembg.remove(input_data)
            else:
                output_data = remove(input_data)

            with open(output_path, "wb") as output_file:
                output_file.write(output_data)

        except ImportError as e:
            logger.warning(f"rembg not available: {e}, falling back to simple method")
            self._remove_simple_background(input_path, output_path)
        except Exception as e:
            logger.warning(f"AI removal failed: {e}, falling back to simple method")
            self._remove_simple_background(input_path, output_path)

    def _auto_background_removal(self, input_path: Path, output_path: Path):
        """Automatically choose the best removal method"""
        try:
            # Try AI method first
            self._remove_ai_background(input_path, output_path)
        except Exception as e:
            logger.info(f"AI method failed, using simple method: {e}")
            self._remove_simple_background(input_path, output_path)

    def _get_edge_colors(self, data: np.ndarray) -> List[Tuple[int, int, int]]:
        """Extract colors from image edges to identify background"""
        height, width = data.shape[:2]

        # Sample colors from edges
        edge_pixels = []

        # Top and bottom edges
        for x in range(0, width, max(1, width // 20)):
            edge_pixels.extend(
                [
                    tuple(data[0, x, :3]),  # Top edge
                    tuple(data[height - 1, x, :3]),  # Bottom edge
                ]
            )

        # Left and right edges
        for y in range(0, height, max(1, height // 20)):
            edge_pixels.extend(
                [
                    tuple(data[y, 0, :3]),  # Left edge
                    tuple(data[y, width - 1, :3]),  # Right edge
                ]
            )

        # Find most common colors (likely background)
        from collections import Counter

        color_counts = Counter(edge_pixels)

        # Return top 3 most common edge colors
        return [color for color, count in color_counts.most_common(3)]

    def _create_edge_based_mask(
        self,
        data: np.ndarray,
        target_colors: List[Tuple[int, int, int]],
        tolerance: int = 30,
    ) -> np.ndarray:
        """Create a mask that removes background starting from edges inward"""
        height, width = data.shape[:2]
        mask = np.ones(data.shape[:2], dtype=bool)

        # Create a simple edge-based approach without external dependencies
        edge_mask = np.zeros((height, width), dtype=bool)

        # Mark edges as potential background
        for target_color in target_colors:
            color_diff = np.sqrt(np.sum((data[:, :, :3] - target_color) ** 2, axis=2))
            edge_mask |= color_diff <= tolerance

        # Only remove background from the outer 20% of the image (edges)
        # This prevents removing content from the center
        edge_width = min(height, width) // 5  # 20% of the smaller dimension

        # Create a mask that only allows background removal near edges
        edge_only_mask = np.zeros((height, width), dtype=bool)

        # Mark the outer edges
        edge_only_mask[:edge_width, :] = True  # Top edge
        edge_only_mask[-edge_width:, :] = True  # Bottom edge
        edge_only_mask[:, :edge_width] = True  # Left edge
        edge_only_mask[:, -edge_width:] = True  # Right edge

        # Only remove background if it's both background color AND near edges
        background_mask = edge_mask & edge_only_mask

        # Apply the background mask
        mask &= ~background_mask

        return mask

    def _create_color_mask(
        self,
        data: np.ndarray,
        target_colors: List[Tuple[int, int, int]],
        tolerance: int = 30,
    ) -> np.ndarray:
        """Create a mask for colors similar to target colors"""
        mask = np.ones(data.shape[:2], dtype=bool)

        for target_color in target_colors:
            # Calculate color distance
            color_diff = np.sqrt(np.sum((data[:, :, :3] - target_color) ** 2, axis=2))
            # Mark pixels within tolerance as background
            mask &= color_diff > tolerance

        return mask

    def batch_process(self, input_dir: str, method: str = "auto") -> List[str]:
        """Process all icons in a directory"""
        input_dir = Path(input_dir)
        processed_files = []

        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Find all image files
        image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
        image_files = [
            f
            for f in input_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        logger.info(f"Found {len(image_files)} images to process")

        for image_file in image_files:
            try:
                output_path = self.process_icon(str(image_file), method)
                processed_files.append(output_path)
            except Exception as e:
                logger.error(f"Failed to process {image_file}: {e}")
                continue

        logger.info(f"Successfully processed {len(processed_files)} images")
        return processed_files

    def enhance_transparency(self, image_path: str, output_path: str):
        """Enhance the transparency and clean up edges"""
        with Image.open(image_path) as img:
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Apply slight blur to smooth edges
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)

            # Save enhanced version
            img.save(output_path, "PNG")


def main():
    """Example usage of the background removal service"""
    service = BackgroundRemovalService()

    # Process a single icon
    # service.process_icon("icons/fitness/fitness_1.png", method="auto")

    # Process all icons in a category
    # service.batch_process("icons/fitness", method="auto")

    print("Background removal service ready!")
    print("Use service.process_icon() or service.batch_process() to remove backgrounds")


if __name__ == "__main__":
    main()
