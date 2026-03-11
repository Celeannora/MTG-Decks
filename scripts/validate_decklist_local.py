#!/usr/bin/env python3
"""
MTG Decklist Validator (Local / Offline Mode)

Fast offline validation using the pre-built local database.
Uses card_index.json pointer system for instant lookups without loading CSVs.

Usage:
    # First, build the local database (one-time setup)
    python scripts/build_local_database.py

    # Then validate decks offline
    python scripts/validate_decklist_local.py Decks/my_deck/decklist.txt
    python scripts/validate_decklist_local.py --sqlite Decks/my_deck/decklist.txt
    python scripts/validate_decklist_local.py --quiet Decks/my_deck/decklist.txt

Exit codes:
    0  Validation passed
    1  Illegal / unrecognised cards found
    2  Input file or database not found
    3  Deck count error
"""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from mtg_utils import parse_decklist

BASIC_LAND_NAMES = {
    'plains', 'island', 'swamp', 'mountain', 'forest',
    'wastes', 'snow-covered plains', 'snow-covered island',
    'snow-covered swamp', 'snow-covered mountain', 'snow-covered forest',
}


class LocalDecklistValidator:
    """Offline decklist validator backed by local_db/."""

    def __init__(self, repo_root: Path, use_sqlite: bool = False) -> None:
        self.repo_root = repo_root
        self.local_db_dir = repo_root / "local_db"
        self.use_sqlite = use_sqlite
        # Always initialise card_index so both code paths share the same lookup
        self.card_index: Dict[str, Dict] = {}
        self.total_cards = 0

        if use_sqlite:
            self._load_sqlite_db()
        else:
            self._load_json_index()

    # ------------------------------------------------------------------
    # Database loading
    # ------------------------------------------------------------------

    def _load_json_index(self) -> None:
        index_file = self.local_db_dir / "card_index.json"
        if not index_file.exists():
            logging.error(
                "Local database not found: %s\n"
                "Build it first with: python scripts/build_local_database.py",
                index_file,
            )
            sys.exit(2)
        logging.info("Loading local JSON index...")
        with open(index_file, encoding='utf-8') as f:
            data = json.load(f)
        self.card_index = data['cards']
        self.total_cards = data['total_cards']
        logging.info("Loaded %d cards from JSON index.", self.total_cards)

    def _load_sqlite_db(self) -> None:
        db_file = self.local_db_dir / "card_details.db"
        if not db_file.exists():
            logging.error(
                "SQLite database not found: %s\n"
                "Build it first with: python scripts/build_local_database.py",
                db_file,
            )
            sys.exit(2)
        logging.info("Loading cards from SQLite database...")
        # Load all cards into self.card_index for a unified lookup path
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cards")
            self.total_cards = cursor.fetchone()[0]
            cursor.execute(
                "SELECT name_lower, name, type_line, mana_cost, source_file FROM cards"
            )
            for row in cursor.fetchall():
                name_lower, name, type_line, mana_cost, source_file = row
                self.card_index[name_lower] = {
                    'name': name,
                    'type_line': type_line,
                    'mana_cost': mana_cost,
                    'file': source_file,
                }
        logging.info("Loaded %d cards from SQLite.", self.total_cards)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def _lookup(self, card_name: str) -> Tuple[bool, Optional[Dict]]:
        entry = self.card_index.get(card_name.lower())
        return (True, entry) if entry else (False, None)

    # ------------------------------------------------------------------
    # Count validation (mirrors validate_decklist.py logic)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, decklist_path: Path, verbose: bool = False) -> int:
        if not decklist_path.exists():
            logging.error("Decklist not found: %s", decklist_path)
            return 2

        mode = "SQLite" if self.use_sqlite else "JSON"
        print(f"Validating (offline / {mode}): {decklist_path}")
        print("=" * 70)

        mainboard, sideboard = parse_decklist(decklist_path)
        illegal: List[Tuple[int, str, str]] = []

        print("\n\U0001f4cb MAINBOARD VALIDATION\n")
        for qty, name in mainboard:
            found, info = self._lookup(name)
            if found:
                if verbose and info:
                    type_info = info.get('type_line', info.get('type', 'unknown'))
                    print(f"  \u2713 {qty}x {name}  [{type_info}]")
                else:
                    print(f"  \u2713 {qty}x {name}")
            else:
                print(f"  \u274c {qty}x {name} \u2014 NOT FOUND IN DATABASE")
                illegal.append((qty, name, 'mainboard'))

        if sideboard:
            print("\n\U0001f4cb SIDEBOARD VALIDATION\n")
            for qty, name in sideboard:
                found, info = self._lookup(name)
                if found:
                    if verbose and info:
                        type_info = info.get('type_line', info.get('type', 'unknown'))
                        print(f"  \u2713 {qty}x {name}  [{type_info}]")
                    else:
                        print(f"  \u2713 {qty}x {name}")
                else:
                    print(f"  \u274c {qty}x {name} \u2014 NOT FOUND IN DATABASE")
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
        description="Offline MTG decklist validator using pre-built local_db/."
    )
    p.add_argument("decklist", help="Path to decklist.txt")
    p.add_argument("--sqlite", action="store_true", help="Use SQLite DB instead of JSON index")
    p.add_argument("--quiet", action="store_true", help="Only print summary")
    p.add_argument("--verbose", action="store_true", help="Print card type info for each valid card")
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

    validator = LocalDecklistValidator(repo_root, use_sqlite=args.sqlite)
    sys.exit(validator.validate(decklist_path, verbose=args.verbose))


if __name__ == "__main__":
    main()
