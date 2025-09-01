# Background Removal Service

This service automatically removes unwanted backgrounds from AI-generated icons, creating clean, transparent PNG files perfect for app use.

## Features

- **Multiple Removal Methods**: Simple color-based removal and AI-powered removal
- **Automatic Fallback**: Tries AI method first, falls back to simple method if needed
- **Batch Processing**: Process entire directories of icons at once
- **Edge Enhancement**: Smooths edges and enhances transparency
- **Smart Background Detection**: Automatically identifies background colors from image edges

## Installation

1. Install required dependencies:

```bash
pip install -r requirements_background_removal.txt
```

2. For best results, install the AI-powered rembg library:

```bash
pip install rembg
```

## Usage

### Basic Usage

```python
from background_removal import BackgroundRemovalService

# Initialize service
service = BackgroundRemovalService(output_dir="icons_processed")

# Process a single icon
result_path = service.process_icon("icons/fitness/fitness_1.png", method="auto")
```

### Batch Processing

```python
# Process all icons in a category
processed_files = service.batch_process("icons/fitness", method="auto")
```

### Available Methods

- **`simple`**: Color-based background removal (fast, good for solid backgrounds)
- **`ai`**: AI-powered removal using rembg (best quality, slower)
- **`auto`**: Automatically chooses the best method (recommended)

## Integration with Icon Generation

Use the enhanced script to generate icons and automatically remove backgrounds:

```bash
cd coyote-ai/backend/sidequest
python generate_icons_with_background_removal.py
```

This will:

1. Generate icons using your existing DALL-E prompts
2. Automatically remove backgrounds from all generated icons
3. Save clean, transparent versions to `icons_processed/`

## Testing

Test the service with a simple test image:

```bash
python test_background_removal.py
```

## How It Works

### Simple Background Removal

1. Analyzes edge colors to identify background
2. Creates a mask for similar colors
3. Sets alpha channel to create transparency
4. Best for solid color or simple gradient backgrounds

### AI Background Removal

1. Uses the `rembg` library with pre-trained deep learning models
2. Automatically detects foreground objects
3. Creates precise masks around complex shapes
4. Handles complex backgrounds and similar colors

### Edge Enhancement

1. Applies slight Gaussian blur to smooth edges
2. Enhances contrast for better visibility
3. Creates professional-looking transparent icons

## Output

- **Original icons**: `icons/` (with backgrounds)
- **Processed icons**: `icons_processed/` (transparent backgrounds)
- **File naming**: `{category}_{number}_transparent.png`

## Troubleshooting

### Common Issues

1. **"rembg not installed"**: Install with `pip install rembg` for best results
2. **Poor quality simple removal**: Try the AI method instead
3. **Memory issues with large images**: Process images individually rather than in batch

### Performance Tips

- Use `method="simple"` for quick processing of many icons
- Use `method="ai"` for highest quality results
- Process in smaller batches if memory is limited

## Customization

You can adjust the color tolerance in the simple removal method:

```python
# Lower tolerance = more aggressive background removal
# Higher tolerance = more conservative (keeps more of the image)
service._create_color_mask(data, target_colors, tolerance=20)  # More aggressive
service._create_color_mask(data, target_colors, tolerance=50)  # More conservative
```

## Future Enhancements

- Support for more image formats
- Custom background color specification
- Batch processing with progress bars
- Integration with image generation APIs
- Quality assessment and automatic retry
