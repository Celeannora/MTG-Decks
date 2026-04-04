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

# ─── Complete MTG creature type list (Scryfall catalog, 325 types) ─────────────
ALL_CREATURE_TYPES: List[str] = [
    "Advisor", "Aetherborn", "Alien", "Ally", "Angel", "Antelope", "Ape",
    "Archer", "Archon", "Armadillo", "Army", "Artifact", "Artificer",
    "Assassin", "Assembly-Worker", "Astartes", "Atog", "Aurochs", "Automaton",
    "Avatar", "Azra", "Badger", "Balloon", "Barbarian", "Bard", "Basilisk",
    "Bat", "Bear", "Beast", "Beaver", "Beeble", "Beholder", "Berserker",
    "Bird", "Bison", "Blinkmoth", "Boar", "Brainiac", "Bringer", "Brushwagg",
    "C'tan", "Camarid", "Camel", "Capybara", "Caribou", "Carrier", "Cat",
    "Centaur", "Chicken", "Child", "Chimera", "Citizen", "Cleric", "Clown",
    "Cockatrice", "Construct", "Coward", "Coyote", "Crab", "Crocodile",
    "Custodes", "Cyberman", "Cyclops", "Dalek", "Dauthi", "Demigod", "Demon",
    "Deserter", "Detective", "Devil", "Dinosaur", "Djinn", "Doctor", "Dog",
    "Dragon", "Drake", "Dreadnought", "Drix", "Drone", "Druid", "Dryad",
    "Dwarf", "Echidna", "Efreet", "Egg", "Elder", "Eldrazi", "Elemental",
    "Elephant", "Elf", "Elk", "Employee", "Eye", "Faerie", "Ferret", "Fish",
    "Flagbearer", "Fox", "Fractal", "Frog", "Fungus", "Gamer", "Gargoyle",
    "Germ", "Giant", "Gith", "Glimmer", "Gnoll", "Gnome", "Goat", "Goblin",
    "God", "Golem", "Gorgon", "Graveborn", "Gremlin", "Griffin", "Guest",
    "Hag", "Halfling", "Hamster", "Harpy", "Head", "Hedgehog", "Hellion",
    "Hero", "Hippo", "Hippogriff", "Homarid", "Homunculus", "Hornet",
    "Horror", "Horse", "Human", "Hydra", "Hyena", "Illusion", "Imp",
    "Incarnation", "Inkling", "Inquisitor", "Insect", "Jackal", "Jellyfish",
    "Juggernaut", "Kangaroo", "Kavu", "Kirin", "Kithkin", "Knight", "Kobold",
    "Kor", "Kraken", "Lamia", "Lammasu", "Leech", "Lemur", "Leviathan",
    "Lhurgoyf", "Licid", "Lizard", "Lobster", "Manticore", "Masticore",
    "Mercenary", "Merfolk", "Metathran", "Minion", "Minotaur", "Mite",
    "Mole", "Monger", "Mongoose", "Monk", "Monkey", "Moogle", "Moonfolk",
    "Mount", "Mouse", "Mutant", "Myr", "Mystic", "Naga", "Nautilus",
    "Necron", "Nephilim", "Nightmare", "Nightstalker", "Ninja", "Noble",
    "Noggle", "Nomad", "Nymph", "Octopus", "Ogre", "Ooze", "Orb", "Orc",
    "Orgg", "Otter", "Ouphe", "Ox", "Oyster", "Pangolin", "Peasant",
    "Pegasus", "Pentavite", "Performer", "Pest", "Phelddagrif", "Phoenix",
    "Phyrexian", "Pilot", "Pincher", "Pirate", "Plant", "Porcupine",
    "Possum", "Praetor", "Primarch", "Prism", "Processor", "Qu", "Rabbit",
    "Raccoon", "Ranger", "Rat", "Rebel", "Reflection", "Reveler", "Rhino",
    "Rigger", "Robot", "Rogue", "Rukh", "Sable", "Salamander", "Samurai",
    "Sand", "Saproling", "Satyr", "Scarecrow", "Scientist", "Scion",
    "Scorpion", "Scout", "Sculpture", "Seal", "Serf", "Serpent", "Servo",
    "Shade", "Shaman", "Shapeshifter", "Shark", "Sheep", "Siren", "Skeleton",
    "Skunk", "Slith", "Sliver", "Sloth", "Slug", "Snail", "Snake", "Soldier",
    "Soltari", "Spawn", "Specter", "Spellshaper", "Sphinx", "Spider", "Spike",
    "Spirit", "Splinter", "Sponge", "Spy", "Squid", "Squirrel", "Starfish",
    "Surrakar", "Survivor", "Symbiote", "Synth", "Teddy", "Tentacle",
    "Tetravite", "Thalakos", "Thopter", "Thrull", "Tiefling", "Time Lord",
    "Toy", "Treefolk", "Trilobite", "Triskelavite", "Troll", "Turtle",
    "Tyranid", "Unicorn", "Urzan", "Vampire", "Varmint", "Vedalken",
    "Villain", "Volver", "Wall", "Walrus", "Warlock", "Warrior", "Wasp",
    "Weasel", "Weird", "Werewolf", "Whale", "Wizard", "Wolf", "Wolverine",
    "Wombat", "Worm", "Wraith", "Wurm", "Yeti", "Zombie", "Zubera",
]
_CREATURE_TYPES_LOWER: Dict[str, str] = {t.lower(): t for t in ALL_CREATURE_TYPES}


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
    import shlex
    cmd_parts = [sys.executable, str(script)]
    cmd_parts += shlex.split(base_args)

    # Add colors if not a land query (lands should search across all colors)
    if "--type land" not in base_args:
        cmd_parts += ["--colors", colors]
    else:
        cmd_parts += ["--colors", colors]

    # For tribal, filter creature queries by subtype name (--name is safer than
    # --oracle which doesn't support | OR syntax). Only filter if a single tribe
    # is given to avoid over-constraining; for multi-tribe the scaffold emits
    # one query per tribe via the TRIBAL_CREATURE_QUERIES expansion below.
    if tribe and "--type creature" in base_args and "--oracle" not in base_args:
        tribe_list = tribe if isinstance(tribe, list) else [tribe]
        if len(tribe_list) == 1:
            cmd_parts += ["--name", tribe_list[0]]

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

    if tribe:
        tribe_list = tribe if isinstance(tribe, list) else [tribe]
        tribe_display = " / ".join(tribe_list) + " Tribal"
    else:
        tribe_display = None
    archetype_display = f"{archetype.title()} ({tribe_display})" if tribe_display else archetype.title()
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


# Canonical WUBRG color order for normalization
_COLOR_ORDER = "WUBRG"
_COLOR_NAMES = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}


def _normalize_colors(raw: str) -> str:
    """Uppercase, deduplicate, and sort into WUBRG canonical order."""
    seen = dict.fromkeys(c for c in raw.upper() if c in _COLOR_ORDER)
    return "".join(c for c in _COLOR_ORDER if c in seen)


def _valid_colors(raw: str) -> bool:
    """Return True if raw contains only valid color letters and at least one."""
    upper = raw.upper()
    return bool(upper) and all(c in _COLOR_ORDER for c in upper)


def run_interactive_wizard() -> argparse.Namespace:
    """Prompt the user for deck parameters interactively."""
    try:
        return _wizard_prompts()
    except KeyboardInterrupt:
        print("\n  Aborted.")
        raise SystemExit(0)


def _wizard_prompts() -> argparse.Namespace:
    print("=" * 60)
    print("  DECK SCAFFOLD GENERATOR — Interactive Wizard")
    print("=" * 60)
    print()

    # ── Step 1: Deck name ─────────────────────────────────────
    print("  Step 1 — Deck Name")
    name = input("  Name: ").strip()
    while not name:
        print("  (name is required)")
        name = input("  Name: ").strip()
    print()

    # ── Step 2: Colors ────────────────────────────────────────
    print("  Step 2 — Color Identity")
    print("  " + "  ".join(f"{k} {v}" for k, v in _COLOR_NAMES.items()))
    print("  Combine freely: W, WB, GU, WUR, WUBRG, etc.")
    print("  Colorless decks: enter C")
    raw_colors = input("  Colors: ").strip()
    while not raw_colors or (raw_colors.upper() != "C" and not _valid_colors(raw_colors)):
        print("  Invalid — use letters W U B R G only (e.g. WB, GU, WUBRG)")
        raw_colors = input("  Colors: ").strip()
    colors = "C" if raw_colors.upper() == "C" else _normalize_colors(raw_colors)
    print()

    # ── Step 3: Archetype ─────────────────────────────────────
    valid_archetypes = sorted(ARCHETYPE_QUERIES.keys())
    print("  Step 3 — Archetype")
    # Print in 2-column rows
    for i, a in enumerate(valid_archetypes, 1):
        end = "\n" if i % 4 == 0 or i == len(valid_archetypes) else ""
        print(f"  {i:2}. {a:<12}", end=end)
    if len(valid_archetypes) % 4 != 0:
        print()
    print()
    print("  Pick one or more (comma-separated numbers or names, e.g. 5,7 or lifegain,mill)")

    def _parse_archetype_input(raw: str) -> Optional[List[str]]:
        """Parse a multi-archetype input string. Returns list or None if invalid."""
        parts = [p.strip().lower() for p in raw.replace(" ", ",").split(",") if p.strip()]
        if not parts:
            return None
        resolved = []
        for p in parts:
            if p in valid_archetypes:
                resolved.append(p)
            elif p.isdigit() and 1 <= int(p) <= len(valid_archetypes):
                resolved.append(valid_archetypes[int(p) - 1])
            else:
                return None  # invalid token
        return list(dict.fromkeys(resolved))  # deduplicate, preserve order

    archetype_raw = input("  Choice(s): ").strip()
    archetypes: List[str] = []
    while True:
        result = _parse_archetype_input(archetype_raw)
        if result:
            archetypes = result
            break
        print(f"  Invalid — use numbers 1-{len(valid_archetypes)} or archetype names, comma-separated")
        archetype_raw = input("  Choice(s): ").strip()

    # For backwards compat, single archetype stored as string too
    archetype = ",".join(archetypes)
    print()

    # ── Step 4: Tribe (only if tribal) ───────────────────────
    tribes: List[str] = []
    if "tribal" in archetypes:
        print("  Step 4 — Creature Subtypes (Tribal selected)")
        print(f"  {len(ALL_CREATURE_TYPES)} types available. You may add multiple (e.g. Angel + Warrior).")
        print()

        def _pick_one_tribe() -> Optional[str]:
            while True:
                raw = input("  Search subtype: ").strip()
                if not raw:
                    return None
                exact = _CREATURE_TYPES_LOWER.get(raw.lower())
                if exact:
                    return exact
                matches = [t for t in ALL_CREATURE_TYPES if raw.lower() in t.lower()]
                if not matches:
                    print(f"  No types match '{raw}'. Try again (or Enter to stop adding).")
                elif len(matches) == 1:
                    return matches[0]
                elif len(matches) <= 10:
                    print(f"  Matches: {', '.join(matches)}")
                    print("  Type the full name to confirm, or refine your search.")
                else:
                    print(f"  {len(matches)} matches — too many to list. Refine your search.")

        while True:
            picked = _pick_one_tribe()
            if picked is None:
                if not tribes:
                    print("  (at least one subtype is required for tribal)")
                    continue
                break
            if picked in tribes:
                print(f"  '{picked}' already added.")
            else:
                tribes.append(picked)
                print(f"  Added: {picked}  |  Selected so far: {', '.join(tribes)}")
            more = input("  Add another subtype? [y/N]: ").strip().lower()
            if more not in ("y", "yes"):
                break
        print()

    tribe = tribes if tribes else None  # keep as list or None

    # ── Step 5: Extra tags (optional) ────────────────────────
    print("  Step 5 — Extra Search Tags (optional)")
    print("  Available tags: lifegain, removal, draw, counter, ramp, haste,")
    print("                  flying, trample, mill, wipe, pump, bounce, etb,")
    print("                  tutor, flash, tribal, protection, deathtouch")
    extra_tags = input("  Tags (comma-separated, or Enter to skip): ").strip() or None
    print()

    # ── Step 6: Run queries? ──────────────────────────────────
    print("  Step 6 — Run Queries Now?")
    print("  Queries search your local card pool and embed results in the scaffold.")
    run_q = input("  Run queries? [Y/n]: ").strip().lower()
    skip_queries = run_q in ("n", "no")
    print()

    # ── Step 7: Confirmation ──────────────────────────────────
    from datetime import date as _date
    preview_date = _date.today().isoformat()
    print("=" * 60)
    print("  SUMMARY")
    print(f"  Name:       {name}")
    print(f"  Colors:     {colors}")
    archetype_label = ", ".join(archetypes) if len(archetypes) > 1 else archetype
    tribe_label = " / ".join(tribes) + " Tribal" if tribes else ""
    print(f"  Archetype:  {archetype_label}" + (f" ({tribe_label})" if tribe_label else ""))
    print(f"  Extra tags: {extra_tags or 'none'}")
    print(f"  Run queries: {'no (offline template)' if skip_queries else 'yes'}")
    print(f"  Output:     Decks/{preview_date}_{sanitize_folder_name(name)}/")
    print("=" * 60)
    confirm = input("  Confirm? [Y/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("  Aborted.")
        raise SystemExit(0)
    print()

    return argparse.Namespace(
        name=name,
        colors=colors,
        archetype=archetypes,
        tribe=tribe,
        date=None,
        output_dir=None,
        extra_tags=extra_tags,
        skip_queries=skip_queries,
        interactive=True,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate a deck-building session scaffold with embedded query results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--name", default=None, help="Deck name (e.g. 'Orzhov Lifegain')")
    p.add_argument("--colors", default=None, help="Color identity (e.g. WB, GU, WUR)")
    p.add_argument(
        "--archetype", default=None,
        nargs="+",
        choices=sorted(ARCHETYPE_QUERIES.keys()),
        metavar="ARCHETYPE",
        help=f"Deck archetype(s), one or more of: {', '.join(sorted(ARCHETYPE_QUERIES.keys()))}",
    )
    p.add_argument("--interactive", "-i", action="store_true", help="Launch interactive wizard mode")
    p.add_argument(
        "--tribe",
        nargs="+",
        metavar="SUBTYPE",
        help=f"Creature subtype(s) for tribal — one or more of the {len(ALL_CREATURE_TYPES)} official MTG types (e.g. --tribe Angel Warrior)",
    )
    p.add_argument("--date", help="Date override (YYYY-MM-DD, default: today)")
    p.add_argument("--output-dir", help="Output directory (default: Decks/)")
    p.add_argument("--extra-tags", help="Additional search tags, comma-separated")
    p.add_argument(
        "--skip-queries", action="store_true",
        help="Generate scaffold without running queries (offline template)",
    )
    p.add_argument(
        "--focus-cards", nargs="+", metavar="CARD",
        help="Specific card names to guarantee in the candidate pool (one per arg or comma-separated)",
    )
    return p


def main() -> None:
    from mtg_utils import RepoPaths

    args = build_parser().parse_args()

    # Launch interactive wizard if no core args provided, or if --interactive flag set
    if args.interactive or not any([args.name, args.colors, args.archetype]):
        args = run_interactive_wizard()
    else:
        # Validate required args for non-interactive mode
        missing = [f"--{f}" for f, v in [("name", args.name), ("colors", args.colors), ("archetype", args.archetype)] if not v]
        if missing:
            build_parser().error(f"the following arguments are required: {', '.join(missing)}")
        # Normalize: always store archetype as a list internally
        if isinstance(args.archetype, str):
            args.archetype = [args.archetype]

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
    archetype_list = args.archetype if isinstance(args.archetype, list) else [args.archetype]
    print(f"  Archetype: {', '.join(archetype_list)}")
    if args.tribe:
        tribe_str = " / ".join(args.tribe) if isinstance(args.tribe, list) else args.tribe
        print(f"  Tribe:     {tribe_str}")
    print(f"  Output:    {deck_dir}/")
    print(f"{'='*70}\n")

    # Build merged query plan from all chosen archetypes (deduplicate by label)
    archetype_list = args.archetype if isinstance(args.archetype, list) else [args.archetype]
    seen_labels: dict = {}
    for arch in archetype_list:
        for q in ARCHETYPE_QUERIES.get(arch, []):
            if q["label"] not in seen_labels:
                seen_labels[q["label"]] = q
    # Always put Lands last
    lands = seen_labels.pop("Lands", None)
    query_plan = list(seen_labels.values())

    # For tribal with multiple tribes, expand the generic creature query into
    # one per tribe (avoids the broken | OR syntax)
    tribe_arg = getattr(args, "tribe", None)
    if tribe_arg:
        tribe_list = tribe_arg if isinstance(tribe_arg, list) else [tribe_arg]
        if len(tribe_list) > 1:
            # Remove the generic tribal creature query; replace with per-tribe queries
            query_plan = [q for q in query_plan if q["label"] != "Tribal creatures (by subtype)"]
            for t in tribe_list:
                query_plan.insert(0, {
                    "label": f"{t} creatures",
                    "args": f"--type creature --name \"{t}\"",
                })

    if lands:
        query_plan.append(lands)
    query_results: List[Dict] = []

    # Inject focus-card queries (guarantee specific cards appear in pool)
    focus_cards = getattr(args, "focus_cards", None)
    if focus_cards:
        # Flatten any comma-separated values passed as single args
        flat: List[str] = []
        for item in focus_cards:
            flat.extend(c.strip() for c in item.split(",") if c.strip())
        for card_name in flat:
            query_plan.append({
                "label": f"Focus card: {card_name}",
                "args": f"--name \"{card_name}\"",
            })

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
            print(f"         -> {count} candidates")

        print(f"\n  Total candidates across all queries: {total_candidates}")

    # Generate session file
    session_content = generate_session_file(
        deck_date=deck_date,
        deck_name=args.name,
        colors=args.colors.upper(),
        archetype=", ".join(archetype_list),
        query_results=query_results,
        tribe=args.tribe,
    )

    # Write files
    session_path = deck_dir / "session.md"
    session_path.write_text(session_content, encoding="utf-8")
    print(f"\n  [OK] session.md written ({len(session_content):,} bytes)")

    decklist_path = deck_dir / "decklist.txt"
    if not decklist_path.exists():
        decklist_path.write_text(generate_decklist_template(), encoding="utf-8")
        print(f"  [OK] decklist.txt template created")

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
        print(f"  [OK] analysis.md template created")

    sb_template = paths.templates / "sideboard_guide.md"
    sb_path = deck_dir / "sideboard_guide.md"
    if not sb_path.exists():
        if sb_template.exists():
            sb_path.write_text(
                sb_template.read_text(encoding="utf-8"), encoding="utf-8"
            )
        else:
            sb_path.write_text("# Sideboard Guide\n\n(fill in after completing Gate 5)\n", encoding="utf-8")
        print(f"  [OK] sideboard_guide.md template created")

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
