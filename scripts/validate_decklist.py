#!/usr/bin/env python3
"""
MTG Decklist Validator

Validates a decklist.txt against the cards_by_category/ database.
Ensures all cards are Standard-legal by checking presence in the CSV files.

Usage:
    python scripts/validate_decklist.py <path_to_decklist.txt>
    python scripts/validate_decklist.py Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --quiet Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --verbose Decks/my_deck/decklist.txt

Exit codes:
    0  Validation passed
    1  Illegal / unrecognised cards found
    2  Input file not found
    3  Deck count error (wrong mainboard/sideboard/copy count)
"""

import argparse
import csv
import difflib
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from mtg_utils import parse_decklist

CARD_TYPES = [
    'artifact', 'battle', 'creature', 'enchantment', 'instant',
    'land', 'other', 'planeswalker', 'sorcery',
]

BASIC_LAND_NAMES = {
    'plains', 'island', 'swamp', 'mountain', 'forest',
    'wastes', 'snow-covered plains', 'snow-covered island',
    'snow-covered swamp', 'snow-covered mountain', 'snow-covered forest',
}


class DecklistValidator:
    """Validates a decklist against the cards_by_category/ CSV database."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.card_database: Dict[str, Dict] = {}
        self._load_database()

    def _load_database(self) -> None:
        cards_dir = self.repo_root / "cards_by_category"
        if not cards_dir.exists():
            logging.error("Card database directory not found: %s", cards_dir)
            sys.exit(2)
        logging.info("Loading card database from %s ...", cards_dir)
        seen: set = set()
        for card_type in CARD_TYPES:
            type_dir = cards_dir / card_type
            if not type_dir.exists():
                continue
            for csv_file in sorted(type_dir.glob('*.csv')):
                try:
                    with open(csv_file, encoding='utf-8') as f:
                        for row in csv.DictReader(f):
                            raw_name = row.get('name', '').strip()
                            key = raw_name.lower()
                            if key and key not in seen:
                                seen.add(key)
                                self.card_database[key] = {
                                    'name': raw_name,
                                    'file': str(csv_file.relative_to(self.repo_root)),
                                    'set': row.get('set', ''),
                                    'type_line': row.get('type_line', ''),
                                }
                except Exception as exc:
                    logging.warning("Could not read %s: %s", csv_file, exc)
        logging.info("Loaded %d unique card names.", len(self.card_database))

    def _lookup(self, card_name: str) -> Tuple[bool, str]:
        entry = self.card_database.get(card_name.lower())
        if entry:
            return True, entry['file']
        return False, ''

    def _suggest(self, card_name: str, n: int = 3) -> List[str]:
        return difflib.get_close_matches(
            card_name.lower(), self.card_database.keys(), n=n, cutoff=0.75
        )

    def _validate_counts(
        self,
        mainboard: List[Tuple[int, str]],
        sideboard: List[Tuple[int, str]],
    ) -> List[str]:
        errors: List[str] = []
        main_total = sum(q for q, _ in mainboard)
        side_total = sum(q for q, _ in sideboard)
        if main_total != 60:
            errors.append(f"Mainboard has {main_total} cards (expected 60).")
        if sideboard and side_total != 15:
            errors.append(f"Sideboard has {side_total} cards (expected 15 or 0).")
        copy_counts: Dict[str, int] = {}
        for qty, name in mainboard + sideboard:
            if name.lower() not in BASIC_LAND_NAMES:
                copy_counts[name] = copy_counts.get(name, 0) + qty
        for name, total in copy_counts.items():
            if total > 4:
                errors.append(f"'{name}' appears {total} times (max 4 for non-basic lands).")
        return errors

    def validate(self, decklist_path: Path, verbose: bool = False) -> int:
        if not decklist_path.exists():
            logging.error("Decklist not found: %s", decklist_path)
            return 2
        print(f"Validating: {decklist_path}")
        print("=" * 70)
        mainboard, sideboard = parse_decklist(decklist_path)
        illegal: List[Tuple[int, str, str]] = []

        print("\n\U0001f4cb MAINBOARD VALIDATION\n")
        for qty, name in mainboard:
            found, src = self._lookup(name)
            if found:
                if verbose:
                    print(f"  \u2713 {qty}x {name}")
                    print(f"     \u2514\u2500 {src}")
                else:
                    print(f"  \u2713 {qty}x {name}")
            else:
                print(f"  \u274c {qty}x {name} \u2014 NOT FOUND IN DATABASE")
                suggestions = self._suggest(name)
                if suggestions:
                    print(f"     Did you mean: {', '.join(suggestions)}?")
                illegal.append((qty, name, 'mainboard'))

        if sideboard:
            print("\n\U0001f4cb SIDEBOARD VALIDATION\n")
            for qty, name in sideboard:
                found, src = self._lookup(name)
                if found:
                    if verbose:
                        print(f"  \u2713 {qty}x {name}")
                        print(f"     \u2514\u2500 {src}")
                    else:
                        print(f"  \u2713 {qty}x {name}")
                else:
                    print(f"  \u274c {qty}x {name} \u2014 NOT FOUND IN DATABASE")
                    suggestions = self._suggest(name)
                    if suggestions:
                        print(f"     Did you mean: {', '.join(suggestions)}?")
                    illegal.append((qty, name, 'sideboard'))

        count_errors = self._validate_counts(mainboard, sideboard)

        print("\n" + "=" * 70)
        print("\n\U0001f4ca VALIDATION SUMMARY\n")
        print(f"  Mainboard : {sum(q for q, _ in mainboard)} cards ({len(mainboard)} unique entries)")
        if sideboard:
            print(f"  Sideboard : {sum(q for q, _ in sideboard)} cards")

        if count_errors:
            print("\n\u26a0\ufe0f  COUNT VIOLATIONS\n")
            for err in count_errors:
                print(f"  \u2022 {err}")

        if illegal:
            print(f"\n\u274c VALIDATION FAILED\n")
            print(f"  Found {len(illegal)} unrecognised card(s):\n")
            for qty, name, section in illegal:
                print(f"  \u2022 {qty}x {name} ({section})")
            print("\n  These cards are either rotated or not present in the database.\n")
            return 1

        if count_errors:
            return 3

        print("\n\u2705 VALIDATION PASSED\n")
        print("  All cards are legal and present in the database.\n")
        return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate an MTG decklist against the cards_by_category/ database."
    )
    p.add_argument("decklist", help="Path to decklist.txt")
    p.add_argument("--quiet", action="store_true", help="Only print summary")
    p.add_argument("--verbose", action="store_true", help="Print source CSV for each card")
    return p


def main() -> None:
    args = _build_parser().parse_args()
    log_level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    decklist_path = Path(args.decklist)
    if not decklist_path.is_absolute():
        decklist_path = repo_root / decklist_path
    validator = DecklistValidator(repo_root)
    sys.exit(validator.validate(decklist_path, verbose=args.verbose))


if __name__ == "__main__":
    main()
