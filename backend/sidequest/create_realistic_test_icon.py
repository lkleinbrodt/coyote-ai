"""
Create a realistic test icon that simulates DALL-E output
with theme colors, gradients, and a central logo
"""

from PIL import Image, ImageDraw, ImageFilter
import numpy as np


def create_realistic_test_icon():
    """Create a test icon that looks like DALL-E output"""
    # Create a 1024x1024 image (like DALL-E output)
    size = 1024
    img = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(img)

    # Create a gradient background (like your theme colors)
    # Start with lime green and teal (fitness theme)
    for y in range(size):
        # Create gradient from top to bottom
        r = int(50 + (y / size) * 100)  # Green component
        g = int(200 + (y / size) * 50)  # Lime green
        b = int(150 + (y / size) * 100)  # Teal
        color = (r, g, b)

        # Draw horizontal line with this color
        draw.line([(0, y), (size, y)], fill=color)

    # Add some texture/variation to make it more realistic
    for _ in range(1000):
        x = np.random.randint(0, size)
        y = np.random.randint(0, size)
        # Add slight color variations
        pixel_color = img.getpixel((x, y))
        variation = np.random.randint(-20, 20)
        new_color = tuple(max(0, min(255, c + variation)) for c in pixel_color)
        draw.point((x, y), fill=new_color)

    # Draw a central logo (red panda with dumbbell)
    center = size // 2

    # Draw a circular badge background
    badge_radius = 300
    badge_center = (center, center)

    # Create badge with slight transparency effect
    badge_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge_img)

    # Draw badge circle with gradient
    for r in range(badge_radius, 0, -1):
        alpha = int(255 * (1 - (badge_radius - r) / badge_radius))
        color = (255, 255, 255, alpha)
        badge_draw.ellipse(
            [
                badge_center[0] - r,
                badge_center[1] - r,
                badge_center[0] + r,
                badge_center[1] + r,
            ],
            fill=color,
            outline=(200, 200, 200, alpha),
        )

    # Composite badge onto main image
    img = Image.alpha_composite(img.convert("RGBA"), badge_img)

    # Draw the red panda (simplified as colored shapes)
    # Body
    body_radius = 120
    draw.ellipse(
        [
            center - body_radius,
            center - body_radius + 20,
            center + body_radius,
            center + body_radius + 20,
        ],
        fill=(139, 69, 19),
    )  # Brown

    # Head
    head_radius = 80
    draw.ellipse(
        [
            center - head_radius,
            center - head_radius - 40,
            center + head_radius,
            center + head_radius - 40,
        ],
        fill=(139, 69, 19),
    )  # Brown

    # Ears
    ear_radius = 25
    draw.ellipse(
        [
            center - head_radius - 10,
            center - head_radius - 80,
            center - head_radius + 10,
            center - head_radius - 30,
        ],
        fill=(139, 69, 19),
    )  # Brown
    draw.ellipse(
        [
            center + head_radius - 10,
            center - head_radius - 80,
            center + head_radius + 10,
            center - head_radius - 30,
        ],
        fill=(139, 69, 19),
    )  # Brown

    # Eyes
    eye_radius = 15
    draw.ellipse(
        [
            center - 30,
            center - head_radius - 20,
            center - 30 + eye_radius,
            center - head_radius - 20 + eye_radius,
        ],
        fill=(255, 255, 255),
    )  # White
    draw.ellipse(
        [
            center + 30 - eye_radius,
            center - head_radius - 20,
            center + 30,
            center - head_radius - 20 + eye_radius,
        ],
        fill=(255, 255, 255),
    )  # White

    # Pupils
    pupil_radius = 8
    draw.ellipse(
        [
            center - 30 + 3,
            center - head_radius - 20 + 3,
            center - 30 + 3 + pupil_radius,
            center - head_radius - 20 + 3 + pupil_radius,
        ],
        fill=(0, 0, 0),
    )  # Black
    draw.ellipse(
        [
            center + 30 - pupil_radius - 3,
            center - head_radius - 20 + 3,
            center + 30 - 3,
            center - head_radius - 20 + 3 + pupil_radius,
        ],
        fill=(0, 0, 0),
    )  # Black

    # Dumbbell
    bar_length = 200
    bar_width = 20
    weight_radius = 50

    # Draw bar
    draw.rectangle(
        [
            center - bar_length // 2,
            center + 60,
            center + bar_length // 2,
            center + 60 + bar_width,
        ],
        fill=(128, 128, 128),
    )  # Gray

    # Draw weights
    draw.ellipse(
        [
            center - bar_length // 2 - weight_radius,
            center + 60 - weight_radius // 2,
            center - bar_length // 2 + weight_radius,
            center + 60 + bar_width + weight_radius // 2,
        ],
        fill=(192, 192, 192),
    )  # Light gray
    draw.ellipse(
        [
            center + bar_length // 2 - weight_radius,
            center + 60 - weight_radius // 2,
            center + bar_length // 2 + weight_radius,
            center + 60 + bar_width + weight_radius // 2,
        ],
        fill=(192, 192, 192),
    )  # Light gray

    # Add some final touches - slight blur to make it more realistic
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # Save the test icon
    test_path = "realistic_test_icon.png"
    img.save(test_path)
    print(f"Created realistic test icon: {test_path}")

    return test_path


if __name__ == "__main__":
    create_realistic_test_icon()
