#!/usr/bin/env python3
"""
Offline Persian ↔ English Translator.
Uses a JSON dictionary file for translations and provides interactive, 
prefix, and fuzzy search modes.
"""

import argparse
import json
import readline
import sys
from difflib import get_close_matches
from pathlib import Path

# Default dictionary location
DICT_FILE = "/sdcard/isaac/dic.json"


def load_dictionary(path: Path):
    """
    Loads the Persian-English dictionary from a JSON file.
    Returns two dictionaries: Persian-to-English and English-to-Persian.
    """
    if not path.exists():
        # Fallback to a local path if the absolute one fails
        local_path = Path(__file__).parent / "dic.json"
        if local_path.exists():
            path = local_path
        else:
            print(f"Error: {path} not found", file=sys.stderr)
            sys.exit(1)

    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading dictionary: {e}", file=sys.stderr)
        sys.exit(1)

    fa_en = {str(k).strip(): str(v).strip() for k, v in data.items()}
    en_fa = {v: k for k, v in fa_en.items()}
    return fa_en, en_fa


def setup_readline(words):
    """
    Configures readline for tab completion using the provided word list.
    """
    words = sorted(words)

    def completer(text, state):
        matches = [w for w in words if w.startswith(text)]
        return matches[state] if state < len(matches) else None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims(" \t\n")


def translate(word, fa_en, en_fa):
    """
    Translates a word by checking both Persian-to-English and English-to-Persian dictionaries.
    """
    return fa_en.get(word) or en_fa.get(word)


def prefix_search(prefix, all_words):
    """
    Returns a sorted list of words that start with the given prefix.
    """
    return sorted(w for w in all_words if w.startswith(prefix))


def fuzzy_search(word, all_words, limit=5, cutoff=0.6):
    """
    Finds close matches for a word in the dictionary.
    """
    return get_close_matches(word, all_words, n=limit, cutoff=cutoff)


def interactive_mode(fa_en, en_fa):
    """
    Runs the translator in an interactive loop.
    """
    all_words = set(fa_en) | set(en_fa)
    setup_readline(all_words)

    print("Offline Persian ↔ English Translator")
    print("TAB for suggestions, Ctrl+C to exit\n")

    while True:
        try:
            word = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if not word:
            continue

        result = translate(word, fa_en, en_fa)
        if result:
            print(result)
        else:
            matches = fuzzy_search(word, all_words, limit=3)
            if matches:
                print(f"Not found. Did you mean: {', '.join(matches)}?")
            else:
                print("Not found")


def main():
    """
    Main entry point. Parses arguments and dispatches to the appropriate mode.
    """
    parser = argparse.ArgumentParser(description="Offline Persian ↔ English translator")
    parser.add_argument("word", nargs="*", help="Word to translate")
    parser.add_argument("--prefix", help="List words starting with prefix")
    parser.add_argument("--fuzzy", help="Fuzzy search (typo tolerant)")
    parser.add_argument("--dict", help="Path to dictionary JSON file")

    args = parser.parse_args()

    dict_path = Path(args.dict) if args.dict else Path(DICT_FILE)
    fa_en, en_fa = load_dictionary(dict_path)
    all_words = set(fa_en) | set(en_fa)

    if args.prefix:
        matches = prefix_search(args.prefix, all_words)
        if matches:
            print("\n".join(matches))
            sys.exit(0)
        print("No matches", file=sys.stderr)
        sys.exit(1)

    if args.fuzzy:
        matches = fuzzy_search(args.fuzzy, all_words)
        if matches:
            print("\n".join(matches))
            sys.exit(0)
        print("No close matches", file=sys.stderr)
        sys.exit(1)

    if args.word:
        word = " ".join(args.word).strip()
        result = translate(word, fa_en, en_fa)
        if result:
            print(result)
            sys.exit(0)
        print("Not found", file=sys.stderr)
        sys.exit(1)

    interactive_mode(fa_en, en_fa)


if __name__ == "__main__":
    main()
