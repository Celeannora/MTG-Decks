#!/usr/bin/env python3
"""
Deck Scaffold Generator — Local Workflow Support

Generates a single consolidated session file that walks through the full
gate system (Gates 1–6) for a new deck. Designed for users running the
deck-building process locally with any AI tool that has limited tool access.

The scaffold:
  1. Runs search_cards.py queries based on your archetype/colors
  2. Embeds all candidate pool results directly into the session file
  3. Stubs out every required gate section (strategy, synergy, selection, etc.)
  4. Pre-populates the deck folder structure
  5. Consolidates ALL output into a single session file for easy AI context

Usage:
    python scripts/generate_deck_scaffold.py --name "Orzhov Lifegain" --colors WB --archetype lifegain
    python scripts/generate_deck_scaffold.py --name "Simic Frog Tribal" --colors GU --archetype tribal --tribe Frog
    python scripts/generate_deck_scaffold.py --name "Dimir Control" --colors UB --archetype control
    python scripts/generate_deck_scaffold.py --name "Boros Aggro" --colors WR --archetype aggro

Flags:
    --name          Deck name (used for folder naming)
    --colors        Color identity: W, U, B, R, G, WB, WUB, etc.
    --archetype     Deck archetype: aggro, midrange, control, combo, mill,
                    lifegain, tribal, ramp, tempo, burn
    --tribe         (Optional) Creature subtype for tribal builds (e.g. Frog, Angel)
    --date          (Optional) Date override (default: today, YYYY-MM-DD)
    --output-dir    (Optional) Output directory override (default: Decks/)
    --extra-tags    (Optional) Additional search tags, comma-separated
    --skip-queries  (Optional) Generate scaffold without running queries
                    (for offline template use)

Output:
    Decks/YYYY-MM-DD_Deck_Name/
    ├── session.md          ← THE SINGLE CONSOLIDATED FILE (all work goes here)
    ├── decklist.txt        ← Empty template (filled during Gate 3)
    ├── analysis.md         ← Empty template (filled after all gates)
    └── sideboard_guide.md  ← Empty template (filled after Gate 5)

Exit codes:
    0  Scaffold generated successfully
    1  Invalid arguments
    2  cards_by_category/ not found
"""

import argparse
import csv
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ─── Archetype → query plan mapping ──────────────────────────────────────────

ARCHETYPE_QUERIES: Dict[str, List[Dict[str, str]]] = {
    "aggro": [
        {"label": "Aggressive creatures",         "args": "--type creature --tags haste,pump,trample --cmc-max 3"},
        {"label": "Cheap creatures",               "args": "--type creature --cmc-max 2"},
        {"label": "Removal instants",              "args": "--type instant --tags removal --cmc-max 3"},
        {"label": "Combat tricks / pump",          "args": "--type instant --tags pump --cmc-max 2"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "midrange": [
        {"label": "Value creatures (2-4 CMC)",     "args": "--type creature --cmc-min 2 --cmc-max 4"},
        {"label": "Top-end threats (5+ CMC)",      "args": "--type creature --cmc-min 5 --rarity rare,mythic"},
        {"label": "Removal",                       "args": "--type instant,sorcery --tags removal"},
        {"label": "Card advantage",                "args": "--type instant,sorcery,enchantment --tags draw"},
        {"label": "Planeswalkers",                 "args": "--type planeswalker"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "control": [
        {"label": "Counterspells",                 "args": "--type instant --tags counter"},
        {"label": "Removal instants",              "args": "--type instant --tags removal"},
        {"label": "Board wipes",                   "args": "--type sorcery --tags wipe"},
        {"label": "Card draw",                     "args": "--type instant,sorcery --tags draw"},
        {"label": "Win conditions",                "args": "--type creature,planeswalker --cmc-min 4 --rarity rare,mythic"},
        {"label": "Enchantments",                  "args": "--type enchantment"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "combo": [
        {"label": "Combo creatures",               "args": "--type creature --tags etb,draw,tutor"},
        {"label": "Combo spells",                  "args": "--type instant,sorcery --tags tutor,draw"},
        {"label": "Enabler artifacts",             "args": "--type artifact --tags ramp,draw"},
        {"label": "Enabler enchantments",          "args": "--type enchantment"},
        {"label": "Protection / counters",         "args": "--type instant --tags counter,protection"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "mill": [
        {"label": "Mill creatures",                "args": "--type creature --tags mill"},
        {"label": "Mill instants/sorceries",       "args": "--type instant,sorcery --tags mill"},
        {"label": "Mill enchantments",             "args": "--type enchantment --tags mill"},
        {"label": "Mill artifacts",                "args": "--type artifact --tags mill"},
        {"label": "Counterspells",                 "args": "--type instant --tags counter"},
        {"label": "Removal",                       "args": "--type instant --tags removal"},
        {"label": "Card draw",                     "args": "--type instant,sorcery --tags draw"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "lifegain": [
        {"label": "Lifegain creatures",            "args": "--type creature --tags lifegain"},
        {"label": "Lifegain payoffs",              "args": "--type creature --oracle \"whenever you gain life\""},
        {"label": "Lifegain spells",               "args": "--type instant,sorcery --tags lifegain"},
        {"label": "Lifegain enchantments",         "args": "--type enchantment --tags lifegain"},
        {"label": "Removal",                       "args": "--type instant --tags removal --cmc-max 3"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "tribal": [
        {"label": "Tribal creatures (by subtype)", "args": "--type creature"},
        {"label": "Tribal support",                "args": "--type instant,sorcery,enchantment --tags tribal,pump"},
        {"label": "Removal",                       "args": "--type instant --tags removal --cmc-max 3"},
        {"label": "Card draw",                     "args": "--type instant,sorcery,enchantment --tags draw"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "ramp": [
        {"label": "Ramp creatures",                "args": "--type creature --tags ramp"},
        {"label": "Ramp spells",                   "args": "--type instant,sorcery --tags ramp"},
        {"label": "Ramp artifacts",                "args": "--type artifact --tags ramp"},
        {"label": "Top-end payoffs",               "args": "--type creature,planeswalker --cmc-min 5 --rarity rare,mythic"},
        {"label": "Removal",                       "args": "--type instant,sorcery --tags removal"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "tempo": [
        {"label": "Efficient creatures",           "args": "--type creature --cmc-max 3 --tags flash,flying"},
        {"label": "Bounce spells",                 "args": "--type instant --tags bounce"},
        {"label": "Counterspells",                 "args": "--type instant --tags counter --cmc-max 3"},
        {"label": "Cheap removal",                 "args": "--type instant --tags removal --cmc-max 2"},
        {"label": "Card draw",                     "args": "--type instant --tags draw --cmc-max 3"},
        {"label": "Lands",                         "args": "--type land"},
    ],
    "burn": [
        {"label": "Burn spells",                   "args": "--type instant,sorcery --tags removal --oracle \"damage\""},
        {"label": "Aggressive creatures",          "args": "--type creature --tags haste --cmc-max 3"},
        {"label": "Reach / finisher spells",       "args": "--type instant,sorcery --oracle \"each opponent\" --cmc-max 4"},
        {"label": "Lands",                         "args": "--type land"},
    ],
}


def run_query(
    repo_root: Path,
    base_args: str,
    colors: str,
    tribe: Optional[str] = None,
    extra_tags: Optional[str] = None,
) -> Tuple[str, str, int]:
    """
    Run a search_cards.py query. Returns (command_string, output, result_count).
    Adds --colors and --show-tags automatically.
    """
    from mtg_utils import RepoPaths
    paths = RepoPaths(root=repo_root)
    script = paths.scripts_dir / "search_cards.py"
    cmd_parts = [sys.executable, str(script)]
    cmd_parts += base_args.split()

    # Add colors if not a land query (lands should search across all colors)
    if "--type land" not in base_args:
        cmd_parts += ["--colors", colors]
    else:
        cmd_parts += ["--colors", colors]

    # For tribal, add --oracle filter for the tribe name on creature queries
    if tribe and "--type creature" in base_args and "--oracle" not in base_args:
        cmd_parts += ["--oracle", tribe]

    cmd_parts += ["--show-tags", "--format", "table", "--limit", "100"]

    # Add extra tags if provided
    if extra_tags:
        # Check if --tags already in args
        if "--tags" in base_args:
            # Merge: find existing --tags value and append
            pass  # handled by user in base_args
        else:
            cmd_parts += ["--tags", extra_tags]

    cmd_str = " ".join(cmd_parts)
    display_cmd = cmd_str.replace(str(script), "search_cards.py")
    display_cmd = display_cmd.replace(sys.executable + " ", "python ")

    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            cwd=str(repo_root),
            timeout=60,
        )
        output = result.stdout or result.stderr or "(no output)"

        # Count results from output
        count = 0
        for line in output.splitlines():
            if "Total candidates:" in line:
                try:
                    count = int(line.split(":")[-1].strip())
                except ValueError:
                    pass
            elif "No cards matched" in line:
                count = 0

        return display_cmd, output, count

    except subprocess.TimeoutExpired:
        return display_cmd, "(query timed out after 60s)", 0
    except FileNotFoundError:
        return display_cmd, "(search_cards.py not found)", 0


def sanitize_folder_name(name: str) -> str:
    """Convert deck name to folder-safe format."""
    return name.replace(" ", "_").replace("/", "_").replace("\\", "_")


def generate_session_file(
    deck_date: str,
    deck_name: str,
    colors: str,
    archetype: str,
    query_results: List[Dict],
    tribe: Optional[str] = None,
) -> str:
    """Generate the consolidated session.md content."""
    from mtg_utils import RepoPaths

    archetype_display = f"{archetype.title()} ({tribe} Tribal)" if tribe else archetype.title()
    color_display = "/".join(colors.upper())

    lines = [
        f"# Deck Building Session: {deck_name}",
        "",
        f"**Date:** {deck_date}",
        f"**Colors:** {color_display}",
        f"**Archetype:** {archetype_display}",
        f"**Format:** Standard",
        "",
        "> This file is the single consolidated workspace for building this deck.",
        "> All gate work, candidate pools, synergy evaluation, and card selections",
        "> go here. When complete, copy the final outputs into decklist.txt,",
        "> analysis.md, and sideboard_guide.md.",
        "",
        "---",
        "",
        "## Pre-Flight Checks",
        "",
        f"- [ ] `{RepoPaths.CARDS_DIR_NAME}/` is present and populated",
        f"- [ ] `{RepoPaths.SCRIPTS_DIR_NAME}/search_cards.py` runs without errors",
        f"- [ ] `{RepoPaths.SCRIPTS_DIR_NAME}/validate_decklist.py` runs without errors",
        "",
        "---",
        "",
        "# GATE 1: DATABASE QUERY — CANDIDATE POOL",
        "",
        "## Queries Run",
        "",
        f"| # | Label | Command | Candidates |",
        f"|---|-------|---------|------------|",
    ]

    for i, qr in enumerate(query_results, 1):
        cmd_short = qr["command"].replace("python ", "").strip()
        lines.append(f"| {i} | {qr['label']} | `{cmd_short}` | {qr['count']} |")

    lines += [
        "",
        "## Full Query Output",
        "",
        "> Below is the complete output from each query. This is your candidate pool.",
        "> DO NOT add any card that does not appear below.",
        "",
    ]

    for i, qr in enumerate(query_results, 1):
        lines += [
            f"### Query {i}: {qr['label']}",
            "",
            f"```",
            f"$ {qr['command']}",
            "",
            qr["output"].rstrip(),
            f"```",
            "",
        ]

    lines += [
        "## Additional Queries",
        "",
        "> If the queries above are insufficient, run more queries and paste results here.",
        "> Every query must use `search_cards.py`. Document the command and output.",
        "",
        "```",
        f"$ python {RepoPaths.SCRIPTS_DIR_NAME}/search_cards.py --type <type> --colors <colors> [flags...]",
        "",
        "(paste output here)",
        "```",
        "",
        "### Gate 1 Checklist",
        "",
        "- [ ] Every needed card type has been queried",
        "- [ ] Complete candidate pool exists from query results above",
        "- [ ] Zero cards have been named from memory or web sources",
        "",
        "---",
        "",
        "# GATE 2: STRATEGY DEFINITION",
        "",
        "## Win Condition",
        "",
        "**Primary win condition:** (fill in)",
        "",
        "**Target win turn:** Turn N",
        "",
        "**Backup plan:** (fill in)",
        "",
        "## Role Map",
        "",
        "| Role | Required | Candidates Available |",
        "|------|----------|---------------------|",
        "| Win condition | ? | (list from pool) |",
        "| Support / engine | ? | (list from pool) |",
        "| Interaction / removal | ? | (list from pool) |",
        "| Card advantage | ? | (list from pool) |",
        "| Mana / ramp | ? | (list from pool) |",
        "| Lands | 22-26 | (list from pool) |",
        "",
        "### Gate 2 Checklist",
        "",
        "- [ ] One primary win condition defined",
        "- [ ] Target win turn identified",
        "- [ ] All roles have candidates from the pool",
        "- [ ] Strategy uses database-confirmed cards only",
        "",
        "---",
        "",
        "# GATE 2.5: SYNERGY EVALUATION",
        "",
        "## Pairwise Interactions",
        "",
        "> For each candidate, classify interactions using:",
        "> ENABLES / TRIGGERS / AMPLIFIES / PROTECTS / FEEDS / REDUNDANT",
        "",
        "## Synergy Scores",
        "",
        "| Card | Synergy Count | Role Breadth | Dependency | Notes |",
        "|------|--------------|-------------|------------|-------|",
        "| (fill in) | | | | |",
        "",
        "**Average Synergy Count:** X.X (threshold: ≥ 3.0)",
        "**Cards with Synergy Count 0–1:** N (max: 4)",
        "**Hub cards (Synergy Count ≥ 8):** N (min: 2)",
        "",
        "## Synergy Chains",
        "",
        "**Chain 1 — [Primary Win Con]:**",
        "[Card A] → [output] → [Card B] → [output] → [Card C] → [outcome]",
        "Redundancy: (fill in)",
        "Minimum pieces to function: N of M",
        "",
        "**Chain 2 — [Secondary / Defensive]:**",
        "(fill in)",
        "",
        "## Redundant Pairs",
        "",
        "| Card A | Card B | Justification for Both |",
        "|--------|--------|------------------------|",
        "| | | |",
        "",
        "### Gate 2.5 Checklist",
        "",
        "- [ ] All candidates scored (Synergy Count, Role Breadth, Dependency)",
        "- [ ] Average Synergy Count ≥ 3.0",
        "- [ ] ≤ 4 cards with Synergy Count 0–1",
        "- [ ] ≥ 2 hub cards with Synergy Count ≥ 8",
        "- [ ] No card with Dependency ≥ 3",
        "- [ ] All REDUNDANT pairs justified",
        "- [ ] 2–3 synergy chains mapped with redundancy and degradation noted",
        "",
        "---",
        "",
        "# GATE 3: CARD SELECTION",
        "",
        "> For every card, cite the source file from the query output above.",
        "> If you cannot cite it, do not include it.",
        "",
        "## Mainboard (60 cards)",
        "",
        "### Creatures",
        "",
        "| Qty | Card Name | Mana | Source File | Set/Collector | Role/Justification |",
        "|-----|-----------|------|------------|---------------|-------------------|",
        "| | | | | | |",
        "",
        "### Instants",
        "",
        "| Qty | Card Name | Mana | Source File | Set/Collector | Role/Justification |",
        "|-----|-----------|------|------------|---------------|-------------------|",
        "| | | | | | |",
        "",
        "### Sorceries",
        "",
        "| Qty | Card Name | Mana | Source File | Set/Collector | Role/Justification |",
        "|-----|-----------|------|------------|---------------|-------------------|",
        "| | | | | | |",
        "",
        "### Enchantments",
        "",
        "| Qty | Card Name | Mana | Source File | Set/Collector | Role/Justification |",
        "|-----|-----------|------|------------|---------------|-------------------|",
        "| | | | | | |",
        "",
        "### Artifacts",
        "",
        "| Qty | Card Name | Mana | Source File | Set/Collector | Role/Justification |",
        "|-----|-----------|------|------------|---------------|-------------------|",
        "| | | | | | |",
        "",
        "### Planeswalkers",
        "",
        "| Qty | Card Name | Mana | Source File | Set/Collector | Role/Justification |",
        "|-----|-----------|------|------------|---------------|-------------------|",
        "| | | | | | |",
        "",
        "### Gate 3 Checklist",
        "",
        "- [ ] All 60 mainboard cards have a cited source file",
        "- [ ] Every card came from Gate 1 query results",
        "- [ ] Zero cards sourced from web or memory",
        "",
        "---",
        "",
        "# GATE 4: MANA BASE",
        "",
        "## Colored Pip Count",
        "",
        "| Color | Total Pips | Key Cards |",
        "|-------|-----------|-----------|",
        "| | | |",
        "",
        "## Land Selection",
        "",
        "| Qty | Land Name | Source File | Set/Collector | Colors Produced |",
        "|-----|-----------|------------|---------------|-----------------|",
        "| | | | | |",
        "",
        "## Karsten Validation",
        "",
        "| Color | Required Sources | Actual Sources | Status |",
        "|-------|-----------------|----------------|--------|",
        "| | | | |",
        "",
        "### Gate 4 Checklist",
        "",
        "- [ ] Colored pips counted",
        "- [ ] Land sources meet Karsten requirements",
        "- [ ] All lands have cited source files",
        "- [ ] Curve is supported (enough early sources for 1-2 drops)",
        "",
        "---",
        "",
        "# GATE 5: SIDEBOARD",
        "",
        "## Sideboard (15 cards)",
        "",
        "| Qty | Card Name | Mana | Source File | Set/Collector | Role / Target Matchup |",
        "|-----|-----------|------|------------|---------------|----------------------|",
        "| | | | | | |",
        "",
        "### Gate 5 Checklist",
        "",
        "- [ ] All 15 sideboard cards have cited source files",
        "- [ ] Covers: aggro, control, midrange, combo matchups",
        "- [ ] No card sourced from web or memory",
        "",
        "---",
        "",
        "# GATE 6: FINAL VALIDATION",
        "",
        "## Validation Command",
        "",
        "```bash",
        f"python {RepoPaths.SCRIPTS_DIR_NAME}/validate_decklist.py {RepoPaths.DECKS_DIR_NAME}/{deck_date}_{sanitize_folder_name(deck_name)}/decklist.txt --verbose",
        "```",
        "",
        "## Validation Output",
        "",
        "```",
        "(paste validation output here)",
        "```",
        "",
        "## Final Checklist",
        "",
        "- [ ] All needed card types were queried (Gate 1)",
        "- [ ] Strategy fully defined (Gate 2)",
        "- [ ] Synergy evaluation completed — thresholds met (Gate 2.5)",
        "- [ ] All 60 mainboard cards have a cited source file (Gate 3)",
        "- [ ] Mana base validated (Gate 4)",
        "- [ ] All 15 sideboard cards have a cited source file (Gate 5)",
        "- [ ] Zero cards sourced from web searches or memory",
        "- [ ] Set codes and collector numbers recorded",
        "- [ ] Validation script returned exit code 0",
        "",
        "---",
        "",
        "# OUTPUT FILES",
        "",
        "> When all gates are complete, copy the finalized content into these files:",
        "",
        "## → decklist.txt",
        "",
        "> Copy your final 60+15 list in MTGA format:",
        "",
        "```",
        "Deck",
        "4 Card Name (SET) Collector_Number",
        "...",
        "",
        "Sideboard",
        "3 Card Name (SET) Collector_Number",
        "...",
        "```",
        "",
        "## → analysis.md",
        "",
        "> Compile your gate work into the analysis.md template.",
        "> Required sections: Database Query Report, Executive Summary,",
        "> Synergy Evaluation, Card-by-Card Breakdown, Mana Base Analysis,",
        "> Curve Analysis, Matchup Table, Weaknesses, Playtesting Notes.",
        "",
        "## → sideboard_guide.md",
        "",
        "> Write boarding plans for each major matchup.",
        "",
        "---",
        "",
        f"_Generated by `{RepoPaths.SCRIPTS_DIR_NAME}/generate_deck_scaffold.py` on {deck_date}_",
        "",
    ]

    return "\n".join(lines)


def generate_decklist_template() -> str:
    return "\n".join([
        "Deck",
        "// Creatures",
        "",
        "// Instants",
        "",
        "// Sorceries",
        "",
        "// Enchantments",
        "",
        "// Artifacts",
        "",
        "// Planeswalkers",
        "",
        "// Lands",
        "",
        "",
        "Sideboard",
        "",
    ])


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate a deck-building session scaffold with embedded query results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--name", required=True, help="Deck name (e.g. 'Orzhov Lifegain')")
    p.add_argument("--colors", required=True, help="Color identity (e.g. WB, GU, WUR)")
    p.add_argument(
        "--archetype", required=True,
        choices=sorted(ARCHETYPE_QUERIES.keys()),
        help="Deck archetype",
    )
    p.add_argument("--tribe", help="Creature subtype for tribal (e.g. Frog, Angel, Elf)")
    p.add_argument("--date", help="Date override (YYYY-MM-DD, default: today)")
    p.add_argument("--output-dir", help="Output directory (default: Decks/)")
    p.add_argument("--extra-tags", help="Additional search tags, comma-separated")
    p.add_argument(
        "--skip-queries", action="store_true",
        help="Generate scaffold without running queries (offline template)",
    )
    return p


def main() -> None:
    from mtg_utils import RepoPaths

    args = build_parser().parse_args()
    paths = RepoPaths()
    repo_root = paths.root

    # Validate card database exists
    if not paths.cards_dir.exists() and not args.skip_queries:
        print(f"ERROR: {RepoPaths.CARDS_DIR_NAME}/ not found.", file=sys.stderr)
        print(f"Run 'python {RepoPaths.SCRIPTS_DIR_NAME}/fetch_and_categorize_cards.py' first.", file=sys.stderr)
        sys.exit(2)

    deck_date = args.date or date.today().isoformat()
    folder_name = f"{deck_date}_{sanitize_folder_name(args.name)}"
    output_base = Path(args.output_dir) if args.output_dir else paths.decks_dir
    deck_dir = output_base / folder_name

    # Create folder
    deck_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'='*70}")
    print(f"  DECK SCAFFOLD GENERATOR")
    print(f"  Name:      {args.name}")
    print(f"  Colors:    {args.colors.upper()}")
    print(f"  Archetype: {args.archetype}")
    if args.tribe:
        print(f"  Tribe:     {args.tribe}")
    print(f"  Output:    {deck_dir}/")
    print(f"{'='*70}\n")

    # Run queries
    query_plan = ARCHETYPE_QUERIES[args.archetype]
    query_results: List[Dict] = []

    if args.skip_queries:
        print("  --skip-queries: Generating template without query results.\n")
        for q in query_plan:
            query_results.append({
                "label": q["label"],
                "command": f"python {RepoPaths.SCRIPTS_DIR_NAME}/search_cards.py {q['args']} --colors {args.colors.upper()} --show-tags",
                "output": "(run this query and paste results here)",
                "count": "?",
            })
    else:
        total_candidates = 0
        for i, q in enumerate(query_plan, 1):
            label = q["label"]
            print(f"  [{i}/{len(query_plan)}] {label}...")

            cmd, output, count = run_query(
                repo_root,
                q["args"],
                args.colors.upper(),
                tribe=args.tribe,
                extra_tags=args.extra_tags,
            )

            query_results.append({
                "label": label,
                "command": cmd,
                "output": output,
                "count": count,
            })
            total_candidates += count
            print(f"         → {count} candidates")

        print(f"\n  Total candidates across all queries: {total_candidates}")

    # Generate session file
    session_content = generate_session_file(
        deck_date=deck_date,
        deck_name=args.name,
        colors=args.colors.upper(),
        archetype=args.archetype,
        query_results=query_results,
        tribe=args.tribe,
    )

    # Write files
    session_path = deck_dir / "session.md"
    session_path.write_text(session_content, encoding="utf-8")
    print(f"\n  ✅ session.md written ({len(session_content):,} bytes)")

    decklist_path = deck_dir / "decklist.txt"
    if not decklist_path.exists():
        decklist_path.write_text(generate_decklist_template(), encoding="utf-8")
        print(f"  ✅ decklist.txt template created")

    # Copy analysis template if it exists
    analysis_template = paths.templates / "analysis.md"
    analysis_path = deck_dir / "analysis.md"
    if not analysis_path.exists():
        if analysis_template.exists():
            analysis_path.write_text(
                analysis_template.read_text(encoding="utf-8"), encoding="utf-8"
            )
        else:
            analysis_path.write_text("# Deck Analysis\n\n(fill in after completing all gates)\n", encoding="utf-8")
        print(f"  ✅ analysis.md template created")

    sb_template = paths.templates / "sideboard_guide.md"
    sb_path = deck_dir / "sideboard_guide.md"
    if not sb_path.exists():
        if sb_template.exists():
            sb_path.write_text(
                sb_template.read_text(encoding="utf-8"), encoding="utf-8"
            )
        else:
            sb_path.write_text("# Sideboard Guide\n\n(fill in after completing Gate 5)\n", encoding="utf-8")
        print(f"  ✅ sideboard_guide.md template created")

    # Display paths — use relative if inside repo, absolute otherwise
    try:
        display_session = session_path.relative_to(repo_root)
        display_decklist = decklist_path.relative_to(repo_root)
    except ValueError:
        display_session = session_path
        display_decklist = decklist_path

    print(f"\n{'='*70}")
    print(f"  SCAFFOLD COMPLETE")
    print(f"")
    print(f"  Next steps:")
    print(f"  1. Open {display_session}")
    print(f"  2. Feed session.md to your AI tool as context")
    print(f"  3. Work through Gates 1–6 inside session.md")
    print(f"  4. Run: python {RepoPaths.SCRIPTS_DIR_NAME}/validate_decklist.py {display_decklist}")
    print(f"  5. Copy final outputs into decklist.txt, analysis.md, sideboard_guide.md")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
