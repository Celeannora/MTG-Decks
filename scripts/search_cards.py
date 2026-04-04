#!/usr/bin/env python3
"""
MTG Card Search Tool — AI-Assisted Deck Building

Replaces manual file-by-file sweeps. Reads every relevant CSV and returns a
filtered candidate pool so AI agents can build from verified data without
holding hundreds of KB of raw CSVs in context.

Usage:
    python scripts/search_cards.py --type creature --colors W --tags lifelink,flying
    python scripts/search_cards.py --type instant --oracle "mill" --colors UB
    python scripts/search_cards.py --type creature --cmc-max 3 --colors WB --tags removal
    python scripts/search_cards.py --name "Sheoldred"
    python scripts/search_cards.py --type land --colors WUB
    python scripts/search_cards.py --type creature --tags lifegain --rarity rare,mythic

Flags:
    --type          Card type(s): creature, instant, sorcery, enchantment, artifact,
                    land, planeswalker, battle, other  (comma-separated for multiple)
    --colors        Color identity filter: W, U, B, R, G, WB, WUB, etc.
                    Use 'C' for colorless. Prefix with '=' for exact match (e.g. =WB)
    --oracle        Substring match in oracle_text (case-insensitive)
    --tags          Strategy tag(s) to filter by (comma-separated)
                    See TAG SYSTEM below for full list
    --name          Substring match in card name (case-insensitive)
    --cmc-max       Maximum converted mana cost (inclusive)
    --cmc-min       Minimum converted mana cost (inclusive)
    --rarity        Rarity filter: common, uncommon, rare, mythic (comma-separated)
    --keywords      MTG keyword filter (comma-separated, e.g. Flying,Lifelink)
    --limit         Max results to return (default: 200)
    --show-tags     Print computed tags for each card in results
    --format        Output format: table (default), csv, names

TAG SYSTEM:
    lifegain        — "you gain" life, lifelink keyword
    mill            — "mill", "put top", "into graveyard from library"
    draw            — "draw a card/cards"
    removal         — "exile target", "destroy target", "deals damage to"
    counter         — "counter target spell/ability"
    ramp            — "add {", "search your library for a land"
    token           — "create a", "token"
    bounce          — "return target", "return up to"
    discard         — "target player discards", "each opponent discards"
    tutor           — "search your library for a card"
    wipe            — "destroy all", "exile all", "deals damage to all"
    protection      — "hexproof", "indestructible", "ward"
    pump            — "+1/+1 counter", "gets +X/+X"
    reanimation     — "return from graveyard", "reanimate"
    etb             — "enters", "when ~ enters the battlefield"
    tribal          — "other [creature subtype]s you control"
    flash           — flash keyword
    haste           — haste keyword
    trample         — trample keyword
    flying          — flying keyword
    deathtouch      — deathtouch keyword
    vigilance       — vigilance keyword
    reach           — reach keyword
    menace          — menace keyword
    scry            — "scry"
    surveil         — "surveil"

Exit codes:
    0  Results found and printed
    1  No results found
    2  Invalid arguments
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Strategic tag rules — (tag_name, list_of_oracle_text_substrings_OR_keywords)
# All matches are case-insensitive. A card gets a tag if ANY substring matches.
# ---------------------------------------------------------------------------
TAG_RULES: List[Tuple[str, List[str]]] = [
    ("lifegain",    ["you gain", "lifelink", "gain life"]),
    ("mill",        ["mill ", "mills ", "put the top", "from the top", "into their graveyard from their library"]),
    ("draw",        ["draw a card", "draw two", "draw three", "draw x", "draw cards"]),
    ("removal",     ["exile target", "destroy target", "deals damage to target", "deals that much damage"]),
    ("counter",     ["counter target spell", "counter that spell", "counter target ability"]),
    ("ramp",        ["add {", "add mana", "search your library for a basic land", "search your library for a land"]),
    ("token",       ["create a ", "create x ", "create two ", "create three ", "token"]),
    ("bounce",      ["return target", "return up to", "return each"]),
    ("discard",     ["discards a card", "discards two", "each opponent discards", "target player discards"]),
    ("tutor",       ["search your library for a card", "search your library for an instant", "search your library for a sorcery"]),
    ("wipe",        ["destroy all", "exile all", "deals damage to all", "deals damage to each"]),
    ("protection",  ["hexproof", "indestructible", "ward {"]),
    ("pump",        ["+1/+1 counter", "gets +", "+x/+x"]),
    ("reanimation", ["return target creature card from your graveyard", "return up to one target creature card from a graveyard"]),
    ("etb",         ["when ~ enters", "when it enters", "enters the battlefield"]),
    ("tribal",      ["other ", "s you control get", "s you control have"]),
    ("scry",        ["scry "]),
    ("surveil",     ["surveil "]),
]

# Keywords that map directly to tags (checked against the `keywords` column)
KEYWORD_TAG_MAP: Dict[str, str] = {
    "flash":       "flash",
    "haste":       "haste",
    "trample":     "trample",
    "flying":      "flying",
    "deathtouch":  "deathtouch",
    "vigilance":   "vigilance",
    "reach":       "reach",
    "menace":      "menace",
    "lifelink":    "lifegain",
    "first strike": "first_strike",
    "double strike": "double_strike",
}

CARD_TYPES = [
    'artifact', 'battle', 'creature', 'enchantment', 'instant',
    'land', 'other', 'planeswalker', 'sorcery',
]

COLOR_ORDER = "WUBRG"


def compute_tags(card: Dict) -> Set[str]:
    """Derive strategic tags from a card's oracle_text and keywords."""
    tags: Set[str] = set()
    oracle = card.get("oracle_text", "").lower()
    kw_raw = card.get("keywords", "").lower()

    for tag, patterns in TAG_RULES:
        if any(p in oracle for p in patterns):
            tags.add(tag)

    for kw, tag in KEYWORD_TAG_MAP.items():
        if kw in kw_raw:
            tags.add(tag)

    return tags


def normalize_colors(color_str: str) -> Set[str]:
    """Normalize a colors/color_identity CSV column value to a set of letters."""
    if not color_str:
        return set()
    # Scryfall stores as comma-separated: "W,U" or empty for colorless
    return set(c.strip().upper() for c in color_str.split(",") if c.strip())


def color_matches(card: Dict, color_filter: str) -> bool:
    """
    Filter by color identity.
    'C' = colorless only
    Prefix '=' for exact color match; otherwise subset match (deck can play card).
    """
    exact = color_filter.startswith("=")
    colors = color_filter.lstrip("=").upper()

    if colors == "C":
        return normalize_colors(card.get("color_identity", "")) == set()

    wanted = set(colors)
    card_identity = normalize_colors(card.get("color_identity", ""))

    if exact:
        return card_identity == wanted
    else:
        # Card is playable in a deck of these colors if card's identity ⊆ wanted
        return card_identity.issubset(wanted)


def load_cards(
    repo_root: Path,
    types: Optional[List[str]],
) -> List[Dict]:
    """Load all cards of the requested types from the card database directory."""
    from mtg_utils import RepoPaths
    paths = RepoPaths(root=repo_root)
    cards_dir = paths.cards_dir
    if not cards_dir.exists():
        print(f"ERROR: {RepoPaths.CARDS_DIR_NAME}/ not found at {cards_dir}", file=sys.stderr)
        sys.exit(2)

    target_types = types if types else CARD_TYPES
    results: List[Dict] = []
    seen_names: Set[str] = set()

    for card_type in target_types:
        type_dir = cards_dir / card_type
        if not type_dir.exists():
            continue
        for csv_file in sorted(type_dir.glob("*.csv")):
            try:
                with open(csv_file, encoding="utf-8") as f:
                    for row in csv.DictReader(f):
                        name = row.get("name", "").strip()
                        key = name.lower()
                        if key and key not in seen_names:
                            seen_names.add(key)
                            row["_card_type"] = card_type
                            row["_source_file"] = str(
                                csv_file.relative_to(repo_root)
                            )
                            results.append(row)
            except Exception as exc:
                print(f"WARNING: Could not read {csv_file}: {exc}", file=sys.stderr)

    return results


def filter_cards(
    cards: List[Dict],
    *,
    color_filter: Optional[str],
    oracle_filter: Optional[str],
    name_filter: Optional[str],
    tag_filters: Optional[List[str]],
    cmc_min: Optional[float],
    cmc_max: Optional[float],
    rarities: Optional[List[str]],
    keyword_filters: Optional[List[str]],
) -> List[Tuple[Dict, Set[str]]]:
    """Apply all filters and return (card, tags) tuples."""
    results: List[Tuple[Dict, Set[str]]] = []

    for card in cards:
        # Name filter
        if name_filter and name_filter.lower() not in card.get("name", "").lower():
            continue

        # Oracle text filter
        if oracle_filter and oracle_filter.lower() not in card.get("oracle_text", "").lower():
            continue

        # Color filter
        if color_filter and not color_matches(card, color_filter):
            continue

        # CMC filters
        try:
            cmc = float(card.get("cmc", 0) or 0)
        except (ValueError, TypeError):
            cmc = 0.0
        if cmc_min is not None and cmc < cmc_min:
            continue
        if cmc_max is not None and cmc > cmc_max:
            continue

        # Rarity filter
        if rarities and card.get("rarity", "").lower() not in rarities:
            continue

        # Keyword filter (MTG mechanical keywords, not our tags)
        if keyword_filters:
            card_kws = {k.strip().lower() for k in card.get("keywords", "").split(";")}
            if not all(kf.lower() in card_kws for kf in keyword_filters):
                continue

        # Compute tags
        tags = compute_tags(card)

        # Tag filter (must have ALL requested tags)
        if tag_filters:
            if not all(t in tags for t in tag_filters):
                continue

        results.append((card, tags))

    return results


def print_table(
    results: List[Tuple[Dict, Set[str]]],
    show_tags: bool,
    limit: int,
) -> None:
    """Print results as a readable table."""
    total = len(results)
    shown = results[:limit]

    print(f"\n{'='*80}")
    print(f"  CANDIDATE POOL — {total} cards found (showing {min(total, limit)})")
    print(f"{'='*80}\n")

    for card, tags in shown:
        name = card.get("name", "")
        mana = card.get("mana_cost", "") or "—"
        cmc_raw = card.get("cmc", "0")
        try:
            cmc = int(float(cmc_raw))
        except (ValueError, TypeError):
            cmc = 0
        type_line = card.get("type_line", "")
        rarity = card.get("rarity", "")[0].upper() if card.get("rarity") else "?"
        set_code = card.get("set", "")
        collector = card.get("collector_number", "")
        source = card.get("_source_file", "")

        print(f"  {name}")
        print(f"    Mana: {mana}  CMC: {cmc}  [{rarity}] ({set_code}) #{collector}")
        print(f"    Type: {type_line}")

        oracle = card.get("oracle_text", "").replace("\n", " / ")
        if oracle:
            # Wrap oracle text at 70 chars
            words = oracle.split()
            lines = []
            current = []
            length = 0
            for w in words:
                if length + len(w) + 1 > 70:
                    lines.append(" ".join(current))
                    current = [w]
                    length = len(w)
                else:
                    current.append(w)
                    length += len(w) + 1
            if current:
                lines.append(" ".join(current))
            for line in lines:
                print(f"    {line}")

        if show_tags and tags:
            print(f"    Tags: {', '.join(sorted(tags))}")

        print(f"    Source: {source}\n")

    if total > limit:
        print(f"  ... {total - limit} more results. Use --limit to show more.\n")

    print(f"{'='*80}")
    print(f"  Total candidates: {total}")
    print(f"{'='*80}\n")


def print_csv(results: List[Tuple[Dict, Set[str]]], limit: int) -> None:
    """Print results as CSV for easy parsing."""
    shown = results[:limit]
    fieldnames = [
        "name", "mana_cost", "cmc", "type_line", "colors", "color_identity",
        "rarity", "set", "collector_number", "keywords", "oracle_text", "_source_file", "_tags"
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for card, tags in shown:
        row = dict(card)
        row["_tags"] = ";".join(sorted(tags))
        writer.writerow(row)


def print_names(results: List[Tuple[Dict, Set[str]]], limit: int) -> None:
    """Print just card names — useful for quick AI candidate lists."""
    for card, _ in results[:limit]:
        src = card.get("_source_file", "")
        print(f"{card.get('name', '')}  [{src}]")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Search the MTG Standard card database with strategy-aware filtering.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--type", dest="types", help="Card type(s), comma-separated")
    p.add_argument("--colors", help="Color identity filter (e.g. WB, =WB, UB, C)")
    p.add_argument("--oracle", help="Substring match in oracle text")
    p.add_argument("--name", help="Substring match in card name")
    p.add_argument("--tags", help="Strategy tags, comma-separated (e.g. lifegain,draw)")
    p.add_argument("--cmc-max", type=float, help="Max CMC (inclusive)")
    p.add_argument("--cmc-min", type=float, help="Min CMC (inclusive)")
    p.add_argument("--rarity", help="Rarity filter: common,uncommon,rare,mythic")
    p.add_argument("--keywords", help="MTG keyword(s), comma-separated (e.g. Flying,Lifelink)")
    p.add_argument("--limit", type=int, default=200, help="Max results (default: 200)")
    p.add_argument("--show-tags", action="store_true", help="Show computed tags per card")
    p.add_argument("--format", choices=["table", "csv", "names"], default="table",
                   help="Output format (default: table)")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Resolve paths
    from mtg_utils import RepoPaths
    paths = RepoPaths()
    repo_root = paths.root

    # Parse type list
    types: Optional[List[str]] = None
    if args.types:
        requested = [t.strip().lower() for t in args.types.split(",")]
        invalid = [t for t in requested if t not in CARD_TYPES]
        if invalid:
            print(f"ERROR: Unknown type(s): {', '.join(invalid)}", file=sys.stderr)
            print(f"Valid types: {', '.join(CARD_TYPES)}", file=sys.stderr)
            sys.exit(2)
        types = requested

    # Parse tag list
    tag_filters: Optional[List[str]] = None
    if args.tags:
        tag_filters = [t.strip().lower() for t in args.tags.split(",")]

    # Parse rarity list
    rarities: Optional[List[str]] = None
    if args.rarity:
        rarities = [r.strip().lower() for r in args.rarity.split(",")]

    # Parse keyword list
    keyword_filters: Optional[List[str]] = None
    if args.keywords:
        keyword_filters = [k.strip() for k in args.keywords.split(",")]

    # Load and filter
    all_cards = load_cards(repo_root, types)

    if not all_cards:
        from mtg_utils import RepoPaths
        print(f"No cards loaded. Check that {RepoPaths.CARDS_DIR_NAME}/ exists and is populated.", file=sys.stderr)
        sys.exit(2)

    results = filter_cards(
        all_cards,
        color_filter=args.colors,
        oracle_filter=args.oracle,
        name_filter=args.name,
        tag_filters=tag_filters,
        cmc_min=args.cmc_min,
        cmc_max=args.cmc_max,
        rarities=rarities,
        keyword_filters=keyword_filters,
    )

    if not results:
        print("\nNo cards matched the given filters.\n", file=sys.stderr)
        sys.exit(1)

    if args.format == "csv":
        print_csv(results, args.limit)
    elif args.format == "names":
        print_names(results, args.limit)
    else:
        print_table(results, show_tags=args.show_tags, limit=args.limit)

    sys.exit(0)


if __name__ == "__main__":
    main()
