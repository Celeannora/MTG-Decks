#!/usr/bin/env python3
"""
MTG Decklist Validator — Universal Local Edition

Validates a decklist against the local card pool. Works out of the box after
cloning the repo — no pre-build step required (CSV backend reads
cards_by_category/ directly). Optionally use pre-built local_db/ for faster
offline validation.

Quick Start:
    pip install -r requirements.txt
    python scripts/validate_decklist.py path/to/decklist.txt

Usage:
    # Default — reads cards_by_category/ CSVs directly (no setup needed)
    python scripts/validate_decklist.py Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --verbose Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --quiet Decks/my_deck/decklist.txt

    # Offline — uses pre-built local_db/ (run build_local_database.py first)
    python scripts/validate_decklist.py --db json Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --db sqlite Decks/my_deck/decklist.txt

    # Extra checks
    python scripts/validate_decklist.py --strict Decks/my_deck/decklist.txt
    python scripts/validate_decklist.py --show-tags Decks/my_deck/decklist.txt

    # Explicit color-identity enforcement (hard errors for off-color cards)
    python scripts/validate_decklist.py --deck-colors WB Decks/my_deck/decklist.txt

Exit codes:
    0  Validation passed
    1  Illegal / unrecognised cards found, or off-color cards (when --deck-colors used)
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
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from mtg_utils import RepoPaths, parse_decklist

CARD_TYPES = [
    'artifact', 'battle', 'creature', 'enchantment', 'instant',
    'land', 'other', 'planeswalker', 'sorcery',
]

BASIC_LAND_NAMES = {
    'plains', 'island', 'swamp', 'mountain', 'forest',
    'wastes', 'snow-covered plains', 'snow-covered island',
    'snow-covered swamp', 'snow-covered mountain', 'snow-covered forest',
}

# Cards that may legally exceed the 4-copy rule
UNLIMITED_COPIES = BASIC_LAND_NAMES | {
    'rat colony', 'relentless rats', 'persistent petitioners',
    'dragon\'s approach', 'shadowborn apostle', 'slime against humanity',
}

# Canonical color letter order for display
COLOR_ORDER = "WUBRG"

# Basic lands are colorless by color_identity in Scryfall data — exempt them
# from color-identity checks so Plains/Island/etc. never trigger a violation.
COLOR_IDENTITY_EXEMPT = BASIC_LAND_NAMES


# ---------------------------------------------------------------------------
# Tag computation (imported logic from search_cards.py)
# ---------------------------------------------------------------------------

TAG_RULES: List[Tuple[str, List[str]]] = [
    ("lifegain",    ["you gain", "lifelink", "gain life"]),
    ("mill",        ["mill ", "mills ", "put the top", "from the top",
                     "into their graveyard from their library"]),
    ("draw",        ["draw a card", "draw two", "draw three", "draw x",
                     "draw cards"]),
    ("removal",     ["exile target", "destroy target",
                     "deals damage to target", "deals that much damage"]),
    ("counter",     ["counter target spell", "counter that spell",
                     "counter target ability"]),
    ("ramp",        ["add {", "add mana",
                     "search your library for a basic land",
                     "search your library for a land"]),
    ("token",       ["create a ", "create x ", "create two ",
                     "create three ", "token"]),
    ("bounce",      ["return target", "return up to", "return each"]),
    ("discard",     ["discards a card", "discards two",
                     "each opponent discards", "target player discards"]),
    ("tutor",       ["search your library for a card",
                     "search your library for an instant",
                     "search your library for a sorcery"]),
    ("wipe",        ["destroy all", "exile all", "deals damage to all",
                     "deals damage to each"]),
    ("protection",  ["hexproof", "indestructible", "ward {"]),
    ("pump",        ["+1/+1 counter", "gets +", "+x/+x"]),
    ("reanimation", ["return target creature card from your graveyard",
                     "return up to one target creature card from a graveyard"]),
    ("etb",         ["when ~ enters", "when it enters",
                     "enters the battlefield"]),
    ("tribal",      ["other ", "s you control get", "s you control have"]),
    ("scry",        ["scry "]),
    ("surveil",     ["surveil "]),
]

KEYWORD_TAG_MAP: Dict[str, str] = {
    "flash":        "flash",
    "haste":        "haste",
    "trample":      "trample",
    "flying":       "flying",
    "deathtouch":   "deathtouch",
    "vigilance":    "vigilance",
    "reach":        "reach",
    "menace":       "menace",
    "lifelink":     "lifegain",
    "first strike": "first_strike",
    "double strike": "double_strike",
}


def compute_tags(oracle_text: str, keywords: str) -> Set[str]:
    """Derive strategic tags from oracle_text and keywords strings."""
    tags: Set[str] = set()
    oracle = oracle_text.lower()
    kw_raw = keywords.lower()

    for tag, patterns in TAG_RULES:
        if any(p in oracle for p in patterns):
            tags.add(tag)

    for kw, tag in KEYWORD_TAG_MAP.items():
        if kw in kw_raw:
            tags.add(tag)

    return tags


def normalize_colors(color_str: str) -> Set[str]:
    """Normalize a comma-separated color_identity value to a set of letters."""
    if not color_str:
        return set()
    return set(c.strip().upper() for c in color_str.split(",") if c.strip())


def format_color_set(colors: Set[str]) -> str:
    """Format a color set in canonical WUBRG order."""
    return "".join(c for c in COLOR_ORDER if c in colors) or "C"


def parse_deck_colors_arg(raw: str) -> Set[str]:
    """Parse a --deck-colors argument like 'WB' or 'W,B' into a color set."""
    # Accept both 'WB' and 'W,B' and 'W B' formats
    cleaned = raw.upper().replace(",", "").replace(" ", "")
    valid = set(COLOR_ORDER)
    colors = {c for c in cleaned if c in valid}
    if not colors and cleaned != "C":
        raise argparse.ArgumentTypeError(
            f"Invalid --deck-colors value '{raw}'. "
            f"Use WUBRG letters, e.g. WB or GU or WUBRG. "
            f"For colorless use C."
        )
    return colors  # empty set = colorless (C)


# ---------------------------------------------------------------------------
# Database backends
# ---------------------------------------------------------------------------

class CSVBackend:
    """Load card index from card database CSV files (default mode)."""

    def __init__(self, repo_root: Path) -> None:
        paths = RepoPaths(root=repo_root)
        self.card_database: Dict[str, Dict] = {}
        cards_dir = paths.cards_dir
        if not cards_dir.exists():
            logging.error(
                "Card database not found: %s\n\n"
                "  The cards_by_category/ directory is missing.\n"
                "  To populate it, run:\n\n"
                "    python scripts/fetch_and_categorize_cards.py\n",
                cards_dir,
            )
            sys.exit(2)
        # Check that it's not empty
        csv_count = sum(1 for _ in cards_dir.rglob("*.csv"))
        if csv_count == 0:
            logging.error(
                "Card database is empty: %s contains no CSV files.\n\n"
                "  Run: python scripts/fetch_and_categorize_cards.py\n",
                cards_dir,
            )
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
                                    "mana_cost": row.get("mana_cost", ""),
                                    "cmc": row.get("cmc", ""),
                                    "colors": row.get("colors", ""),
                                    "color_identity": row.get("color_identity", ""),
                                    "oracle_text": row.get("oracle_text", ""),
                                    "keywords": row.get("keywords", ""),
                                    "rarity": row.get("rarity", ""),
                                }
                except Exception as exc:
                    logging.warning("Could not read %s: %s", csv_file, exc)
        logging.info("Loaded %d unique card names.", len(self.card_database))

    def lookup(self, card_name: str) -> Tuple[bool, Optional[Dict]]:
        entry = self.card_database.get(card_name.lower())
        if entry:
            return True, entry
        return False, None

    def suggest(self, card_name: str, n: int = 3) -> List[str]:
        return difflib.get_close_matches(
            card_name.lower(), self.card_database.keys(), n=n, cutoff=0.75
        )


class JSONBackend:
    """Load card index from pre-built local database JSON index."""

    def __init__(self, repo_root: Path) -> None:
        paths = RepoPaths(root=repo_root)
        self.card_database: Dict[str, Dict] = {}
        index_file = paths.local_db / "card_index.json"
        if not index_file.exists():
            logging.error(
                "Local JSON database not found: %s\n\n"
                "  Build it first:\n\n"
                "    python scripts/build_local_database.py\n",
                index_file,
            )
            sys.exit(2)
        logging.info("Loading local JSON index...")
        with open(index_file, encoding="utf-8") as f:
            data = json.load(f)
        self.card_database = data["cards"]
        logging.info("Loaded %d cards from JSON index.", data["total_cards"])

    def lookup(self, card_name: str) -> Tuple[bool, Optional[Dict]]:
        entry = self.card_database.get(card_name.lower())
        if entry:
            return True, entry
        return False, None

    def suggest(self, card_name: str, n: int = 3) -> List[str]:
        return difflib.get_close_matches(
            card_name.lower(), self.card_database.keys(), n=n, cutoff=0.75
        )


class SQLiteBackend:
    """Load card index from pre-built local database SQLite file."""

    def __init__(self, repo_root: Path) -> None:
        paths = RepoPaths(root=repo_root)
        self.card_database: Dict[str, Dict] = {}
        db_file = paths.local_db / "card_details.db"
        if not db_file.exists():
            logging.error(
                "SQLite database not found: %s\n\n"
                "  Build it first:\n\n"
                "    python scripts/build_local_database.py\n",
                db_file,
            )
            sys.exit(2)
        logging.info("Loading cards from SQLite database...")
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name_lower, name, type_line, mana_cost, source_file, "
                "cmc, colors, color_identity, oracle_text, keywords, rarity "
                "FROM cards"
            )
            for row in cursor.fetchall():
                (name_lower, name, type_line, mana_cost, source_file,
                 cmc, colors, color_identity, oracle_text, keywords,
                 rarity) = row
                self.card_database[name_lower] = {
                    "name": name,
                    "type_line": type_line or "",
                    "mana_cost": mana_cost or "",
                    "file": source_file or "",
                    "cmc": str(cmc) if cmc else "",
                    "colors": colors or "",
                    "color_identity": color_identity or "",
                    "oracle_text": oracle_text or "",
                    "keywords": keywords or "",
                    "rarity": rarity or "",
                }
        logging.info("Loaded %d cards from SQLite.", len(self.card_database))

    def lookup(self, card_name: str) -> Tuple[bool, Optional[Dict]]:
        entry = self.card_database.get(card_name.lower())
        if entry:
            return True, entry
        return False, None

    def suggest(self, card_name: str, n: int = 3) -> List[str]:
        return difflib.get_close_matches(
            card_name.lower(), self.card_database.keys(), n=n, cutoff=0.75
        )


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class DecklistValidator:
    """Validates a decklist against a pluggable card database backend."""

    def __init__(self, backend, *, strict: bool = False,
                 show_tags: bool = False,
                 deck_colors: Optional[Set[str]] = None) -> None:
        self.backend = backend
        self.strict = strict
        self.show_tags = show_tags
        # Explicitly declared color identity for the deck (from --deck-colors).
        # When set, off-color cards are hard errors (exit 1).
        # When None, color identity is inferred from the card pool and
        # anomalies are warnings only.
        self.deck_colors: Optional[Set[str]] = deck_colors

    # -- count checks -------------------------------------------------------

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
        # 4-copy rule
        copy_counts: Dict[str, int] = {}
        for qty, name in mainboard + sideboard:
            if name.lower() not in UNLIMITED_COPIES:
                copy_counts[name] = copy_counts.get(name, 0) + qty
        for name, total in copy_counts.items():
            if total > 4:
                errors.append(
                    f"'{name}' appears {total} times (max 4 for non-basic lands)."
                )
        return errors

    # -- land count sanity --------------------------------------------------

    @staticmethod
    def _check_land_count(
        mainboard: List[Tuple[int, str]],
        card_data: Dict[str, Dict],
    ) -> List[str]:
        """Warn if land count is outside the typical 20-28 range."""
        warnings: List[str] = []
        land_count = 0
        for qty, name in mainboard:
            info = card_data.get(name.lower())
            if info:
                tl = info.get("type_line", "").lower()
                if "land" in tl:
                    land_count += qty
            elif name.lower() in BASIC_LAND_NAMES:
                land_count += qty
        if land_count < 20:
            warnings.append(
                f"Low land count: {land_count} lands (typical range is 20–28)."
            )
        elif land_count > 28:
            warnings.append(
                f"High land count: {land_count} lands (typical range is 20–28)."
            )
        return warnings

    # -- color identity consistency -----------------------------------------

    def _check_color_identity(
        self,
        mainboard: List[Tuple[int, str]],
        sideboard: List[Tuple[int, str]],
        card_data: Dict[str, Dict],
    ) -> Tuple[List[str], List[str]]:
        """Check each card's color identity against the declared (or inferred) deck identity.

        Returns (errors, warnings).

        When self.deck_colors is set (--deck-colors supplied by user):
          - Any card whose color_identity is not a subset of deck_colors is an ERROR.
          - Basic lands and colorless cards are exempt.

        When self.deck_colors is None (inferred mode):
          - The deck's color identity is computed as the union of all cards.
          - Cards that exceed the union identity indicate a data anomaly and are
            reported as WARNINGS (this is unusual but can happen with bad CSV data).
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Determine the reference color set
        if self.deck_colors is not None:
            reference = self.deck_colors
            strict_mode = True
        else:
            # Infer from union of all cards
            reference: Set[str] = set()
            for _, name in mainboard + sideboard:
                info = card_data.get(name.lower())
                if info:
                    reference |= normalize_colors(info.get("color_identity", ""))
            strict_mode = False

        if not reference and self.deck_colors is None:
            # Colorless deck inferred — nothing to check
            return errors, warnings

        for _, name in mainboard + sideboard:
            # Skip basic lands — they are colorless in Scryfall's color_identity
            # field and should never trigger a violation
            if name.lower() in COLOR_IDENTITY_EXEMPT:
                continue
            info = card_data.get(name.lower())
            if not info:
                continue
            card_id = normalize_colors(info.get("color_identity", ""))
            if not card_id:
                # Colorless card — always legal in any deck
                continue
            if not card_id.issubset(reference):
                extra = card_id - reference
                extra_str = format_color_set(extra)
                msg = (
                    f"'{name}' has color identity {format_color_set(card_id)} "
                    f"— adds {extra_str} outside declared "
                    f"{format_color_set(reference)}."
                )
                if strict_mode:
                    errors.append(msg)
                else:
                    warnings.append(f"[data anomaly] {msg}")

        return errors, warnings

    # -- tag-based synergy summary ------------------------------------------

    @staticmethod
    def _synergy_summary(
        mainboard: List[Tuple[int, str]],
        card_data: Dict[str, Dict],
    ) -> Dict[str, int]:
        """Count how many mainboard non-land cards contribute to each tag."""
        tag_counts: Counter = Counter()
        for qty, name in mainboard:
            info = card_data.get(name.lower())
            if not info:
                continue
            tl = info.get("type_line", "").lower()
            if "land" in tl:
                continue
            tags = compute_tags(
                info.get("oracle_text", ""),
                info.get("keywords", ""),
            )
            for tag in tags:
                tag_counts[tag] += qty
        return dict(tag_counts)

    # -- main validate method -----------------------------------------------

    def validate(self, decklist_path: Path, verbose: bool = False) -> int:
        if not decklist_path.exists():
            logging.error("Decklist not found: %s", decklist_path)
            return 2

        print(f"Validating: {decklist_path}")
        if self.deck_colors is not None:
            declared_str = format_color_set(self.deck_colors) if self.deck_colors else "C"
            print(f"Declared color identity: {declared_str}")
        print("=" * 70)

        mainboard, sideboard = parse_decklist(decklist_path)

        if not mainboard:
            logging.error("Decklist is empty or has no mainboard cards.")
            return 2

        illegal: List[Tuple[int, str, str]] = []
        card_data: Dict[str, Dict] = {}  # lookup cache for enriched checks

        print("\n  MAINBOARD VALIDATION\n")
        for qty, name in mainboard:
            found, info = self.backend.lookup(name)
            if found and info:
                card_data[name.lower()] = info
                if verbose:
                    print(f"  + {qty}x {name}")
                    print(f"     -> {info.get('file', '')}")
                else:
                    print(f"  + {qty}x {name}")
            else:
                print(f"  X {qty}x {name} -- NOT FOUND IN DATABASE")
                suggestions = self.backend.suggest(name)
                if suggestions:
                    print(f"     Did you mean: {', '.join(suggestions)}?")
                illegal.append((qty, name, "mainboard"))

        if sideboard:
            print("\n  SIDEBOARD VALIDATION\n")
            for qty, name in sideboard:
                found, info = self.backend.lookup(name)
                if found and info:
                    card_data[name.lower()] = info
                    if verbose:
                        print(f"  + {qty}x {name}")
                        print(f"     -> {info.get('file', '')}")
                    else:
                        print(f"  + {qty}x {name}")
                else:
                    print(f"  X {qty}x {name} -- NOT FOUND IN DATABASE")
                    suggestions = self.backend.suggest(name)
                    if suggestions:
                        print(f"     Did you mean: {', '.join(suggestions)}?")
                    illegal.append((qty, name, "sideboard"))

        # -- Count checks ---------------------------------------------------
        count_errors = self._validate_counts(mainboard, sideboard)

        # -- Strict-mode extra checks ---------------------------------------
        land_warnings: List[str] = []
        if self.strict:
            land_warnings = self._check_land_count(mainboard, card_data)

        # -- Color identity check -------------------------------------------
        color_errors, color_warnings = self._check_color_identity(
            mainboard, sideboard, card_data
        )

        # -- Synergy tags ---------------------------------------------------
        tag_summary: Dict[str, int] = {}
        if self.show_tags:
            tag_summary = self._synergy_summary(mainboard, card_data)

        # -- Color identity summary -----------------------------------------
        deck_colors: Set[str] = set()
        for _, name in mainboard + sideboard:
            info = card_data.get(name.lower())
            if info:
                deck_colors |= normalize_colors(info.get("color_identity", ""))

        # -- Print summary --------------------------------------------------
        print("\n" + "=" * 70)
        print("\n  VALIDATION SUMMARY\n")
        main_total = sum(q for q, _ in mainboard)
        side_total = sum(q for q, _ in sideboard)
        print(f"  Mainboard : {main_total} cards "
              f"({len(mainboard)} unique entries)")
        if sideboard:
            print(f"  Sideboard : {side_total} cards "
                  f"({len(sideboard)} unique entries)")

        if deck_colors:
            print(f"  Colors    : {format_color_set(deck_colors)}")

        if count_errors:
            print("\n  COUNT VIOLATIONS\n")
            for err in count_errors:
                print(f"  * {err}")

        if land_warnings:
            print("\n  LAND WARNINGS\n")
            for w in land_warnings:
                print(f"  * {w}")

        if color_errors:
            print("\n  COLOR IDENTITY VIOLATIONS\n")
            for err in color_errors:
                print(f"  * {err}")

        if color_warnings:
            print("\n  COLOR IDENTITY WARNINGS\n")
            for w in color_warnings:
                print(f"  * {w}")

        if tag_summary:
            print("\n  SYNERGY TAGS (mainboard non-land cards)\n")
            for tag, count in sorted(tag_summary.items(),
                                     key=lambda x: -x[1]):
                print(f"    {tag:<16} {count:>3} cards")

        if illegal:
            print(f"\n  VALIDATION FAILED\n")
            print(f"  Found {len(illegal)} unrecognised card(s):\n")
            for qty, name, section in illegal:
                print(f"  * {qty}x {name} ({section})")
            print("\n  These cards are either rotated or not present "
                  "in the database.\n")
            return 1

        if color_errors:
            print(f"\n  VALIDATION FAILED — color identity violation(s) above.\n")
            return 1

        if count_errors:
            return 3

        print("\n  VALIDATION PASSED\n")
        print("  All cards are legal and present in the database.\n")
        return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="validate_decklist.py",
        description=(
            "Validate an MTG decklist against the local card database.\n\n"
            "By default, reads cards_by_category/ CSVs directly (no setup\n"
            "needed beyond cloning the repo). Use --db to select a faster\n"
            "pre-built backend."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "backends:\n"
            "  csv     Read cards_by_category/ CSVs directly (default, no setup)\n"
            "  json    Read local_db/card_index.json (run build_local_database.py first)\n"
            "  sqlite  Read local_db/card_details.db (run build_local_database.py first)\n"
            "\n"
            "examples:\n"
            "  %(prog)s Decks/my_deck/decklist.txt\n"
            "  %(prog)s --verbose Decks/my_deck/decklist.txt\n"
            "  %(prog)s --db sqlite Decks/my_deck/decklist.txt\n"
            "  %(prog)s --strict --show-tags Decks/my_deck/decklist.txt\n"
            "  %(prog)s --deck-colors WB Decks/my_deck/decklist.txt\n"
        ),
    )
    p.add_argument(
        "decklist",
        help="path to decklist.txt (relative to repo root or absolute)",
    )
    p.add_argument(
        "--db",
        choices=["csv", "json", "sqlite"],
        default="csv",
        help="card database backend (default: csv)",
    )
    # Keep --local and --sqlite as hidden aliases for backwards compatibility
    p.add_argument(
        "--local",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    p.add_argument(
        "--sqlite",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    p.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="suppress per-card output, only print summary",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="print source CSV path for each card",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="enable extra checks (land count sanity warnings)",
    )
    p.add_argument(
        "--show-tags",
        action="store_true",
        help="print synergy tag summary for the deck",
    )
    p.add_argument(
        "--deck-colors",
        metavar="COLORS",
        default=None,
        help=(
            "declare the deck's color identity (e.g. WB, GU, WUBRG, C). "
            "When set, any card outside this identity is a hard error (exit 1). "
            "Without this flag, colors are inferred from the card pool and "
            "anomalies are warnings only."
        ),
    )
    return p


def main() -> None:
    args = _build_parser().parse_args()
    log_level = logging.WARNING if args.quiet else logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=log_level)

    paths = RepoPaths()
    repo_root = paths.root

    decklist_path = Path(args.decklist)
    if not decklist_path.is_absolute():
        decklist_path = repo_root / decklist_path

    # Resolve backend — support legacy --local / --sqlite flags
    db_choice = args.db
    if args.local and args.sqlite:
        db_choice = "sqlite"
    elif args.local:
        db_choice = "json"

    if db_choice == "sqlite":
        backend = SQLiteBackend(repo_root)
    elif db_choice == "json":
        backend = JSONBackend(repo_root)
    else:
        backend = CSVBackend(repo_root)

    # Parse --deck-colors if provided
    deck_colors: Optional[Set[str]] = None
    if args.deck_colors:
        raw = args.deck_colors.strip().upper()
        if raw == "C":
            deck_colors = set()  # explicitly colorless
        else:
            deck_colors = parse_deck_colors_arg(raw)

    validator = DecklistValidator(
        backend,
        strict=args.strict,
        show_tags=args.show_tags,
        deck_colors=deck_colors,
    )
    sys.exit(validator.validate(decklist_path, verbose=args.verbose))


if __name__ == "__main__":
    main()
