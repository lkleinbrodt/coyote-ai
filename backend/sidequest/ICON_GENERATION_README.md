# SideQuest Icon Generation System

This system generates consistent, on-brand icons for each quest category using AI image generation. It creates whimsical, cute mascots that represent each category with a consistent visual style.

## Features

- **Consistent Branding**: Each category has a specific mascot, prop, and color palette
- **Multi-Engine Support**: Generates prompts for DALL-E 3, Stable Diffusion, and Midjourney
- **Smart Prompt Crafting**: Extracts keywords from example quests to enhance prompts
- **Batch Generation**: Can generate icons for all categories at once

## Category Style Mapping

| Category    | Mascot    | Prop                  | Palette            |
| ----------- | --------- | --------------------- | ------------------ |
| Fitness     | Red Panda | Dumbbell/Jump Rope    | Lime Green + Teal  |
| Mindfulness | Koala     | Yoga Mat/Lotus        | Lavender + Mint    |
| Learning    | Owl       | Book/Glasses          | Royal Blue + Gold  |
| Chores      | Beaver    | Broom/Potted Plant    | Sage + Sand        |
| Social      | Capybara  | Heart/Envelope        | Peach + Rose       |
| Outdoors    | Otter     | Leaf/Water Bottle     | Emerald + Sky Blue |
| Creativity  | Cat       | Paintbrush/Guitar     | Magenta + Cyan     |
| Hobbies     | Fox       | Checklist/Alarm Clock | Orange + Cobalt    |

## Usage

### Generate Icons for All Categories

```bash
cd coyote-ai/backend/sidequest
python generate_icons.py
```

This will:

1. Generate prompts for each category using example quests
2. Create DALL-E 3 images for each category
3. Save icons to `icons/` directory with naming like `fitness_icon.png`

### Generate Icon for Specific Category

```python
from generate_icons import generate_icon_for_category
from sidequest.models import QuestCategory

# Generate icon for fitness category
filename = generate_icon_for_category(QuestCategory.FITNESS)
print(f"Generated: {filename}")
```

### Test Prompt Generation

```bash
python test_prompts.py
```

This tests the prompt generation logic without requiring database access or API calls.

## Prompt Structure

Each generated prompt follows this pattern:

```
cute, playful icon of a [mascot] with a [prop] inside a soft rounded badge;
cozy lighting, soft shading, clean silhouette, high readability at small size;
gradient background in [palette]; no text.
```

### Example Generated Prompts

**Fitness Category:**

```
cute, playful icon of a red panda with a dumbbell or jump rope inside a soft rounded badge;
cozy lighting, soft shading, clean silhouette, high readability at small size;
gradient background in lime green and teal; no text.
Friendly, charming, minimal composition. Focus on the single mascot and one prop.
Soft gradient badge, clean edges, high contrast. Avoid text, signatures, or logos.
actions: push-ups, stretch, walk; props: neighborhood, routine, shoulders
```

## Configuration

### Style Customization

Edit `CATEGORY_STYLE` in `generate_icons.py` to modify:

- Mascot animals
- Category props
- Color palettes

### Negative Prompts

The system uses consistent negative prompts to avoid:

- Text, watermarks, signatures
- Photorealistic or 3D renders
- Dark or creepy imagery
- Low quality or blurry results

### Engine Parameters

Each AI engine has optimized parameters:

**DALL-E 3:**

- Size: 1024x1024
- Quality: Standard
- Background: Transparent (if supported)

**Stable Diffusion:**

- Size: 1024x1024
- CFG Scale: 6.5
- Steps: 28
- Sampler: DPM++ 2M Karras

**Midjourney:**

- Aspect: 1:1
- Style: 4c
- Quality: High

## File Structure

```
sidequest/
├── generate_icons.py          # Main icon generation script
├── test_prompts.py            # Test script for prompts
├── ICON_GENERATION_README.md  # This documentation
└── icons/                     # Generated icons (created automatically)
    ├── fitness_icon.png
    ├── mindfulness_icon.png
    ├── learning_icon.png
    └── ...
```

## Requirements

- OpenAI API key (for DALL-E 3)
- Python 3.7+
- Required packages: `openai`, `requests`
- Database access (for quest examples)

## Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure `OPENAI_API_KEY` environment variable is set
2. **Database Connection**: Check database configuration and connectivity
3. **Permission Errors**: Ensure write permissions for `icons/` directory
4. **API Rate Limits**: DALL-E 3 has rate limits; add delays if needed

### Debug Mode

Enable debug output by modifying the main function:

```python
def main():
    app = create_app()
    with app.app_context():
        # Add debug logging
        import logging
        logging.basicConfig(level=logging.DEBUG)

        # ... rest of function
```

## Future Enhancements

- Support for additional AI image generators
- Custom style presets for different app themes
- Batch processing with progress bars
- Icon validation and quality checks
- Integration with design system tools

## Contributing

When adding new categories or modifying styles:

1. Update `CATEGORY_STYLE` mapping
2. Add corresponding test cases
3. Update this documentation
4. Test prompt generation for new categories

## License

This system is part of the SideQuest backend and follows the same licensing terms.
