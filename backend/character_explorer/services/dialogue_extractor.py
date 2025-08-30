"""
dialogue_extractor_sliding.py
────────────────────────────────────────────────────────
Sliding-window dialogue extractor for classic prose.

Changes from the paragraph-based version:
• The LLM now receives the **entire window** (2 000-char default).
• Windows slide forward by 1 500 chars (configurable).
• If a window ends inside an open quote, it is **extended** to include the
  closing quote so the model never sees an unterminated string.
• No per-paragraph pre-filtering – the LLM extracts **all** dialogue lines
  it finds in the window.
• De-duplication across windows unchanged.

Requires:
    pip install nltk
    # plus whatever your OpenRouter client depends on
"""

from __future__ import annotations

import json
import logging
import re
from typing import Dict, List, Set, Tuple

import nltk

from backend.src.OpenRouter import OpenRouterClient  # adjust import path if needed

# ─── configuration ────────────────────────────────────────────────────
WINDOW_CHARS = 500  # size of each text slice
STEP_CHARS = 250  # slide amount
MODEL_NAME = "openai/gpt-4o-mini"

# ─── logging setup ───────────────────────────────────────────────────
logger = logging.getLogger(__name__)
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

# To enable debug logging, set: logging.getLogger(__name__).setLevel(logging.DEBUG)

# ─── helpers ─────────────────────────────────────────────────────────


def collapse_soft_breaks(txt: str) -> str:
    """Join single line-breaks inside paragraphs but keep blank lines."""
    return re.sub(r"(?<!\n)\n(?!\n)", " ", txt)


def window_iter(text: str, size: int = WINDOW_CHARS, step: int = STEP_CHARS):
    """Yield (slice_text, start_offset)."""
    for start in range(0, len(text), step):
        yield text[start : start + size], start


# ─── extractor class ─────────────────────────────────────────────────


class DialogueExtractorSliding:
    """Sliding-window dialogue extractor."""

    def __init__(self):
        logger.info(f"Initializing DialogueExtractorSliding with model: {MODEL_NAME}")
        self.llm_client = OpenRouterClient()
        self.model = MODEL_NAME

        # stop-word list for junk filtering (unchanged)
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            logger.info("Downloading NLTK stopwords...")
            nltk.download("stopwords")
        self.stopwords = set(nltk.corpus.stopwords.words("english"))
        logger.debug(f"Loaded {len(self.stopwords)} stopwords for filtering")

        # curly → straight quote map
        self.quote_map = {
            "\u201c": '"',
            "\u201d": '"',
            "\u2018": "'",
            "\u2019": "'",
            "«": '"',
            "»": '"',
            "„": '"',
        }
        logger.debug("Initialized quote normalization map")

    # ─── preprocessing ────────────────────────────────────────────
    def _normalise(self, txt: str) -> str:
        original_len = len(txt)
        normalized = collapse_soft_breaks(txt.translate(str.maketrans(self.quote_map)))
        logger.debug(f"Normalized text: {original_len} -> {len(normalized)} chars")
        return normalized

    # ─── quote hygiene ────────────────────────────────────────────
    @staticmethod
    def _window_ends_in_open_quote(slice_txt: str) -> bool:
        """Return True if there is an unmatched double quote in slice."""
        return slice_txt.count('"') % 2 == 1

    @staticmethod
    def _window_has_quotes(slice_txt: str) -> bool:
        """Return True if the window contains any quotation marks."""
        return '"' in slice_txt or "'" in slice_txt

    # ─── junk filtering ───────────────────────────────────────────
    def _junk_quote(self, quote: str) -> bool:
        tokens = quote.lower().split()
        if len(tokens) < 3:
            logger.debug(
                f"Junk filter: Quote too short ({len(tokens)} tokens): '{quote[:50]}...'"
            )
            return True
        sw_ratio = sum(t in self.stopwords for t in tokens) / len(tokens)
        is_junk = sw_ratio > 0.8
        if is_junk:
            logger.debug(
                f"Junk filter: High stopword ratio ({sw_ratio:.2f}): '{quote[:50]}...'"
            )
        return is_junk

    # ─── LLM call ────────────────────────────────────────────────
    def _call_llm(self, window_text: str) -> List[Dict[str, str]]:
        prompt = (
            f"""
Extract ONLY dialogue lines that are explicitly enclosed in quotation marks ("" or '') from the following text. For each quoted dialogue line, identify the speaker.

IMPORTANT: Only extract text that is actually surrounded by quotation marks. If text is not enclosed in quotes, it is NOT dialogue and should be ignored.

If you cannot identify the speaker, set \"character_name\" to \"Unknown\".
Return ONLY JSON following this exact schema:
{{
  \"dialogue_entries\": [
    {{\"character_name\": <string>, \"quote\": <string>}},
    ...
  ]
}}

TEXT:
"""
            + window_text
        )

        messages = [{"role": "user", "content": prompt}]
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "dialogue_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "dialogue_entries": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "character_name": {"type": "string"},
                                    "quote": {"type": "string"},
                                },
                                "required": ["character_name", "quote"],
                                "additionalProperties": False,
                            },
                        }
                    },
                    "required": ["dialogue_entries"],
                    "additionalProperties": False,
                },
            },
        }

        logger.debug(f"LLM call: Sending {len(window_text)} chars to {self.model}")
        logger.debug(f"LLM prompt preview: {prompt[:200]}...")

        try:
            raw = self.llm_client.chat(
                messages, model=self.model, response_format=response_format
            )
            logger.debug(f"LLM response preview: {raw[:200]}...")

            parsed = json.loads(raw).get("dialogue_entries", [])
            logger.debug(f"LLM parsed {len(parsed)} dialogue entries")

            if parsed:
                logger.debug(f"LLM sample entries: {parsed[:2]}")

            return parsed
        except Exception as e:
            logger.warning(f"LLM call failed or returned invalid JSON: {e}")
            logger.debug(
                f"LLM raw response: {raw[:500] if 'raw' in locals() else 'No response'}"
            )
            return []

    # ─── public API ──────────────────────────────────────────────
    def extract(
        self, raw_text: str, output_file: str = "dialogue_output.json"
    ) -> List[Dict[str, str]]:
        logger.info(f"Starting dialogue extraction from {len(raw_text)} characters")
        text = self._normalise(raw_text)
        logger.debug(f"Normalized text length: {len(text)} characters")

        results: List[Dict[str, str]] = []
        seen: Set[Tuple[str, str]] = set()

        # Calculate total windows for progress tracking
        total_windows = (len(text) + STEP_CHARS - 1) // STEP_CHARS
        logger.info(
            f"Processing {total_windows} windows (size: {WINDOW_CHARS}, step: {STEP_CHARS})"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

        window_count = 0
        total_entries_found = 0
        total_entries_kept = 0

        for slice_txt, start in window_iter(text):
            window_count += 1

            # extend window if it ends in the middle of a quote
            original_slice_len = len(slice_txt)
            if self._window_ends_in_open_quote(slice_txt):
                end = start + len(slice_txt)
                next_quote = text.find('"', end)
                if next_quote != -1:
                    slice_txt = text[start : next_quote + 1]
                    logger.debug(
                        f"Window {window_count}: Extended from {original_slice_len} to {len(slice_txt)} chars to close quote"
                    )

            # Skip windows that don't contain any quotation marks
            if not self._window_has_quotes(slice_txt):
                logger.debug(
                    f"Window {window_count}/{total_windows}: Skipping window at position {start} - no quotation marks found"
                )
                continue

            logger.debug(
                f"Window {window_count}/{total_windows}: Processing slice at position {start} ({len(slice_txt)} chars)"
            )
            logger.debug(f"Window {window_count} preview: {slice_txt[:100]}...")

            entries = self._call_llm(slice_txt)
            total_entries_found += len(entries)

            window_kept = 0
            for entry in entries:
                speaker = entry.get("character_name", "").strip()
                quote = entry.get("quote", "").strip()
                if not speaker or self._junk_quote(quote):
                    logger.debug(
                        f"Window {window_count}: Filtered out '{speaker}': '{quote[:50]}...'"
                    )
                    continue
                key = (speaker, quote)
                if key in seen:
                    logger.debug(
                        f"Window {window_count}: Duplicate entry for '{speaker}'"
                    )
                    continue
                seen.add(key)
                results.append({"character_name": speaker, "quote": quote})
                window_kept += 1

            if window_kept > 0:
                logger.debug(
                    f"Window {window_count}: Kept {window_kept}/{len(entries)} entries"
                )
            total_entries_kept += window_kept

            # Log progress every 10 windows or at the end
            if window_count % 10 == 0 or window_count == total_windows:
                logger.info(
                    f"Progress: {window_count}/{total_windows} windows processed, {total_entries_kept} unique entries found"
                )

        # write final deduplicated list once
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(
            f"Extraction complete: {total_entries_found} total entries found, {len(results)} unique entries kept"
        )
        logger.info(f"Results saved to {output_file}")
        return results


# ─── convenience CLI ───────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    import pathlib

    # parser = argparse.ArgumentParser(description="Extract dialogue from a text file.")
    # parser.add_argument("input", type=pathlib.Path, help="Path to .txt source file")
    # parser.add_argument(
    #     "-o",
    #     "--output",
    #     type=pathlib.Path,
    #     default="dialogue_output.json",
    #     help="Path for JSON output",
    # )
    # parser.add_argument(
    #     "--window", type=int, default=WINDOW_CHARS, help="Window size in characters"
    # )
    # parser.add_argument(
    #     "--step", type=int, default=STEP_CHARS, help="Step size in characters"
    # )
    # args = parser.parse_args()
    # raw = args.input.read_text(encoding="utf-8")
    from backend.config import Config

    book_dir = Config.ROOT_DIR / "backend" / "data" / "books"
    book_path = book_dir / "emma_short.txt"
    raw = book_path.read_text(encoding="utf-8")

    extractor = DialogueExtractorSliding()
    data = extractor.extract(raw, output_file="emma_short_dialogue_output.json")
    print(
        f"Extracted {len(data)} unique dialogue lines → emma_short_dialogue_output.json"
    )
