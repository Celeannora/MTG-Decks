#!/usr/bin/env python3
"""
MTG Decklist Validator

Validates a decklist.txt against the cards_by_category/ database.
Supports both online (CSV scan) and fast offline (pre-built local_db/) modes.

Usage:
    # Online — reads cards_by_category/ CSVs directly
    python scripts/validate_decklist.py Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --quiet Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --verbose Decks/my_deck/decklist.txt

    # Offline — uses pre-built local_db/ (run build_local_database.py first)
    python scripts/validate_decklist.py --local Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --local --sqlite Decks/my_deck/decklist.txt

Exit codes:
    0  Validation passed
    1  Illegal / unrecognised cards found
    2  Input file or database not found
    3  Deck count violation (wrong 60/15/4-copy counts)
"""

import argparse
import csv
import difflib
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


# ---------------------------------------------------------------------------
# Database backends
# ---------------------------------------------------------------------------

class CSVBackend:
    """Load card index from cards_by_category/ CSV files (online mode)."""

    def __init__(self, repo_root: Path) -> None:
        self.card_database: Dict[str, Dict] = {}
        cards_dir = repo_root / "cards_by_category"
        if not cards_dir.exists():
            logging.error("Card database directory not found: %s", cards_dir)
            sys.exit(2)
        logging.info("Loading card database from %s ...", cards_dir)
        seen: set = set()
        for card_type in CARD_TYPES:
            type_dir = cards_dir / card_type
            if not type_dir.exists():
                continue
            for csv_file in sorted(type_dir.glob("*.csv")):
                try:
                    with open(csv_file, encoding="utf-8") as f:
                        for row in csv.DictReader(f):
                            raw_name = row.get("name", "").strip()
                            key = raw_name.lower()
                            if key and key not in seen:
                                seen.add(key)
                                self.card_database[key] = {
                                    "name": raw_name,
                                    "file": str(csv_file.relative_to(repo_root)),
                                    "set": row.get("set", ""),
                                    "type_line": row.get("type_line", ""),
                                }
                except Exception as exc:
                    logging.warning("Could not read %s: %s", csv_file, exc)
        logging.info("Loaded %d unique card names.", len(self.card_database))

    def lookup(self, card_name: str) -> Tuple[bool, str]:
        entry = self.card_database.get(card_name.lower())
        if entry:
            return True, entry["file"]
        return False, ""

    def suggest(self, card_name: str, n: int = 3) -> List[str]:
        return difflib.get_close_matches(
            card_name.lower(), self.card_database.keys(), n=n, cutoff=0.75
        )


class JSONBackend:
    """Load card index from pre-built local_db/card_index.json (offline mode)."""

    def __init__(self, repo_root: Path) -> None:
        self.card_database: Dict[str, Dict] = {}
        index_file = repo_root / "local_db" / "card_index.json"
        if not index_file.exists():
            logging.error(
                "Local database not found: %s\n"
                "Build it first with: python scripts/build_local_database.py",
                index_file,
            )
            sys.exit(2)
        logging.info("Loading local JSON index...")
        with open(index_file, encoding="utf-8") as f:
            data = json.load(f)
        self.card_database = data["cards"]
        logging.info("Loaded %d cards from JSON index.", data["total_cards"])

    def lookup(self, card_name: str) -> Tuple[bool, str]:
        entry = self.card_database.get(card_name.lower())
        if entry:
            return True, entry.get("file", "")
        return False, ""

    def suggest(self, card_name: str, n: int = 3) -> List[str]:
        return difflib.get_close_matches(
            card_name.lower(), self.card_database.keys(), n=n, cutoff=0.75
        )


class SQLiteBackend:
    """Load card index from pre-built local_db/card_details.db (offline SQLite mode)."""

    def __init__(self, repo_root: Path) -> None:
        self.card_database: Dict[str, Dict] = {}
        db_file = repo_root / "local_db" / "card_details.db"
        if not db_file.exists():
            logging.error(
                "SQLite database not found: %s\n"
                "Build it first with: python scripts/build_local_database.py",
                db_file,
            )
            sys.exit(2)
        logging.info("Loading cards from SQLite database...")
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name_lower, name, type_line, mana_cost, source_file FROM cards"
            )
            for row in cursor.fetchall():
                name_lower, name, type_line, mana_cost, source_file = row
                self.card_database[name_lower] = {
                    "name": name,
                    "type_line": type_line,
                    "mana_cost": mana_cost,
                    "file": source_file,
                }
        logging.info("Loaded %d cards from SQLite.", len(self.card_database))

    def lookup(self, card_name: str) -> Tuple[bool, str]:
        entry = self.card_database.get(card_name.lower())
        if entry:
            return True, entry.get("file", "")
        return False, ""

    def suggest(self, card_name: str, n: int = 3) -> List[str]:
        return difflib.get_close_matches(
            card_name.lower(), self.card_database.keys(), n=n, cutoff=0.75
        )


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class DecklistValidator:
    """Validates a decklist against a pluggable card database backend."""

    def __init__(self, backend) -> None:
        self.backend = backend

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
                errors.append(
                    f"'{name}' appears {total} times (max 4 for non-basic lands)."
                )
        return errors

    def validate(self, decklist_path: Path, verbose: bool = False) -> int:
        if not decklist_path.exists():
            logging.error("Decklist not found: %s", decklist_path)
            return 2

        print(f"Validating: {decklist_path}")
        print("=" * 70)

        mainboard, sideboard = parse_decklist(decklist_path)
        illegal: List[Tuple[int, str, str]] = []

        print("\n📋 MAINBOARD VALIDATION\n")
        for qty, name in mainboard:
            found, src = self.backend.lookup(name)
            if found:
                if verbose:
                    print(f"  ✓ {qty}x {name}")
                    print(f"     └─ {src}")
                else:
                    print(f"  ✓ {qty}x {name}")
            else:
                print(f"  ❌ {qty}x {name} — NOT FOUND IN DATABASE")
                suggestions = self.backend.suggest(name)
                if suggestions:
                    print(f"     Did you mean: {', '.join(suggestions)}?")
                illegal.append((qty, name, "mainboard"))

        if sideboard:
            print("\n📋 SIDEBOARD VALIDATION\n")
            for qty, name in sideboard:
                found, src = self.backend.lookup(name)
                if found:
                    if verbose:
                        print(f"  ✓ {qty}x {name}")
                        print(f"     └─ {src}")
                    else:
                        print(f"  ✓ {qty}x {name}")
                else:
                    print(f"  ❌ {qty}x {name} — NOT FOUND IN DATABASE")
                    suggestions = self.backend.suggest(name)
                    if suggestions:
                        print(f"     Did you mean: {', '.join(suggestions)}?")
                    illegal.append((qty, name, "sideboard"))

        count_errors = self._validate_counts(mainboard, sideboard)

        print("\n" + "=" * 70)
        print("\n📊 VALIDATION SUMMARY\n")
        print(f"  Mainboard : {sum(q for q, _ in mainboard)} cards "
              f"({len(mainboard)} unique entries)")
        if sideboard:
            print(f"  Sideboard : {sum(q for q, _ in sideboard)} cards")

        if count_errors:
            print("\n⚠️  COUNT VIOLATIONS\n")
            for err in count_errors:
                print(f"  • {err}")

        if illegal:
            print(f"\n❌ VALIDATION FAILED\n")
            print(f"  Found {len(illegal)} unrecognised card(s):\n")
            for qty, name, section in illegal:
                print(f"  • {qty}x {name} ({section})")
            print("\n  These cards are either rotated or not present in the database.\n")
            return 1

        if count_errors:
            return 3

        print("\n✅ VALIDATION PASSED\n")
        print("  All cards are legal and present in the database.\n")
        return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Validate an MTG decklist against the card database."
    )
    p.add_argument("decklist", help="Path to decklist.txt")
    p.add_argument("--quiet",   action="store_true", help="Only print summary")
    p.add_argument("--verbose", action="store_true", help="Print source CSV for each card")
    p.add_argument(
        "--local",
        action="store_true",
        help="Use pre-built local_db/ for fast offline validation "
             "(run build_local_database.py first)",
    )
    p.add_argument(
        "--sqlite",
        action="store_true",
        help="(with --local) Use SQLite DB instead of JSON index",
    )
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

    # Select backend
    if args.local and args.sqlite:
        backend = SQLiteBackend(repo_root)
    elif args.local:
        backend = JSONBackend(repo_root)
    else:
        backend = CSVBackend(repo_root)

    validator = DecklistValidator(backend)
    sys.exit(validator.validate(decklist_path, verbose=args.verbose))


if __name__ == "__main__":
    main()
