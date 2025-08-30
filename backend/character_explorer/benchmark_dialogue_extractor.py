#!/usr/bin/env python3
"""
Benchmark script to compare old vs new dialogue extractor efficiency.
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.character_explorer.services.dialogue_extractor import (
    DialogueExtractorSliding,
)


def create_test_book():
    """Create a larger test book with various dialogue patterns."""
    chapters = []

    for i in range(1, 6):
        chapter = f"""
        CHAPTER {i}
        
        This is a chapter with some exposition and narrative description. The characters moved through the room, their footsteps echoing on the wooden floorboards.
        
        "Hello there," said Alice, looking up from her book.
        
        "Good afternoon," replied Bob, adjusting his glasses. "How are you today?"
        
        Alice smiled warmly. "I'm doing quite well, thank you for asking."
        
        "That's wonderful to hear," Bob said with genuine enthusiasm. "I was hoping to discuss the project we've been working on."
        
        "Of course," Alice replied, setting her book aside. "What's on your mind?"
        
        Bob leaned forward in his chair. "I think we might be approaching this from the wrong angle."
        
        "Interesting," Alice mused. "What makes you say that?"
        
        "Well," Bob began, "when I look at the data, it suggests a different interpretation entirely."
        
        Alice nodded thoughtfully. "I see what you mean. That could change everything."
        
        "Exactly," Bob said with a smile. "I'm glad you see it too."
        
        The conversation continued for some time, with both characters sharing their insights and observations about the project at hand.
        """
        chapters.append(chapter)

    return "\n\n".join(chapters)


def benchmark_extractor():
    """Benchmark the dialogue extractor performance."""

    print("Benchmarking DialogueExtractor Performance")
    print("=" * 60)

    # Create test book
    test_book = create_test_book()
    print(f"Test book size: {len(test_book)} characters")
    paragraphs = test_book.split("\n\n")
    print(f"Test book paragraphs: {len(paragraphs)}")

    # Count quotes in test book
    quote_count = test_book.count('"')
    print(f"Total quote marks: {quote_count}")

    extractor = DialogueExtractorSliding()

    print("\nRunning extraction...")
    start_time = time.time()

    try:
        results = extractor.extract(test_book)
        end_time = time.time()

        print(f"\nResults:")
        print(f"- Extraction time: {end_time - start_time:.2f} seconds")
        print(f"- Total dialogue entries extracted: {len(results)}")

        if results:
            print(f"- Sample entries:")
            for i, entry in enumerate(results[:3], 1):
                print(f"  {i}. {entry['character_name']}: \"{entry['quote'][:50]}...\"")

        # Calculate efficiency metrics
        paragraphs_with_quotes = len([p for p in test_book.split("\n\n") if '"' in p])
        print(f"\nEfficiency Metrics:")
        print(f"- Paragraphs with quotes: {paragraphs_with_quotes}")
        print(
            f"- LLM calls needed: {paragraphs_with_quotes} (vs processing entire book)"
        )
        print(
            f"- Estimated token reduction: ~{(len(test_book) - paragraphs_with_quotes * 200) / len(test_book) * 100:.1f}%"
        )

    except Exception as e:
        print(f"Error during extraction: {e}")


if __name__ == "__main__":
    benchmark_extractor()
