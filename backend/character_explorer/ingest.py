import json
import random

import click
from flask.cli import with_appcontext

from backend.extensions import db
from backend.src.OpenRouter import OpenRouterClient

from .models import Book, Character, Quote
from .services.dialogue_extractor import DialogueExtractorSliding
from .services.embedding_service import EmbeddingService


def extract_book_metadata(book_text: str) -> dict:
    """Extract book title and author from the first 50 lines using LLM."""
    llm_client = OpenRouterClient()
    model = "anthropic/claude-3-haiku"

    # Get first 50 lines
    first_lines = "\n".join(book_text.split("\n")[:50])

    prompt = f"""
    You are a literary metadata expert. Extract the book title and author from the following text.
    The text is likely from the beginning of a book and may contain Project Gutenberg headers, title pages, etc.
    
    Return ONLY a valid JSON object with "title" and "author" keys. Do not include any other text.
    
    Example format:
    {{"title": "Emma", "author": "Jane Austen"}}
    
    Text to analyze:
    ---
    {first_lines}
    ---
    """

    try:
        messages = [{"role": "user", "content": prompt}]
        response = llm_client.chat(messages, model=model)

        # Clean and parse the JSON response
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:-3].strip()
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:-3].strip()

        metadata = json.loads(cleaned_response)

        # Validate required fields
        if "title" not in metadata or "author" not in metadata:
            raise ValueError("Missing required fields in metadata")

        return metadata

    except Exception as e:
        print(f"Error extracting metadata: {e}")
        print(f"Raw response: {response[:500]}")
        return None


@click.command("ingest-book")
@click.argument("filepath")
@click.option("--title", help="Override the extracted title.")
@click.option("--author", help="Override the extracted author.")
@click.option("--force", is_flag=True, help="Force re-ingestion even if book exists.")
@with_appcontext
def ingest_book_command(filepath, title, author, force):
    """
    Processes a book from a text file, extracts dialogue, generates embeddings,
    and populates the database.

    Usage: flask ingest-book /path/to/book.txt
    """
    click.echo(f"Starting ingestion from {filepath}...")

    # Initialize services
    dialogue_extractor = DialogueExtractorSliding()
    embedding_service = EmbeddingService()

    # Read book text with proper UTF-8 encoding
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            book_text = f.read()
    except FileNotFoundError:
        click.echo(f"Error: File not found at {filepath}")
        return
    except UnicodeDecodeError as e:
        click.echo(f"Error: Could not decode file with UTF-8 encoding: {e}")
        click.echo("Trying with different encoding...")
        try:
            with open(filepath, "r", encoding="latin-1") as f:
                book_text = f.read()
        except Exception as e2:
            click.echo(f"Error: Could not read file with any encoding: {e2}")
            return

    # Extract metadata if not provided
    if not title or not author:
        click.echo("Extracting book metadata...")
        metadata = extract_book_metadata(book_text)

        if not metadata:
            click.echo(
                "Error: Could not extract book metadata. Please provide --title and --author manually."
            )
            return

        title = title or metadata["title"]
        author = author or metadata["author"]
        click.echo(f"Extracted: '{title}' by {author}")

    # Check if book already exists
    book = Book.query.filter_by(title=title, author=author).first()
    if book and not force:
        click.echo(
            f"Book '{title}' already exists in the database. Use --force to re-ingest."
        )
        return
    elif book and force:
        click.echo(f"Re-ingesting existing book '{title}'...")
        # Delete existing data
        db.session.delete(book)
        db.session.commit()

    book = Book(title=title, author=author)
    db.session.add(book)
    db.session.commit()  # Commit to get book.id

    click.echo("Extracting dialogue... (this may take a while)")
    dialogues = dialogue_extractor.extract(book_text)

    if not dialogues:
        click.echo("No dialogue could be extracted. Aborting.")
        db.session.delete(book)
        db.session.commit()
        return

    # Log a sample of extracted dialogue occasionally
    if random.random() < 0.5:  # 50% chance to show sample
        click.echo(
            f"\n=== Sample of extracted dialogue ({len(dialogues)} total entries) ==="
        )
        sample_size = min(5, len(dialogues))
        sample_dialogues = random.sample(dialogues, sample_size)

        for i, dialogue in enumerate(sample_dialogues, 1):
            character = dialogue.get("character_name", "Unknown")
            quote = dialogue.get("quote", "")
            if len(quote) > 80:
                quote = quote[:77] + "..."
            click.echo(f'{i}. {character}: "{quote}"')
        click.echo("=" * 50)

    click.echo(f"Extracted {len(dialogues)} dialogue entries. Processing characters...")

    # Group quotes by character
    character_quotes = {}
    for item in dialogues:
        name = item["character_name"]
        quote = item["quote"]
        if name not in character_quotes:
            character_quotes[name] = []
        character_quotes[name].append(quote)

    click.echo(
        f"Found {len(character_quotes)} unique characters. Generating embeddings and saving..."
    )

    total_characters = 0
    for name, quotes_list in character_quotes.items():
        if len(quotes_list) < 5:  # Skip characters with too few quotes
            continue

        # Create Character
        character = Character(book_id=book.id, name=name, total_quotes=len(quotes_list))
        db.session.add(character)
        db.session.flush()  # Flush to get character.id

        # Generate and save quotes with their embeddings
        for quote_text in quotes_list:
            quote_embedding = embedding_service.generate_quote_embedding(quote_text)
            quote = Quote(
                character_id=character.id,
                text=quote_text,
                embedding=quote_embedding,
                word_count=len(quote_text.split()),
            )
            db.session.add(quote)

        # Generate and save character embedding (centroid of their quotes)
        character.embedding = embedding_service.generate_character_embedding(
            quotes_list
        )
        total_characters += 1

        # Occasionally log a sample quote from this character
        if random.random() < 0.3:  # 30% chance to show a sample quote
            sample_quote = random.choice(quotes_list)
            if len(sample_quote) > 60:
                sample_quote = sample_quote[:57] + "..."
            click.echo(
                f'  - Processed {name} with {len(quotes_list)} quotes. Sample: "{sample_quote}"'
            )
        else:
            click.echo(f"  - Processed {name} with {len(quotes_list)} quotes.")

    # Update book with final character count and commit all changes
    book.total_characters = total_characters
    db.session.commit()
    click.echo(f"Successfully ingested '{title}' with {total_characters} characters.")
