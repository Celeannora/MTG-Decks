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
    "opp_mill": [
        # Spells/effects that mill the opponent
        ["--oracle", "opponent mills", "--format", "csv", "--limit", "9999"],
        ["--oracle", "target player mills", "--format", "csv", "--limit", "9999"],
        ["--oracle", "each opponent mills", "--format", "csv", "--limit", "9999"],
        ["--oracle", "mills that many", "--format", "csv", "--limit", "9999"],
        ["--tags", "mill", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "self_mill": [
        # Spells/effects that self-mill (fill your own graveyard)
        ["--oracle", "put the top", "--oracle", "into your graveyard", "--format", "csv", "--limit", "9999"],
        ["--oracle", "mill yourself", "--format", "csv", "--limit", "9999"],
        ["--oracle", "discard", "--tags", "self_mill", "--format", "csv", "--limit", "9999"],
        ["--oracle", "put.*cards.*graveyard", "--format", "csv", "--limit", "9999"],
        ["--tags", "self_mill", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "reanimation": [
        # Return creatures from graveyard to play
        ["--oracle", "return target creature card from your graveyard", "--format", "csv", "--limit", "9999"],
        ["--oracle", "return.*from.*graveyard.*battlefield", "--format", "csv", "--limit", "9999"],
        ["--oracle", "return.*graveyard.*to.*play", "--format", "csv", "--limit", "9999"],
        ["--tags", "reanimation", "--format", "csv", "--limit", "9999"],  # color-agnostic
        # Sac outlets + discard-as-cost enablers
        ["--oracle", "sacrifice a creature", "--format", "csv", "--limit", "9999"],  # color-agnostic
        ["--oracle", "discard a card", "--tags", "reanimation", "--format", "csv", "--limit", "9999"],
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
    "aristocrats": [
        ["--oracle", "when a creature you control dies", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever you sacrifice a creature", "--format", "csv", "--limit", "9999"],
        ["--oracle", "sacrifice a creature:", "--format", "csv", "--limit", "9999"],
        ["--oracle", "each creature that dies", "--format", "csv", "--limit", "9999"],
        ["--tags", "aristocrats", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "tokens": [
        ["--oracle", "create.*token", "--format", "csv", "--limit", "9999"],
        ["--oracle", "creatures you control get", "--format", "csv", "--limit", "9999"],
        ["--oracle", "for each token you control", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Convoke", "--format", "csv", "--limit", "9999"],
        ["--tags", "token", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "blink": [
        ["--oracle", "exile.*return.*to.*battlefield", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever.*enters the battlefield", "--format", "csv", "--limit", "9999"],
        ["--oracle", "flicker", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Blitz", "--format", "csv", "--limit", "9999"],
        ["--tags", "blink", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "stax": [
        ["--oracle", "players can't", "--format", "csv", "--limit", "9999"],
        ["--oracle", "costs.*more to cast", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever a player casts a spell", "--format", "csv", "--limit", "9999"],
        ["--oracle", "don't untap", "--format", "csv", "--limit", "9999"],
        ["--tags", "stax", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "storm": [
        ["--keywords", "Storm", "--format", "csv", "--limit", "9999"],
        ["--oracle", "for each spell cast this turn", "--format", "csv", "--limit", "9999"],
        ["--oracle", "add.*to your mana pool", "--oracle", "this turn", "--format", "csv", "--limit", "9999"],
        ["--oracle", "copy.*for each other spell", "--format", "csv", "--limit", "9999"],
        ["--tags", "storm", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "prowess": [
        ["--keywords", "Prowess", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever you cast a noncreature spell", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever you cast an instant or sorcery", "--format", "csv", "--limit", "9999"],
        ["--oracle", "magecraft", "--format", "csv", "--limit", "9999"],
        ["--tags", "prowess", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "enchantress": [
        ["--oracle", "whenever you cast an enchantment", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever an enchantment enters the battlefield", "--format", "csv", "--limit", "9999"],
        ["--oracle", "constellation", "--format", "csv", "--limit", "9999"],
        ["--oracle", "enchant creature", "--oracle", "draw a card", "--format", "csv", "--limit", "9999"],
        ["--tags", "enchantress", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "artifacts": [
        ["--oracle", "whenever an artifact enters the battlefield", "--format", "csv", "--limit", "9999"],
        ["--oracle", "metalcraft", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Affinity", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Improvise", "--format", "csv", "--limit", "9999"],
        ["--tags", "artifacts", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "equipment": [
        ["--type", "equipment", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever equipped creature", "--format", "csv", "--limit", "9999"],
        ["--oracle", "attach.*to.*creature you control", "--format", "csv", "--limit", "9999"],
        ["--oracle", "living weapon", "--format", "csv", "--limit", "9999"],
        ["--tags", "equipment", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "voltron": [
        ["--oracle", "put.*aura.*onto the battlefield attached", "--format", "csv", "--limit", "9999"],
        ["--oracle", "double strike", "--oracle", "trample", "--format", "csv", "--limit", "9999"],
        ["--oracle", "hexproof", "--oracle", "indestructible", "--format", "csv", "--limit", "9999"],
        ["--oracle", "21 or more combat damage to a player", "--format", "csv", "--limit", "9999"],
        ["--tags", "voltron", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "landfall": [
        ["--oracle", "landfall", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever a land enters the battlefield under your control", "--format", "csv", "--limit", "9999"],
        ["--oracle", "you may play an additional land", "--format", "csv", "--limit", "9999"],
        ["--oracle", "search your library for.*land", "--format", "csv", "--limit", "9999"],
        ["--tags", "landfall", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "lands": [
        ["--oracle", "return.*land.*from your graveyard", "--format", "csv", "--limit", "9999"],
        ["--oracle", "you may play lands from your graveyard", "--format", "csv", "--limit", "9999"],
        ["--oracle", "dredge", "--format", "csv", "--limit", "9999"],
        ["--oracle", "sacrifice.*land", "--format", "csv", "--limit", "9999"],
        ["--tags", "lands", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "infect": [
        ["--keywords", "Infect", "--format", "csv", "--limit", "9999"],
        ["--oracle", "poison counter", "--format", "csv", "--limit", "9999"],
        ["--oracle", "wither", "--format", "csv", "--limit", "9999"],
        ["--oracle", "gets.*until end of turn", "--format", "csv", "--limit", "9999"],  # color-agnostic
        ["--tags", "infect", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "proliferate": [
        ["--keywords", "Proliferate", "--format", "csv", "--limit", "9999"],
        ["--oracle", "proliferate", "--format", "csv", "--limit", "9999"],
        ["--oracle", "double the number of.*counters", "--format", "csv", "--limit", "9999"],
        ["--oracle", "put.*counter.*on each", "--format", "csv", "--limit", "9999"],
        ["--tags", "proliferate", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "energy": [
        ["--oracle", "energy counter", "--format", "csv", "--limit", "9999"],
        ["--oracle", "you get", "--oracle", "energy", "--format", "csv", "--limit", "9999"],
        ["--oracle", "pay.*energy", "--format", "csv", "--limit", "9999"],
        ["--tags", "energy", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "graveyard": [
        ["--oracle", "cards in your graveyard", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Delve", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Threshold", "--format", "csv", "--limit", "9999"],
        ["--oracle", "if seven or more cards are in your graveyard", "--format", "csv", "--limit", "9999"],
        ["--tags", "graveyard", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "flashback": [
        ["--keywords", "Flashback", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Jump-start", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Aftermath", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Escape", "--format", "csv", "--limit", "9999"],
        ["--oracle", "cast.*from your graveyard", "--format", "csv", "--limit", "9999"],
    ],
    "madness": [
        ["--keywords", "Madness", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever you discard a card", "--format", "csv", "--limit", "9999"],
        ["--oracle", "discard.*card.*draw", "--format", "csv", "--limit", "9999"],
        ["--oracle", "you may cast.*from your hand.*exile it", "--format", "csv", "--limit", "9999"],
        ["--tags", "madness", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "superfriends": [
        ["--type", "planeswalker", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever a planeswalker you control", "--format", "csv", "--limit", "9999"],
        ["--oracle", "loyalty counter", "--format", "csv", "--limit", "9999"],
        ["--oracle", "you control a planeswalker", "--format", "csv", "--limit", "9999"],
        ["--tags", "superfriends", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "extra_turns": [
        ["--oracle", "take an extra turn after this one", "--format", "csv", "--limit", "9999"],
        ["--oracle", "takes an additional turn", "--format", "csv", "--limit", "9999"],
        ["--oracle", "extra turn", "--format", "csv", "--limit", "9999"],
        ["--oracle", "untap all", "--format", "csv", "--limit", "9999"],
        ["--tags", "extra_turns", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "eldrazi": [
        ["--type", "eldrazi", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Annihilator", "--format", "csv", "--limit", "9999"],
        ["--oracle", "colorless mana", "--format", "csv", "--limit", "9999"],
        ["--oracle", "waste", "--type", "land", "--format", "csv", "--limit", "9999"],
        ["--tags", "eldrazi", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "vehicles": [
        ["--type", "vehicle", "--format", "csv", "--limit", "9999"],
        ["--keywords", "Crew", "--format", "csv", "--limit", "9999"],
        ["--oracle", "crew", "--oracle", "becomes an artifact creature", "--format", "csv", "--limit", "9999"],
        ["--oracle", "whenever you crew", "--format", "csv", "--limit", "9999"],
        ["--tags", "vehicles", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
    "domain": [
        ["--oracle", "domain", "--format", "csv", "--limit", "9999"],
        ["--oracle", "for each basic land type among lands you control", "--format", "csv", "--limit", "9999"],
        ["--oracle", "number of basic land types", "--format", "csv", "--limit", "9999"],
        ["--oracle", "search your library for a basic land", "--format", "csv", "--limit", "9999"],
        ["--tags", "domain", "--format", "csv", "--limit", "9999"],  # color-agnostic
    ],
}


def run_query(
    repo_root: Path,
    base_args: str,
    colors: str,
    tribe: Optional[str] = None,
    extra_tags: Optional[str] = None,
    suppress_tribe: bool = False,
) -> Tuple[str, str, int]:
    """
    Run a search_cards.py query. Returns (command_string, output, result_count).
    color-agnostic: does NOT inject --colors — archetype queries search all colors.
    Adds --show-tags automatically.
    """
    from mtg_utils import RepoPaths
    paths = RepoPaths(root=repo_root)
    script = paths.scripts_dir / "search_cards.py"
    import shlex
    cmd_parts = [sys.executable, str(script)]
    cmd_parts += shlex.split(base_args)

    # color-agnostic: no --colors injection; archetypes search across all colors

    # Tribe is NOT used as a filter on existing queries — it only adds
    # supplemental per-tribe creature queries to the query plan (see main()).
    # Filtering here would exclude non-tribal cards (Changelings, support spells)
    # from the candidate pool, which breaks non-creature archetypes.

    cmd_parts += ["--show-tags", "--format", "csv", "--limit", "9999"]

    # Add extra tags if provided
    if extra_tags:
        if "--tags" in base_args:
            # Merge extra_tags into the existing --tags value
            def _merge_tags(m):
                existing = m.group(1).rstrip(",")
                return f"--tags {existing},{extra_tags}"
            base_args = re.sub(r"--tags\s+(\S+)", _merge_tags, base_args, count=1)
            # Rebuild cmd_parts from updated base_args
            cmd_parts = [sys.executable, str(script)]
            cmd_parts += shlex.split(base_args)
            cmd_parts += ["--show-tags", "--format", "csv", "--limit", "9999"]
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
        "## Candidate Pool Index",
        "",
        "> Pool data is in separate CSV files under `pools/`. Read the relevant pool",
        "> file(s) when selecting cards at each gate. Load only the file(s) for the",
        "> card type you are currently selecting — not all pools at once.",
        "> DO NOT add any card that does not appear in a pool file.",
        "",
        "| # | Role | Pool File | Cards |",
        "|---|------|-----------|-------|",
    ]

    for i, qr in enumerate(query_results, 1):
        pool_file = qr.get("pool_file", f"pools/pool_{i:02d}_unknown.csv")
        count = qr["count"] if isinstance(qr.get("count"), int) and qr["count"] > 0 else (qr.get("count") or "—")
        lines.append(f"| {i} | {qr['label']} | [`{pool_file}`]({pool_file}) | {count} |")

    lines += [
        "",
        "### Query Commands (for reference / re-running)",
        "",
        "| # | Label | Command |",
        "|---|-------|---------|",
    ]

    for i, qr in enumerate(query_results, 1):
        cmd_short = qr["command"].replace("python ", "").strip()
        lines.append(f"| {i} | {qr['label']} | `{cmd_short}` |")

    lines += [""]

    lines += [
        "## Additional Queries",
        "",
        "> If the pools above are insufficient, run additional queries:",
        "> ```bash",
        f"> python {RepoPaths.SCRIPTS_DIR_NAME}/search_cards.py --type <type> --colors <colors> [flags...]",
        "> ```",
        "> Write output to a new file in `pools/` (e.g. `pools/pool_07_extra.csv`)",
        "> and add a row to the Candidate Pool Index table above.",
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

    print("  Step 6b — Wildcard Mode  (optional)")
    if tribes:
        print("  Skip tribal --name filters so all archetype creatures appear in the pool.")
        print("  The tribe(s) will be noted in the session as an AI hint only.")
        wc = input("  Wildcard? [y/N]: ").strip().lower()
        wildcard = wc in ("y", "yes")
    else:
        wildcard = False
    print()
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
    p.add_argument(
        "--wildcard", action="store_true",
        help="Suppress tribal --name creature queries — tribe becomes an AI hint at Gate 3 only, not a pool filter. Use when you want the full archetype pool with tribal preference, not tribal-only creatures.",
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
    wildcard_active = getattr(args, "wildcard", False)
    print(f"  Archetype: {', '.join(archetype_list)}")
    if args.tribe:
        tribe_str = " / ".join(args.tribe) if isinstance(args.tribe, list) else args.tribe
        if wildcard_active:
            print(f"  Tribe:     {tribe_str}  [WILDCARD — hint only, --name filter suppressed]")
        else:
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

    # For tribal builds, add one supplemental creature query per tribe by name.
    # These are ADDITIVE — they run alongside the archetype's existing creature
    # queries so non-tribal creatures (Changelings, support creatures) still
    # appear in the pool. The generic "Tribal creatures (by subtype)" placeholder
    # query is removed since per-tribe queries cover it more precisely.
    tribe_arg = getattr(args, "tribe", None)
    if tribe_arg:
        tribe_list = tribe_arg if isinstance(tribe_arg, list) else [tribe_arg]
        # Remove the generic placeholder (if present) — replaced by per-tribe below
        query_plan = [q for q in query_plan if q["label"] != "Tribal creatures (by subtype)"]
        # Insert per-tribe name queries at the front, one per tribe.
        # Marked with is_tribe_query so --wildcard can suppress them.
        for t in reversed(tribe_list):
            query_plan.insert(0, {
                "label": f"{t} creatures",
                "args": f"--type creature --name \"{t}\"",
                "is_tribe_query": True,
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
                "command": f"python {RepoPaths.SCRIPTS_DIR_NAME}/search_cards.py {q['args']} --show-tags",
                "output": "(run this query and paste results here)",
                "count": "?",
            })
    else:
        total_candidates = 0
        for i, q in enumerate(query_plan, 1):
            label = q["label"]
            print(f"  [{i}/{len(query_plan)}] {label}...")

            wildcard_active = getattr(args, "wildcard", False)
            if wildcard_active and q.get("is_tribe_query", False):
                print(f"         -> skipped (wildcard mode)")
                query_results.append({
                    "label": q["label"],
                    "command": f"# skipped — wildcard mode active",
                    "output": "(skipped — wildcard mode: tribe label used as AI hint only, not as a pool filter)",
                    "count": 0,
                })
                continue
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
    # Write each query's output to a separate pool CSV file
    import re as _re
    pools_dir = deck_dir / "pools"
    pools_dir.mkdir(exist_ok=True)
    for i, qr in enumerate(query_results, 1):
        safe_label = _re.sub(r"[^a-z0-9]+", "_", qr["label"].lower()).strip("_")
        pool_filename = f"pool_{i:02d}_{safe_label}.csv"
        pool_path = pools_dir / pool_filename
        qr["pool_file"] = f"pools/{pool_filename}"
        output = qr.get("output", "")
        if output and not output.startswith("("):
            pool_path.write_text(output, encoding="utf-8")
        else:
            pool_path.write_text(f"# No results for: {qr['label']}\n# Command: {qr['command']}\n", encoding="utf-8")

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
