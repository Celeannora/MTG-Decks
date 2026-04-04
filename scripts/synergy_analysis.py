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


def extract_names_from_session(content: str) -> List[str]:
    """
    Extract unique card names from a session.md.
    Looks at: query output blocks (table rows) and Gate 3 selection tables.
    """
    names: List[str] = []
    seen: Set[str] = set()

    # Table rows: | 4 | Card Name | ... | or | Card Name | ... |
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if not parts or parts[0] in ("-", "Qty", "qty", "#", "Card", "card"):
            continue
        # Try each cell as a potential card name (2-5 words, mixed case)
        for cell in parts:
            cell = cell.strip()
            # Strip quantity prefix like "4 " or "3x "
            cell = re.sub(r"^\d+[x ]?\s*", "", cell).strip()
            # Skip cells that look like mana costs, numbers, or long descriptions
            if not cell or len(cell) < 3 or len(cell) > 50:
                continue
            if re.match(r"^[\d{}/WUBRGC]+$", cell):
                continue
            if cell.lower() in seen:
                continue
            seen.add(cell.lower())
            names.append(cell)

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
    for name in scores:
        sc = scores[name]
        sc["synergy_count"] = len(sc["synergy_partners"])
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

def check_thresholds(scores: Dict[str, Dict], min_avg: float) -> Tuple[bool, List[str]]:
    """Check all Gate 2.5 thresholds. Returns (all_passed, list_of_messages)."""
    msgs = []
    passed = True

    counts = [s["synergy_count"] for s in scores.values()]
    if not counts:
        return False, ["No cards to evaluate."]

    avg = sum(counts) / len(counts)
    low_synergy = [n for n, s in scores.items() if s["synergy_count"] <= 1]
    hubs = [n for n, s in scores.items() if s["synergy_count"] >= 8]
    high_dep = [n for n, s in scores.items() if s["dependency"] >= 3]

    # T1
    if avg >= min_avg:
        msgs.append(f"[PASS] T1: Average Synergy Count = {avg:.1f} (>= {min_avg})")
    else:
        msgs.append(f"[FAIL] T1: Average Synergy Count = {avg:.1f} (need >= {min_avg})")
        passed = False

    # T2
    if len(low_synergy) <= 4:
        msgs.append(f"[PASS] T2: {len(low_synergy)} cards with Synergy Count <= 1 (max 4)")
    else:
        msgs.append(f"[FAIL] T2: {len(low_synergy)} cards with Synergy Count <= 1 (max 4): {', '.join(low_synergy[:5])}")
        passed = False

    # T3
    if len(hubs) >= 2:
        msgs.append(f"[PASS] T3: {len(hubs)} hub cards with Synergy Count >= 8: {', '.join(hubs[:4])}")
    else:
        msgs.append(f"[FAIL] T3: Only {len(hubs)} hub card(s) with Synergy Count >= 8 (need 2+)")
        passed = False

    # T4
    if not high_dep:
        msgs.append(f"[PASS] T4: No cards with Dependency >= 3")
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
        "| Card | Tags | Synergy Count | Role Breadth | Dependency | Key Interactions |",
        "|------|------|:---:|:---:|:---:|-----------------|",
    ]

    sorted_cards = sorted(scores.items(), key=lambda x: -x[1]["synergy_count"])
    for name, sc in sorted_cards:
        tags_str = ", ".join(sorted(sc["tags"])) or "—"
        partners = list(sc["synergy_partners"])[:3]
        partner_str = ", ".join(partners) + ("..." if len(sc["synergy_partners"]) > 3 else "")
        lines.append(
            f"| {name} | {tags_str} | {sc['synergy_count']} "
            f"| {sc['role_breadth']} | {sc['dependency']} | {partner_str or '—'} |"
        )

    if not_found:
        lines += [
            "",
            f"> **Note:** {len(not_found)} card(s) not found in local database — scored as 0 tags:",
            f"> {', '.join(not_found[:10])}{'...' if len(not_found) > 10 else ''}",
        ]

    counts = [s["synergy_count"] for s in scores.values()]
    avg = sum(counts) / len(counts) if counts else 0
    hubs = [n for n, s in scores.items() if s["synergy_count"] >= 8]

    lines += [
        "",
        f"**Average Synergy Count:** {avg:.1f} (threshold: >= 3.0)",
        f"**Cards with Synergy Count 0-1:** {sum(1 for c in counts if c <= 1)} (max: 4)",
        f"**Hub cards (Synergy Count >= 8):** {len(hubs)} (min: 2)"
        + (f" — {', '.join(hubs)}" if hubs else ""),
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
        f"- [{'x' if counts and sum(counts)/len(counts) >= 3.0 else ' '}] Average Synergy Count >= 3.0",
        f"- [{'x' if sum(1 for c in counts if c <= 1) <= 4 else ' '}] <= 4 cards with Synergy Count 0-1",
        f"- [{'x' if len(hubs) >= 2 else ' '}] >= 2 hub cards with Synergy Count >= 8",
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
