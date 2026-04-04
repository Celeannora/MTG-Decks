#!/usr/bin/env python3
"""
Synergy Analysis — Gate 2.5 Automation

Reads a card list (from a session.md candidate pool, a decklist.txt, or a
plain text file) and produces a Gate 2.5 synergy report:

  - Computes strategy tags for every card from oracle text + keywords
  - Scores pairwise tag-based interactions (FEEDS, TRIGGERS, REDUNDANT)
  - Calculates Synergy Count, Role Breadth, and Dependency for each card
  - Checks all 5 Gate 2.5 thresholds and reports PASS / FAIL
  - Writes a pre-populated Gate 2.5 markdown block you can paste into session.md

Usage:
    # Analyze candidate pool extracted from a session.md
    python scripts/synergy_analysis.py Decks/2026-04-03_My_Deck/session.md

    # Analyze a finished decklist.txt
    python scripts/synergy_analysis.py Decks/2026-04-03_My_Deck/decklist.txt

    # Analyze a plain card-name list (one name per line)
    python scripts/synergy_analysis.py my_candidates.txt --format names

    # Write report to a file instead of stdout
    python scripts/synergy_analysis.py session.md --output report.md

Flags:
    --format    Input format: auto (default), session, decklist, names
    --output    Write markdown report to this file (default: stdout)
    --min-synergy N   Override the avg synergy threshold (default: 3.0)

Exit codes:
    0  All Gate 2.5 thresholds passed
    1  One or more thresholds failed
    2  Input file not found or no cards extracted
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mtg_utils import RepoPaths, parse_decklist
from search_cards import TAG_RULES, KEYWORD_TAG_MAP, compute_tags, CARD_TYPES

# ---------------------------------------------------------------------------
# Interaction classification rules
# These define which tag combinations on two cards suggest an interaction.
# Format: (tag_on_A, tag_on_B, interaction_type, note_template)
# ---------------------------------------------------------------------------

INTERACTION_RULES: List[Tuple[str, str, str, str]] = [
    # FEEDS: A produces a resource B consumes
    ("lifegain",    "lifegain",    "FEEDS",    "{a} gains life -> {b} cares about life gain"),
    ("token",       "token",       "FEEDS",    "{a} creates tokens -> {b} benefits from tokens"),
    ("token",       "pump",        "FEEDS",    "{a} creates tokens -> {b} pumps them"),
    ("token",       "tribal",      "FEEDS",    "{a} creates tokens -> {b} tribal bonus"),
    ("ramp",        "ramp",        "FEEDS",    "{a} ramps -> {b} needs extra mana"),
    ("mill",        "mill",        "FEEDS",    "{a} mills -> {b} also mills (stack effect)"),
    ("draw",        "draw",        "FEEDS",    "{a} draws -> {b} rewards card draw"),
    ("pump",        "pump",        "FEEDS",    "{a} adds counters -> {b} scales with counters"),
    ("discard",     "reanimation", "FEEDS",    "{a} fills graveyard -> {b} reanimates"),
    ("etb",         "etb",         "FEEDS",    "{a} ETB trigger -> {b} cares about ETBs"),
    ("etb",         "bounce",      "FEEDS",    "{a} ETB value -> {b} bounces to reuse ETB"),

    # TRIGGERS: A's action matches B's trigger condition
    ("lifegain",    "draw",        "TRIGGERS", "{a} gains life -> {b} draws on life gain"),
    ("lifegain",    "pump",        "TRIGGERS", "{a} gains life -> {b} gets counters on life gain"),
    ("lifegain",    "token",       "TRIGGERS", "{a} gains life -> {b} creates tokens on life gain"),
    ("token",       "draw",        "TRIGGERS", "{a} creates tokens -> {b} draws on token creation"),
    ("mill",        "draw",        "TRIGGERS", "{a} mills -> {b} triggers from graveyard"),
    ("etb",         "draw",        "TRIGGERS", "{a} enters -> {b} draws on ETB"),
    ("removal",     "draw",        "TRIGGERS", "{a} removes -> {b} draws on spell cast"),
    ("counter",     "draw",        "TRIGGERS", "{a} counters -> {b} draws on counter"),

    # ENABLES: A makes B functional or cheaper
    ("ramp",        "pump",        "ENABLES",  "{a} produces mana -> {b} activated ability"),
    ("ramp",        "token",       "ENABLES",  "{a} produces mana -> {b} activated ability"),
    ("ramp",        "wipe",        "ENABLES",  "{a} produces mana -> {b} expensive wipe"),
    ("protection",  "tribal",      "ENABLES",  "{a} protects -> {b} tribal engine survives"),
    ("protection",  "pump",        "ENABLES",  "{a} protects -> {b} pump payoff survives"),
    ("tutor",       "draw",        "ENABLES",  "{a} tutors -> {b} is the key piece found"),

    # AMPLIFIES: A multiplies B's output
    ("pump",        "tribal",      "AMPLIFIES", "{a} pumps -> {b} tribal anthem stacks"),
    ("token",       "wipe",        "AMPLIFIES", "{a} tokens -> {b} sacrifice/wipe synergy"),

    # PROTECTS
    ("protection",  "removal",     "PROTECTS",  "{a} hexproof/indestructible -> {b} survives wrath"),
    ("counter",     "protection",  "PROTECTS",  "{a} counters removal -> {b} key piece protected"),
    ("bounce",      "counter",     "PROTECTS",  "{a} bounces threats -> {b} counters follow-ups"),
]

# Tags that define a "role" — cards sharing the same primary role are REDUNDANT
ROLE_TAGS = [
    "wipe", "counter", "tutor", "reanimation", "mill",
    "removal", "draw", "ramp", "pump", "lifegain",
]

# ---------------------------------------------------------------------------
# Card loading
# ---------------------------------------------------------------------------

def load_cards_from_db(names: List[str], paths: RepoPaths) -> Dict[str, Dict]:
    """Look up card data from the local CSV database by name."""
    target = {n.lower(): n for n in names}
    found: Dict[str, Dict] = {}

    for card_type in CARD_TYPES:
        type_dir = paths.cards_dir / card_type
        if not type_dir.exists():
            continue
        for csv_file in sorted(type_dir.glob("*.csv")):
            try:
                with open(csv_file, encoding="utf-8") as f:
                    for row in csv.DictReader(f):
                        name_lower = row.get("name", "").lower()
                        if name_lower in target and name_lower not in found:
                            found[name_lower] = row
                            if len(found) == len(target):
                                return found
            except Exception:
                continue

    return found


# Matches the search_cards.py table output: lines starting with 2 spaces then a card name
# Format:  "  Card Name"  followed by "    Mana: ..." on the next line
_SEARCH_OUTPUT_CARD_RE = re.compile(r"^  ([A-Z][^\n]{1,60})$", re.MULTILINE)

# Matches Gate 3 table rows: | 4 | Card Name | ... |
_GATE3_ROW_RE = re.compile(r"\|\s*(\d+)\s*\|\s*([^|\n]{2,60})\s*\|")

# Column headers to skip
_SKIP_HEADERS = {
    "card name", "card", "qty", "quantity", "mana", "source file",
    "set/collector", "role/justification", "role", "color", "total pips",
    "key cards", "required sources", "actual sources", "status",
    "land name", "colors produced",
}


def extract_names_from_session(content: str) -> List[str]:
    """
    Extract unique card names from a session.md by parsing:
    1. search_cards.py table output inside fenced code blocks (indented "  Card Name" lines)
    2. Gate 3 card selection tables (| Qty | Card Name | ... |)
    """
    names: List[str] = []
    seen: Set[str] = set()

    def add(name: str):
        key = name.lower().strip()
        if key and key not in seen and len(key) >= 3:
            seen.add(key)
            names.append(name.strip())

    # 1. Parse search_cards.py output inside fenced code blocks
    # Find all code blocks and scan for the indented card name pattern
    code_blocks = re.findall(r"```[^\n]*\n(.*?)```", content, re.DOTALL)
    for block in code_blocks:
        lines = block.splitlines()
        for i, line in enumerate(lines):
            # search_cards output: "  CardName" (2 leading spaces, starts with capital)
            m = re.match(r"^  ([A-Z][^\n]{1,60})$", line)
            if not m:
                continue
            candidate = m.group(1).strip()
            # Confirm it looks like a card name: next line should have "Mana:" or "Type:"
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if "Mana:" in next_line or "Type:" in next_line or "CMC:" in next_line:
                add(candidate)

    # 2. Parse Gate 3 / Gate 5 card selection tables
    # Look for sections after "# GATE 3" or "# GATE 5"
    gate_sections = re.split(r"# GATE [35][^#]*", content)
    for section in gate_sections[1:]:  # skip everything before Gate 3
        for line in section.splitlines():
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) < 3:
                continue
            # First cell is quantity, second is card name
            qty_cell = parts[0]
            name_cell = parts[1] if len(parts) > 1 else ""
            # Skip header/separator rows
            if name_cell.lower() in _SKIP_HEADERS:
                continue
            if re.match(r"^-+$", name_cell):
                continue
            # Skip empty template rows
            if not name_cell or name_cell in ("", " "):
                continue
            # qty must be a number or empty
            if qty_cell and not re.match(r"^\d+$", qty_cell.strip()):
                continue
            # Name must start with a capital letter and look like a card name
            if re.match(r"^[A-Z][a-zA-Z',\- ]{1,50}$", name_cell):
                add(name_cell)

    return names


def extract_names_from_decklist(path: Path) -> List[str]:
    """Extract mainboard + sideboard card names from a decklist.txt."""
    main, side = parse_decklist(path)
    return [name for _, name in main + side]


def extract_names_from_text(content: str) -> List[str]:
    """One card name per line."""
    names = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("//"):
            names.append(line)
    return names


# ---------------------------------------------------------------------------
# Synergy scoring
# ---------------------------------------------------------------------------

def score_pairwise(cards: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    For each card, compute:
      - synergy_count: number of distinct partners with a non-REDUNDANT interaction
      - role_breadth: number of distinct interaction types
      - dependency: number of cards this card hard-requires on board to function
      - interactions: list of (partner_name, type, note) tuples
      - redundant_with: list of card names that are REDUNDANT partners
    """
    # Compute tags for every card
    card_tags: Dict[str, Set[str]] = {}
    for name, data in cards.items():
        card_tags[name] = compute_tags(data)

    scores: Dict[str, Dict] = {
        name: {
            "tags": card_tags[name],
            "synergy_partners": set(),
            "role_breadth_types": set(),
            "dependency": 0,
            "interactions": [],
            "redundant_with": [],
        }
        for name in cards
    }

    names = list(cards.keys())

    for i, name_a in enumerate(names):
        tags_a = card_tags[name_a]
        for name_b in names[i + 1:]:
            tags_b = card_tags[name_b]

            # Check interaction rules A->B
            for tag_a, tag_b, itype, note_tmpl in INTERACTION_RULES:
                if tag_a in tags_a and tag_b in tags_b:
                    note = note_tmpl.format(a=name_a, b=name_b)
                    scores[name_a]["interactions"].append((name_b, itype, note))
                    if itype != "REDUNDANT":
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_a]["role_breadth_types"].add(itype)
                        scores[name_b]["role_breadth_types"].add(itype)
                    else:
                        scores[name_a]["redundant_with"].append(name_b)
                        scores[name_b]["redundant_with"].append(name_a)

            # Check B->A direction too
            for tag_a, tag_b, itype, note_tmpl in INTERACTION_RULES:
                if tag_a in tags_b and tag_b in tags_a:
                    note = note_tmpl.format(a=name_b, b=name_a)
                    scores[name_b]["interactions"].append((name_a, itype, note))
                    if itype != "REDUNDANT":
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_a]["role_breadth_types"].add(itype)
                        scores[name_b]["role_breadth_types"].add(itype)
                    else:
                        if name_a not in scores[name_b]["redundant_with"]:
                            scores[name_b]["redundant_with"].append(name_a)
                        if name_b not in scores[name_a]["redundant_with"]:
                            scores[name_a]["redundant_with"].append(name_b)

            # REDUNDANT check: same role tag
            shared_roles = tags_a & tags_b & set(ROLE_TAGS)
            if shared_roles:
                for name in (name_a, name_b):
                    other = name_b if name == name_a else name_a
                    if other not in scores[name]["redundant_with"]:
                        scores[name]["redundant_with"].append(other)
                        scores[name]["interactions"].append(
                            (other, "REDUNDANT", f"Both share role: {', '.join(shared_roles)}")
                        )

    # Finalize counts
    pool_size = len(cards)
    max_possible = max(pool_size - 1, 1)  # maximum partners any card could have

    for name in scores:
        sc = scores[name]
        sc["synergy_count"] = len(sc["synergy_partners"])
        # Normalized density: fraction of pool this card interacts with (0.0-1.0)
        sc["synergy_density"] = sc["synergy_count"] / max_possible
        sc["role_breadth"] = len(sc["role_breadth_types"])
        # Dependency heuristic: cards with 0 tags that produce value alone = 0 dependency
        # Cards whose only tags are "protection" or "pump" (need target) = 1
        dep = 0
        tags = sc["tags"]
        if tags == {"protection"} or tags == {"pump"}:
            dep = 1
        if not tags:
            dep = 0
        sc["dependency"] = dep

    return scores


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

# Density-based thresholds (pool-size invariant).
# A synergy_density of X means a card interacts with X fraction of the pool.
# Thresholds are calibrated so a 10-card, 60-card, or 300-card pool all
# use the same bar — cards must actually fit the deck strategy, not just
# exist in a large pool.
DENSITY_THRESHOLDS = {
    "min_avg_density":    0.30,   # average card interacts with >= 30% of pool
    "max_isolated_frac":  0.10,   # at most 10% of pool may have density <= 0.05
    "min_hub_density":    0.50,   # hub = card interacts with >= 50% of pool
    "min_hub_count":      2,      # at least 2 such hub cards required
}


def check_thresholds(scores: Dict[str, Dict], min_avg: float) -> Tuple[bool, List[str]]:
    """Check all Gate 2.5 thresholds using pool-size-normalized density. Returns (all_passed, list_of_messages)."""
    msgs = []
    passed = True

    if not scores:
        return False, ["No cards to evaluate."]

    pool_size = len(scores)
    densities = [s["synergy_density"] for s in scores.values()]
    avg_density = sum(densities) / len(densities)

    dt = DENSITY_THRESHOLDS

    # T1: average density >= 30%
    if avg_density >= dt["min_avg_density"]:
        msgs.append(
            f"[PASS] T1: Avg Synergy Density = {avg_density:.1%} "
            f"(pool={pool_size}, threshold >= {dt['min_avg_density']:.0%})"
        )
    else:
        msgs.append(
            f"[FAIL] T1: Avg Synergy Density = {avg_density:.1%} "
            f"(pool={pool_size}, need >= {dt['min_avg_density']:.0%})"
        )
        passed = False

    # T2: at most 10% of pool may be isolated (density <= 5%)
    isolated = [n for n, s in scores.items() if s["synergy_density"] <= 0.05]
    max_isolated = max(1, int(pool_size * dt["max_isolated_frac"]))
    if len(isolated) <= max_isolated:
        msgs.append(
            f"[PASS] T2: {len(isolated)} isolated cards (density <= 5%) — "
            f"max allowed {max_isolated} ({dt['max_isolated_frac']:.0%} of {pool_size})"
        )
    else:
        msgs.append(
            f"[FAIL] T2: {len(isolated)} isolated cards (density <= 5%) — "
            f"max allowed {max_isolated}: {', '.join(isolated[:5])}"
        )
        passed = False

    # T3: at least 2 hub cards with density >= 50%
    hubs = [n for n, s in scores.items() if s["synergy_density"] >= dt["min_hub_density"]]
    if len(hubs) >= dt["min_hub_count"]:
        msgs.append(
            f"[PASS] T3: {len(hubs)} hub cards (density >= {dt['min_hub_density']:.0%}): "
            f"{', '.join(hubs[:4])}{'...' if len(hubs) > 4 else ''}"
        )
    else:
        msgs.append(
            f"[FAIL] T3: Only {len(hubs)} hub card(s) with density >= {dt['min_hub_density']:.0%} "
            f"(need {dt['min_hub_count']}+)"
        )
        passed = False

    # T4: no high-dependency cards
    high_dep = [n for n, s in scores.items() if s["dependency"] >= 3]
    if not high_dep:
        msgs.append("[PASS] T4: No cards with Dependency >= 3")
    else:
        msgs.append(f"[FAIL] T4: {len(high_dep)} card(s) with Dependency >= 3: {', '.join(high_dep)}")
        passed = False

    return passed, msgs


def build_report(
    scores: Dict[str, Dict],
    threshold_msgs: List[str],
    all_passed: bool,
    source_file: str,
    not_found: List[str],
) -> str:
    lines = [
        "# Gate 2.5: Synergy Evaluation",
        "",
        f"> Auto-generated by `scripts/synergy_analysis.py` from `{source_file}`",
        "> Tag-based scoring only — review ENABLES/TRIGGERS/AMPLIFIES manually for oracle text nuances.",
        "",
        "---",
        "",
        "## Synergy Scores",
        "",
        "| Card | Tags | Synergy Count (Density) | Role Breadth | Dependency | Key Interactions |",
        "|------|------|:---:|:---:|:---:|-----------------|",
    ]

    sorted_cards = sorted(scores.items(), key=lambda x: -x[1]["synergy_count"])
    for name, sc in sorted_cards:
        tags_str = ", ".join(sorted(sc["tags"])) or "—"
        partners = list(sc["synergy_partners"])[:3]
        partner_str = ", ".join(partners) + ("..." if len(sc["synergy_partners"]) > 3 else "")
        density_str = f"{sc['synergy_density']:.0%}"
        lines.append(
            f"| {name} | {tags_str} | {sc['synergy_count']} ({density_str}) "
            f"| {sc['role_breadth']} | {sc['dependency']} | {partner_str or '—'} |"
        )

    if not_found:
        lines += [
            "",
            f"> **Note:** {len(not_found)} card(s) not found in local database — scored as 0 tags:",
            f"> {', '.join(not_found[:10])}{'...' if len(not_found) > 10 else ''}",
        ]

    pool_size = len(scores)
    counts = [s["synergy_count"] for s in scores.values()]
    densities = [s["synergy_density"] for s in scores.values()]
    avg = sum(counts) / len(counts) if counts else 0
    avg_density = sum(densities) / len(densities) if densities else 0.0
    isolated = [n for n, s in scores.items() if s["synergy_density"] <= 0.05]
    max_isolated = max(1, int(pool_size * DENSITY_THRESHOLDS["max_isolated_frac"]))
    hubs = [n for n, s in scores.items() if s["synergy_density"] >= DENSITY_THRESHOLDS["min_hub_density"]]

    lines += [
        "",
        f"**Pool size:** {pool_size}",
        f"**Avg Synergy Count (raw):** {avg:.1f}  |  **Avg Synergy Density:** {avg_density:.1%} (threshold: >= {DENSITY_THRESHOLDS['min_avg_density']:.0%})",
        f"**Isolated cards (density <= 5%):** {len(isolated)} (max: {max_isolated})",
        f"**Hub cards (density >= 50%):** {len(hubs)} (min: {DENSITY_THRESHOLDS['min_hub_count']})"
        + (f" — {', '.join(hubs[:6])}{'...' if len(hubs) > 6 else ''}" if hubs else ""),
        "",
        "---",
        "",
        "## Gate 2.5 Threshold Check",
        "",
    ]

    for msg in threshold_msgs:
        prefix = "- [x]" if msg.startswith("[PASS]") else "- [ ]"
        lines.append(f"{prefix} {msg}")

    overall = "[PASS] All thresholds met — proceed to Gate 3." if all_passed else \
              "[FAIL] One or more thresholds failed — revisit candidate pool before Gate 3."
    lines += ["", f"**Overall: {overall}**", ""]

    # Redundant pairs
    seen_pairs: Set[frozenset] = set()
    redundant_pairs = []
    for name, sc in scores.items():
        for partner in sc["redundant_with"]:
            pair = frozenset([name, partner])
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                # Find shared roles
                shared = sc["tags"] & scores[partner]["tags"] & set(ROLE_TAGS)
                redundant_pairs.append((name, partner, shared))

    if redundant_pairs:
        lines += [
            "---",
            "",
            "## Redundant Pairs",
            "",
            "| Card A | Card B | Shared Role | Justification for Both |",
            "|--------|--------|-------------|------------------------|",
        ]
        for a, b, roles in redundant_pairs[:20]:
            role_str = ", ".join(roles) if roles else "same role"
            lines.append(f"| {a} | {b} | {role_str} | *(fill in)* |")
        lines.append("")

    # Synergy chains scaffold
    lines += [
        "---",
        "",
        "## Synergy Chains",
        "",
        "> Map 2-3 chains below. Use hub cards as anchors.",
        "> Format: [Card A] -> [what A produces] -> [Card B] -> [outcome]",
        "",
    ]
    for i, (hub_name, _) in enumerate([x for x in sorted_cards if x[1]["synergy_count"] >= 4][:3], 1):
        partners = list(scores[hub_name]["synergy_partners"])[:2]
        chain = f"[{hub_name}] -> [output] -> [{partners[0]}]" if partners else f"[{hub_name}] -> [output]"
        lines += [
            f"**Chain {i} — [{hub_name} engine]:**",
            chain,
            "Redundancy: *(fill in)*",
            "Minimum pieces to function: N of M",
            "",
        ]
    if not [x for x in sorted_cards if x[1]["synergy_count"] >= 4]:
        lines += [
            "**Chain 1:**",
            "[Card A] -> [output] -> [Card B] -> [outcome]",
            "Redundancy: *(fill in)*",
            "Minimum pieces to function: N of M",
            "",
        ]

    lines += [
        "---",
        "",
        "## Gate 2.5 Checklist",
        "",
        f"- [{'x' if all_passed else ' '}] All candidates scored (Synergy Count, Role Breadth, Dependency)",
        f"- [{'x' if avg_density >= DENSITY_THRESHOLDS['min_avg_density'] else ' '}] Avg Synergy Density >= {DENSITY_THRESHOLDS['min_avg_density']:.0%}",
        f"- [{'x' if len(isolated) <= max_isolated else ' '}] <= {max_isolated} isolated cards (density <= 5%)",
        f"- [{'x' if len(hubs) >= DENSITY_THRESHOLDS['min_hub_count'] else ' '}] >= {DENSITY_THRESHOLDS['min_hub_count']} hub cards (density >= 50%)",
        "- [ ] No card with Dependency >= 3  *(verify manually)*",
        "- [ ] All REDUNDANT pairs justified  *(fill in above)*",
        "- [ ] 2-3 synergy chains mapped  *(fill in above)*",
        "- [ ] All analysis based on Gate 1 query results — not memory",
        "",
        "**If any item is unchecked, do not proceed to Gate 3.**",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(
        description="Gate 2.5 synergy analysis — tag-based pairwise scoring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("input_file", help="session.md, decklist.txt, or names list")
    p.add_argument("--format", choices=["auto", "session", "decklist", "names"],
                   default="auto", help="Input format (default: auto-detect)")
    p.add_argument("--output", help="Write report to this file (default: stdout)")
    p.add_argument("--min-synergy", type=float, default=3.0,
                   help="Minimum average synergy count threshold (default: 3.0)")
    args = p.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found.", file=sys.stderr)
        sys.exit(2)

    content = input_path.read_text(encoding="utf-8")

    # Auto-detect format
    fmt = args.format
    if fmt == "auto":
        if "session.md" in input_path.name.lower() or "# Deck Building Session" in content:
            fmt = "session"
        elif "Deck\n" in content or content.strip().startswith("Deck"):
            fmt = "decklist"
        else:
            fmt = "names"

    if fmt == "session":
        names = extract_names_from_session(content)
    elif fmt == "decklist":
        names = extract_names_from_decklist(input_path)
    else:
        names = extract_names_from_text(content)

    # Deduplicate preserving order
    seen: Set[str] = set()
    unique_names = []
    for n in names:
        if n.lower() not in seen:
            seen.add(n.lower())
            unique_names.append(n)

    if not unique_names:
        print("ERROR: No card names extracted from input.", file=sys.stderr)
        sys.exit(2)

    print(f"Loaded {len(unique_names)} unique cards from {input_path.name}", file=sys.stderr)
    print("Looking up card data in local database...", file=sys.stderr)

    paths = RepoPaths()
    card_data = load_cards_from_db(unique_names, paths)
    not_found = [n for n in unique_names if n.lower() not in card_data]

    if not_found:
        print(f"  {len(not_found)} card(s) not found in DB (will score as 0 tags): "
              f"{', '.join(not_found[:5])}", file=sys.stderr)

    # Add zero-tag placeholders for not-found cards
    for name in not_found:
        card_data[name.lower()] = {"name": name}

    print("Scoring pairwise synergies...", file=sys.stderr)
    scores = score_pairwise(card_data)
    all_passed, threshold_msgs = check_thresholds(scores, args.min_synergy)

    report = build_report(
        scores, threshold_msgs, all_passed,
        str(input_path), not_found,
    )

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
