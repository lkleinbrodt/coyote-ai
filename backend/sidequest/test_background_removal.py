"""
Test script for the background removal service.
Creates a simple test image and processes it to verify functionality.
"""

import os
from PIL import Image, ImageDraw
from background_removal import BackgroundRemovalService


def create_test_image():
    """Create a simple test image with a solid background"""
    # Create a 256x256 image with a blue background
    img = Image.new("RGB", (256, 256), color="#4A90E2")
    draw = ImageDraw.Draw(img)

    # Draw a simple red circle in the center
    circle_bbox = (78, 78, 178, 178)  # Centered circle
    draw.ellipse(circle_bbox, fill="#E74C3C")

    # Save test image
    test_path = "test_icon.png"
    img.save(test_path)
    print(f"Created test image: {test_path}")

    return test_path


def test_background_removal():
    """Test the background removal service"""
    print("Testing background removal service...")

    # Create test image
    test_image = create_test_image()

    # Initialize service
    service = BackgroundRemovalService(output_dir="test_output")

    try:
        # Test simple background removal
        print("Testing simple background removal...")
        result_path = service.process_icon(test_image, method="simple")
        print(f"✓ Simple removal result: {result_path}")

        # Test AI background removal (if available)
        print("Testing AI background removal...")
        try:
            ai_result_path = service.process_icon(test_image, method="ai")
            print(f"✓ AI removal result: {ai_result_path}")
        except Exception as e:
            print(f"⚠ AI removal not available: {e}")

        # Test auto method
        print("Testing auto method...")
        auto_result_path = service.process_icon(test_image, method="auto")
        print(f"✓ Auto removal result: {auto_result_path}")

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise

    finally:
        # Cleanup test files
        if os.path.exists(test_image):
            os.remove(test_image)
            print(f"Cleaned up: {test_image}")


if __name__ == "__main__":
    test_background_removal()
