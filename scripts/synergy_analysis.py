#!/usr/bin/env python3
"""
Synergy Analysis — Gate 2.5 Automation

Reads a card list (from a session.md candidate pool, a decklist.txt, a pool
CSV file, or a plain text file) and produces a Gate 2.5 synergy report:

  - Builds a directional synergy profile for every card (source vs. payoff tags,
    creature subtypes, keywords, CMC, oracle text)
  - Scores pairwise interactions in five passes:
      Pass 1 — Rule-based tag matching (source_tags → payoff_tags)
      Pass 2 — Oracle text cross-reference (subtype + keyword verification)
      Pass 2b — Oracle payoff bridges (life-gain drain, food, tribe triggers)
      Pass 3 — CMC-bracket-aware REDUNDANT detection (narrow roles only)
      Pass 4 — Oracle-text dependency scoring (Auras, Equipment, conditionals)
  - Role-aware scoring: engine / enabler / payoff / support / interaction
  - Checks all Gate 2.5 thresholds with pool-vs-deck calibration
  - Writes a pre-populated Gate 2.5 markdown block you can paste into session.md

Usage:
    # Analyze candidate pool extracted from a session.md
    python scripts/synergy_analysis.py Decks/2026-04-03_My_Deck/session.md

    # Analyze a finished decklist.txt (mainboard only by default)
    python scripts/synergy_analysis.py Decks/2026-04-03_My_Deck/decklist.txt

    # Include sideboard in scoring
    python scripts/synergy_analysis.py decklist.txt --include-sideboard

    # Analyze pool CSV files in a pools/ directory
    python scripts/synergy_analysis.py Decks/2026-04-03_My_Deck/ --format pools

    # Analyze a plain card-name list (one name per line)
    python scripts/synergy_analysis.py my_candidates.txt --format names

    # Write report to a file instead of stdout
    python scripts/synergy_analysis.py session.md --output report.md

    # Force pool or deck threshold calibration
    python scripts/synergy_analysis.py decklist.txt --mode deck

    # Override primary axis detection
    python scripts/synergy_analysis.py decklist.txt --primary-axis lifegain,token

Flags:
    --format            Input format: auto (default), session, decklist, names, pools
    --output            Write markdown report to this file (default: stdout)
    --mode              Threshold calibration: pool, deck, or auto (default)
    --include-sideboard Include sideboard in scoring (default: mainboard only)
    --allow-missing     Skip inconclusive guard when maindeck cards are missing from DB
    --score-mode        legacy or role-aware (default: role-aware)
    --primary-axis      Comma-separated mechanic override, e.g. lifegain,token

Exit codes:
    0  All Gate 2.5 thresholds passed
    1  One or more thresholds failed (or inconclusive)
    2  Input file not found or no cards extracted
"""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mtg_utils import RepoPaths, parse_decklist
from search_cards import TAG_RULES, KEYWORD_TAG_MAP, compute_tags, compute_synergy_profile, CARD_TYPES

# ─── Directional interaction rules ──────────────────────────────────────────
INTERACTION_RULES: List[Tuple[str, str, str, str, str, str]] = [
    # ── FEEDS ────────────────────────────────────────────────────────────────
    ("source_tags", "lifegain",    "payoff_tags", "lifegain",    "FEEDS",    "{a} produces life gain → {b} has a life-gain trigger"),
    ("source_tags", "token",       "payoff_tags", "token",       "FEEDS",    "{a} creates tokens → {b} benefits from token creation"),
    ("source_tags", "draw",        "payoff_tags", "draw",        "FEEDS",    "{a} draws cards → {b} rewards card draw"),
    ("source_tags", "etb",         "payoff_tags", "etb",         "FEEDS",    "{a} has ETB → {b} reacts to creatures entering"),
    ("source_tags", "pump",        "payoff_tags", "pump",        "FEEDS",    "{a} places counters → {b} scales with counters"),
    ("source_tags", "discard",     "payoff_tags", "discard",     "FEEDS",    "{a} forces discard → {b} benefits from discard"),
    ("source_tags", "mill",        "payoff_tags", "mill",        "FEEDS",    "{a} mills cards → {b} benefits from graveyard"),
    ("source_tags", "token",       "broad_tags",  "pump",        "FEEDS",    "{a} creates tokens → {b} pumps the team"),
    ("source_tags", "lifegain",    "broad_tags",  "draw",        "FEEDS",    "{a} gains life → {b} draws on life gain"),
    ("broad_tags",  "discard",     "broad_tags",  "reanimation", "FEEDS",    "{a} fills graveyard → {b} reanimates from it"),
    ("source_tags", "etb",         "broad_tags",  "bounce",      "FEEDS",    "{a} has ETB value → {b} bounces to replay ETB"),
    # ── TRIGGERS ─────────────────────────────────────────────────────────────
    ("source_tags", "token",       "payoff_tags", "token",       "TRIGGERS", "{a} creates tokens → {b}'s token-creation trigger fires"),
    # ── ENABLES ──────────────────────────────────────────────────────────────
    ("broad_tags",  "ramp",        "broad_tags",  "wipe",        "ENABLES",  "{a} ramps mana → {b} expensive wipe becomes castable"),
    ("broad_tags",  "ramp",        "broad_tags",  "reanimation", "ENABLES",  "{a} ramps mana → {b} reanimation spell becomes castable"),
    ("broad_tags",  "ramp",        "broad_tags",  "pump",        "ENABLES",  "{a} produces mana → {b} activated pump ability"),
    ("broad_tags",  "protection",  "broad_tags",  "tribal",      "ENABLES",  "{a} protects key piece → {b} tribal engine survives"),
    ("broad_tags",  "tutor",       "broad_tags",  "draw",        "ENABLES",  "{a} tutors → {b} draw engine found reliably"),
    ("broad_tags",  "protection",  "source_tags", "lifegain",    "ENABLES",  "{a} protects → {b} lifegain engine survives removal"),
    # ── AMPLIFIES ────────────────────────────────────────────────────────────
    ("source_tags", "token",       "broad_tags",  "wipe",        "AMPLIFIES","Tokens → sacrifice synergy: {a} creates fodder for {b}"),
    ("broad_tags",  "pump",        "broad_tags",  "tribal",      "AMPLIFIES","Tribal anthem: {a} pump stacks with {b} tribal bonus"),
    ("source_tags", "pump",        "source_tags", "pump",        "AMPLIFIES","{a} + {b} both add counters — outputs stack"),
    # ── PROTECTS ─────────────────────────────────────────────────────────────
    ("broad_tags",  "protection",  "broad_tags",  "removal",     "PROTECTS", "{a} protects key creatures → {b} removal suite operates safely"),
    ("broad_tags",  "counter",     "broad_tags",  "protection",  "PROTECTS", "{a} counters removal → {b} protected threat survives"),
    ("broad_tags",  "bounce",      "broad_tags",  "counter",     "PROTECTS", "{a} bounces threats → {b} backup counter coverage"),
    # ── SACRIFICE / ARISTOCRATS ──────────────────────────────────────────────
    ("source_tags", "sacrifice",   "payoff_tags",  "sacrifice",   "FEEDS",    "{a} provides sac outlet → {b} fires death trigger"),
    ("source_tags", "token",       "payoff_tags",  "sacrifice",   "FEEDS",    "{a} makes tokens → {b} sacrifice outlet has fuel"),
    ("broad_tags",  "sacrifice",   "broad_tags",   "lifegain",    "TRIGGERS", "{a} death triggers → {b} life gain on creature death"),
    ("broad_tags",  "sacrifice",   "broad_tags",   "draw",        "TRIGGERS", "{a} sacrifice or death → {b} card draw on death"),
    # ── ENERGY ───────────────────────────────────────────────────────────────
    ("source_tags", "energy",      "payoff_tags",  "energy",      "FEEDS",    "{a} produces energy → {b} spends energy counters"),
    ("source_tags", "energy",      "broad_tags",   "pump",        "FEEDS",    "{a} produces energy → {b} activated pump uses energy"),
    # ── STORM / SPELL COUNT ──────────────────────────────────────────────────
    ("source_tags", "storm_count", "payoff_tags",  "storm_count", "AMPLIFIES","{a} generates/extends spell chain → {b} scales with spell count"),
    ("broad_tags",  "ramp",        "source_tags",  "storm_count", "ENABLES",  "{a} ritual/ramp → {b} storm chain becomes viable"),
    # ── ENCHANTRESS ──────────────────────────────────────────────────────────
    ("source_tags", "enchantress", "payoff_tags",  "enchantress", "TRIGGERS", "{a} is an enchantment → {b} enchantment-cast draw trigger fires"),
    ("broad_tags",  "tutor",       "source_tags",  "enchantress", "ENABLES",  "{a} tutors enchantments → {b} enchantress engine found reliably"),
    # ── BLINK / ETB ABUSE ────────────────────────────────────────────────────
    ("source_tags", "blink",       "payoff_tags",  "etb",         "AMPLIFIES","{a} blinks → {b} ETB fires again on re-entry"),
    ("source_tags", "blink",       "broad_tags",   "etb",         "AMPLIFIES","{a} blinks → {b} ETB fires repeatedly"),
    ("broad_tags",  "bounce",      "payoff_tags",  "etb",         "FEEDS",    "{a} bounces → {b} ETB replays on recast"),
]

ROLE_TAGS = {"wipe", "counter", "tutor", "reanimation", "removal", "draw", "bounce"}

_ORACLE_KEYWORDS = {
    "flying", "lifelink", "deathtouch", "first strike", "double strike",
    "vigilance", "trample", "haste", "menace", "reach", "indestructible",
}

_DEP_PATTERNS: List[Tuple[str, int, str]] = [
    (r"\benchant\b",                                           1, "Aura — needs enchantment target"),
    (r"\bequip\b",                                             1, "Equipment — needs a creature to equip"),
    (r"\bfortify\b",                                           1, "Fortification — needs a land"),
    (r"sacrifice another",                                     1, "Needs another permanent to sacrifice"),
    (r"sacrifice a (creature|permanent)",                      1, "Needs a creature to sacrifice"),
    (r"tap another .{0,20}you control",                       1, "Needs another tapped permanent"),
    (r"if you control (a|an)\b",                              1, "Conditional on board presence"),
    (r"if you have \d+ or more life",                         1, "Conditional on life total"),
    (r"(target|another) creature you control",                 1, "Needs a creature target you control"),
    (r"whenever .{0,30} you control .{0,30}(attacks|blocks)", 1, "Needs attacking/blocking creatures"),
    (r"activated ability of .{0,30} you control",             1, "Needs specific activated ability"),
    (r"for each other .{0,20}you control",                    1, "Scales with other permanents"),
]

# ─── Role classification constants ──────────────────────────────────────────
INTERACTION_TAGS: Set[str] = {"removal", "counter", "wipe", "bounce", "protection"}
SUPPORT_TAGS: Set[str]     = {"draw", "scry", "ramp", "tutor", "loot"}
CORE_ENGINE_TAGS: Set[str] = {
    "lifegain", "token", "sacrifice", "etb", "mill", "discard",
    "energy", "enchantress", "pump", "drain",
}

# Oracle payoff bridge patterns: (regex, mechanic_axis, label)
_PAYOFF_BRIDGE_PATTERNS: List[Tuple[str, str, str]] = [
    (r"whenever you gain life.*each opponent loses",              "lifegain", "drain-payoff"),
    (r"target opponent loses x life.*amount of life you gained", "lifegain", "burst-payoff"),
    (r"whenever you gain life.*put.*counter",                    "lifegain", "counter-payoff"),
    (r"whenever you gain life.*draw",                            "lifegain", "draw-payoff"),
    (r"create a food token",                                     "lifegain", "food-enabler"),
    (r"sacrifice.*food.*gain",                                   "lifegain", "food-sac-gain"),
    (r"whenever .{0,30} attacks.*you gain \d+ life",             "lifegain", "attack-lifegain"),
    (r"whenever a (creature|bat|vampire|cleric) .{0,20}you control (enters|attacks|dies).*gain",
                                                                 "lifegain", "tribe-lifegain"),
]

# ─── CMC bracket helper ──────────────────────────────────────────────────────
def _cmc_bracket(cmc: float) -> int:
    """0-1=early, 2-3=mid-low, 4-5=mid-high, 6+=late"""
    if cmc <= 1: return 0
    if cmc <= 3: return 1
    if cmc <= 5: return 2
    return 3


# ─── Card loading ────────────────────────────────────────────────────────────

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
            except Exception as exc:
                print(f"[WARN] Skipped {csv_file.name}: {exc}", file=sys.stderr)
                continue

    return found


_GATE3_ROW_RE = re.compile(r"\|\s*(\d+)\s*\|\s*([^|\n]{2,60})\s*\|")

_SKIP_HEADERS = {
    "card name", "card", "qty", "quantity", "mana", "source file",
    "set/collector", "role/justification", "role", "color", "total pips",
    "key cards", "required sources", "actual sources", "status",
    "land name", "colors produced", "label", "command",
}


def extract_names_from_session(content: str) -> List[str]:
    names: List[str] = []
    seen: Set[str] = set()

    def add(name: str):
        key = name.lower().strip()
        if key and key not in seen and len(key) >= 3:
            seen.add(key)
            names.append(name.strip())

    gate_sections = re.split(r"# GATE [35][^#]*", content)
    for section in gate_sections[1:]:
        for line in section.splitlines():
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) < 3:
                continue
            qty_cell  = parts[0]
            name_cell = parts[1] if len(parts) > 1 else ""
            if name_cell.lower() in _SKIP_HEADERS:
                continue
            if re.match(r"^-+$", name_cell):
                continue
            if not name_cell:
                continue
            if qty_cell and not re.match(r"^\d+$", qty_cell.strip()):
                continue
            if re.match(r"^[A-Z][a-zA-Z',\- ]{1,50}$", name_cell):
                add(name_cell)

    code_blocks = re.findall(r"```[^\n]*\n(.*?)```", content, re.DOTALL)
    for block in code_blocks:
        lines = block.splitlines()
        for line in lines[1:]:
            if not line.strip() or line.startswith("#") or line.startswith("-"):
                continue
            parts = line.split(",")
            if parts:
                candidate = parts[0].strip().strip('"')
                if candidate and candidate.lower() not in _SKIP_HEADERS:
                    if re.match(r"^[A-Z][a-zA-Z',\- ]{1,50}$", candidate):
                        add(candidate)

    return names


def extract_names_from_decklist(path: Path) -> List[str]:
    """Legacy: Extract mainboard + sideboard card names (drops quantities)."""
    main, side = parse_decklist(path)
    return [name for _, name in main + side]


def extract_deck_entries_from_decklist(
    path: Path, include_sideboard: bool = False
) -> List[Dict]:
    """Return counted deck entries. Default: mainboard only."""
    main, side = parse_decklist(path)
    entries = [{"name": name, "qty": qty, "section": "main"} for qty, name in main]
    if include_sideboard:
        entries += [{"name": name, "qty": qty, "section": "side"} for qty, name in side]
    return entries


def attach_card_data(
    entries: List[Dict], card_data: Dict[str, Dict]
) -> Tuple[List[Dict], List[Dict]]:
    """Attach DB row to each entry. Returns (annotated, missing)."""
    annotated: List[Dict] = []
    missing:   List[Dict] = []
    for e in entries:
        row  = dict(e)
        data = card_data.get(e["name"].lower())
        if data:
            row["data"]        = data
            row["found_in_db"] = True
        else:
            row["data"]        = None
            row["found_in_db"] = False
            missing.append(row)
        annotated.append(row)
    return annotated, missing


def extract_names_from_pools(input_path: Path) -> List[str]:
    if input_path.is_file():
        pools_dir = input_path.parent / "pools"
    elif (input_path / "pools").exists():
        pools_dir = input_path / "pools"
    else:
        pools_dir = input_path

    names = []
    seen: Set[str] = set()
    for pool_file in sorted(pools_dir.glob("pool_*.csv")):
        try:
            content = pool_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                parts = line.split(",")
                if not parts:
                    continue
                candidate = parts[0].strip().strip('"')
                if candidate and candidate.lower() not in _SKIP_HEADERS and candidate.lower() not in seen:
                    seen.add(candidate.lower())
                    names.append(candidate)
        except Exception:
            continue
    return names


def extract_names_from_text(content: str) -> List[str]:
    names = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("//"):
            names.append(line)
    return names


# ─── Role classification ─────────────────────────────────────────────────────

def infer_primary_axes(profiles: List[Dict], override: str = "") -> Set[str]:
    """Detect dominant mechanic axes from tag frequency (threshold: 3+ cards)."""
    if override:
        return {x.strip().lower() for x in override.split(",") if x.strip()}
    counts: Dict[str, int] = {}
    for p in profiles:
        tags = (
            set(p.get("source_tags", set()))
            | set(p.get("payoff_tags", set()))
            | set(p.get("broad_tags",  set()))
        )
        for t in tags & CORE_ENGINE_TAGS:
            counts[t] = counts.get(t, 0) + 1
    return {t for t, c in counts.items() if c >= 3}


def classify_role(profile: Dict, primary_axes: Set[str]) -> str:
    """Classify a card's role relative to the deck's primary mechanic axes."""
    src   = set(profile.get("source_tags",  set()))
    pay   = set(profile.get("payoff_tags",  set()))
    broad = set(profile.get("broad_tags",   set()))
    core  = (src | pay | broad) & primary_axes
    if core and src and pay:
        return "engine"
    if pay & primary_axes:
        return "payoff"
    if src & primary_axes:
        return "enabler"
    if broad & INTERACTION_TAGS:
        return "interaction"
    if broad & SUPPORT_TAGS:
        return "support"
    return "support"


# ─── Weighted scoring helpers ────────────────────────────────────────────────

def _apply_weighted(
    scores: Dict[str, Dict],
    name_a: str,
    name_b: str,
    itype: str,
    primary_axes: Set[str],
) -> None:
    weight  = 2.0 if itype in {"FEEDS", "TRIGGERS", "ENABLES"} else 1.0
    boost_a = 1.0 + 0.25 * max(scores[name_a]["qty"] - 1, 0)
    boost_b = 1.0 + 0.25 * max(scores[name_b]["qty"] - 1, 0)
    scores[name_a]["weighted_synergy"] += weight * boost_b
    scores[name_b]["weighted_synergy"] += weight * boost_a
    engine_roles = {"engine", "enabler", "payoff"}
    if scores[name_a]["role"] in engine_roles and scores[name_b]["role"] in engine_roles:
        scores[name_a]["engine_partners"].add(name_b)
        scores[name_b]["engine_partners"].add(name_a)
        scores[name_a]["engine_synergy"] += weight * boost_b
        scores[name_b]["engine_synergy"] += weight * boost_a
    else:
        scores[name_a]["support_partners"].add(name_b)
        scores[name_b]["support_partners"].add(name_a)


def _add_oracle_bridge(
    scores: Dict[str, Dict],
    payoff_name: str,
    source_name: str,
    note: str,
    primary_axes: Set[str],
) -> None:
    if payoff_name not in scores or source_name not in scores:
        return
    scores[payoff_name]["interactions"].append((source_name, "TRIGGERS", note, "oracle"))
    for a, b in [(payoff_name, source_name), (source_name, payoff_name)]:
        scores[a]["synergy_partners"].add(b)
        scores[a]["engine_partners"].add(b)
        scores[a]["role_breadth_types"].add("TRIGGERS")
    scores[payoff_name]["weighted_synergy"] += 3.0
    scores[source_name]["weighted_synergy"] += 3.0
    scores[payoff_name]["engine_synergy"]   += 3.0
    scores[source_name]["engine_synergy"]   += 3.0


# ─── Synergy scoring ─────────────────────────────────────────────────────────

def score_pairwise(cards_or_entries, score_mode: str = "role-aware", primary_axis: str = "") -> Dict[str, Dict]:
    """
    Compute synergy scores using directional profiles.

    Pass 1  — Rule-based tag matching
    Pass 2  — Oracle subtype + keyword cross-reference
    Pass 2b — Oracle payoff bridges (drain, food, tribe triggers)
    Pass 3  — REDUNDANT: same narrow role at same CMC bracket
    Pass 4  — Dependency scoring
    """
    profiles:       Dict[str, dict] = {}
    qty_by_name:    Dict[str, int]  = {}
    section_by_name:Dict[str, str]  = {}

    if isinstance(cards_or_entries, list):
        for e in cards_or_entries:
            if not e.get("found_in_db") or not e.get("data"):
                continue
            p = compute_synergy_profile(e["data"])
            if p["is_land"]:
                continue
            key = e["name"].lower()
            profiles[key]         = p
            qty_by_name[key]      = int(e.get("qty", 1))
            section_by_name[key]  = e.get("section", "pool")
    else:
        for name, data in cards_or_entries.items():
            p = compute_synergy_profile(data)
            if p["is_land"]:
                continue
            profiles[name]         = p
            qty_by_name[name]      = 1
            section_by_name[name]  = "pool"

    primary_axes = infer_primary_axes(list(profiles.values()), override=primary_axis)

    scores: Dict[str, Dict] = {
        name: {
            "profile":            profiles[name],
            "qty":                qty_by_name.get(name, 1),
            "section":            section_by_name.get(name, "pool"),
            "role":               classify_role(profiles[name], primary_axes),
            "synergy_partners":   set(),
            "engine_partners":    set(),
            "support_partners":   set(),
            "role_breadth_types": set(),
            "dependency":         0,
            "interactions":       [],
            "redundant_with":     [],
            "weighted_synergy":   0.0,
            "engine_synergy":     0.0,
        }
        for name in profiles
    }

    names = list(profiles.keys())

    # ── Pass 1: Rule-based tag interactions ──────────────────────────────────
    for i, name_a in enumerate(names):
        pa = profiles[name_a]
        for name_b in names[i + 1:]:
            pb = profiles[name_b]
            for field_a, val_a, field_b, val_b, itype, note_tmpl in INTERACTION_RULES:
                if val_a in pa[field_a] and val_b in pb[field_b]:
                    note = note_tmpl.format(a=name_a, b=name_b)
                    scores[name_a]["interactions"].append((name_b, itype, note, "tag"))
                    if itype != "REDUNDANT":
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_a]["role_breadth_types"].add(itype)
                        scores[name_b]["role_breadth_types"].add(itype)
                        _apply_weighted(scores, name_a, name_b, itype, primary_axes)
                if val_a in pb[field_a] and val_b in pa[field_b]:
                    note = note_tmpl.format(a=name_b, b=name_a)
                    scores[name_b]["interactions"].append((name_a, itype, note, "tag"))
                    if itype != "REDUNDANT":
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_b]["role_breadth_types"].add(itype)
                        scores[name_a]["role_breadth_types"].add(itype)
                        _apply_weighted(scores, name_b, name_a, itype, primary_axes)

    # ── Pass 2: Oracle text cross-reference ──────────────────────────────────
    for i, name_a in enumerate(names):
        pa = profiles[name_a]
        for name_b in names[i + 1:]:
            pb = profiles[name_b]
            for subtype in pa["subtypes"]:
                if len(subtype) < 3:
                    continue
                if re.search(r"\b" + re.escape(subtype) + r"\b", pb["oracle_text"]):
                    note = f"Oracle: {name_b} references '{subtype}' subtype that {name_a} has"
                    if not any(p == name_b for p, it, _, c in scores[name_a]["interactions"] if c == "oracle" and it == "TRIGGERS"):
                        scores[name_a]["interactions"].append((name_b, "TRIGGERS", note, "oracle"))
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_a]["role_breadth_types"].add("TRIGGERS")
                        scores[name_b]["role_breadth_types"].add("TRIGGERS")
            for subtype in pb["subtypes"]:
                if len(subtype) < 3:
                    continue
                if re.search(r"\b" + re.escape(subtype) + r"\b", pa["oracle_text"]):
                    note = f"Oracle: {name_a} references '{subtype}' subtype that {name_b} has"
                    if not any(p == name_a for p, it, _, c in scores[name_b]["interactions"] if c == "oracle" and it == "TRIGGERS"):
                        scores[name_b]["interactions"].append((name_a, "TRIGGERS", note, "oracle"))
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_b]["role_breadth_types"].add("TRIGGERS")
                        scores[name_a]["role_breadth_types"].add("TRIGGERS")
            for kw in pa["keywords"] & _ORACLE_KEYWORDS:
                pattern = r"(creature[s]? (with|that (have|has))|whenever a .{0,20})" + re.escape(kw)
                if re.search(pattern, pb["oracle_text"], re.IGNORECASE):
                    note = f"Oracle: {name_b} cares about '{kw}' that {name_a} has"
                    if not any(p == name_b and "keyword" in n for p, _, n, _ in scores[name_a]["interactions"]):
                        scores[name_a]["interactions"].append((name_b, "TRIGGERS", note, "oracle"))
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_a]["role_breadth_types"].add("TRIGGERS")
                        scores[name_b]["role_breadth_types"].add("TRIGGERS")

    # ── Pass 2b: Oracle payoff bridges ───────────────────────────────────────
    for i, name_a in enumerate(names):
        pa = profiles[name_a]
        for name_b in names[i + 1:]:
            pb = profiles[name_b]
            for pat, axis, label in _PAYOFF_BRIDGE_PATTERNS:
                if axis not in primary_axes:
                    continue
                a_text = pa["oracle_text"]
                b_text = pb["oracle_text"]
                b_tags = pb.get("source_tags", set()) | pb.get("payoff_tags", set()) | pb.get("broad_tags", set())
                a_tags = pa.get("source_tags", set()) | pa.get("payoff_tags", set()) | pa.get("broad_tags", set())
                if re.search(pat, a_text, re.IGNORECASE) and axis in b_tags:
                    note = f"Oracle payoff bridge [{label}]: {name_a} converts {axis} → payoff; {name_b} produces {axis}"
                    _add_oracle_bridge(scores, name_a, name_b, note, primary_axes)
                elif re.search(pat, b_text, re.IGNORECASE) and axis in a_tags:
                    note = f"Oracle payoff bridge [{label}]: {name_b} converts {axis} → payoff; {name_a} produces {axis}"
                    _add_oracle_bridge(scores, name_b, name_a, note, primary_axes)

    # ── Pass 3: REDUNDANT detection ───────────────────────────────────────────
    seen_redundant: Set[frozenset] = set()
    for i, name_a in enumerate(names):
        pa = profiles[name_a]
        for name_b in names[i + 1:]:
            pb = profiles[name_b]
            shared_roles = pa["broad_tags"] & pb["broad_tags"] & ROLE_TAGS
            if shared_roles and _cmc_bracket(pa["cmc"]) == _cmc_bracket(pb["cmc"]):
                pair = frozenset([name_a, name_b])
                if pair not in seen_redundant:
                    seen_redundant.add(pair)
                    note = f"Both are {', '.join(shared_roles)} at CMC {pa['cmc']}/{pb['cmc']} (same bracket)"
                    scores[name_a]["redundant_with"].append(name_b)
                    scores[name_b]["redundant_with"].append(name_a)
                    scores[name_a]["interactions"].append((name_b, "REDUNDANT", note, "role"))
                    scores[name_b]["interactions"].append((name_a, "REDUNDANT", note, "role"))

    # ── Pass 4: Dependency scoring ────────────────────────────────────────────
    for name, sc in scores.items():
        oracle = sc["profile"]["oracle_text"]
        dep = 0
        for pat, weight, _ in _DEP_PATTERNS:
            if re.search(pat, oracle, re.IGNORECASE):
                dep += weight
        sc["dependency"] = min(dep, 4)

    # ── Finalize counts ───────────────────────────────────────────────────────
    all_scored     = len(scores)
    engine_names   = [n for n, s in scores.items() if s["role"] in {"engine", "enabler", "payoff"}]
    max_possible   = max(all_scored - 1, 1)
    engine_possible= max(len(engine_names) - 1, 1)

    for name in scores:
        sc = scores[name]
        sc["synergy_count"]       = len(sc["synergy_partners"])
        sc["synergy_density"]     = sc["synergy_count"] / max_possible
        sc["engine_synergy_count"]= len(sc["engine_partners"])
        sc["engine_density"]      = (
            sc["engine_synergy_count"] / engine_possible
            if sc["role"] in {"engine", "enabler", "payoff"} else 0.0
        )
        sc["role_breadth"]        = len(sc["role_breadth_types"])
        sc["oracle_interactions"] = [
            (p, it, n) for p, it, n, conf in sc["interactions"] if conf == "oracle"
        ]

    return scores


# ─── Threshold calibration ───────────────────────────────────────────────────

def _get_thresholds(pool_size: int, mode: str = "auto") -> dict:
    if mode == "auto":
        mode = "pool" if pool_size > 40 else "deck"

    if mode == "deck":
        return {
            "min_avg_density":          0.25,
            "min_engine_avg_density":   0.40,
            "max_isolated_frac":        0.12,
            "max_true_isolated_engine": 2,
            "min_hub_density":          0.50,
            "min_hub_count":            2,
            "max_support_ratio":        0.45,
            "mode_label":               "deck (role-aware)",
        }
    else:
        return {
            "min_avg_density":          0.20,
            "min_engine_avg_density":   0.30,
            "max_isolated_frac":        0.15,
            "max_true_isolated_engine": 3,
            "min_hub_density":          0.40,
            "min_hub_count":            2,
            "max_support_ratio":        0.55,
            "mode_label":               "pool (loose)",
        }


def check_thresholds(
    scores: Dict[str, Dict],
    min_avg: float,
    mode: str = "auto",
) -> Tuple[bool, List[str]]:
    msgs: List[str] = []
    passed = True

    if not scores:
        return False, ["No cards to evaluate."]

    pool_size = len(scores)
    dt        = _get_thresholds(pool_size, mode)
    if mode == "auto":
        mode = "pool" if pool_size > 40 else "deck"

    densities       = [s["synergy_density"]  for s in scores.values()]
    avg_density     = sum(densities) / len(densities)
    engine_scores   = [s for s in scores.values() if s["role"] in {"engine", "enabler", "payoff"}]
    engine_densities= [s["engine_density"]   for s in engine_scores]
    engine_avg      = sum(engine_densities) / len(engine_densities) if engine_densities else 0.0
    support_count   = sum(1 for s in scores.values() if s["role"] in {"support", "interaction"})
    support_ratio   = support_count / max(pool_size, 1)

    msgs.append(f"[INFO] Mode: {dt['mode_label']} — {pool_size} non-land cards evaluated "
                f"({len(engine_scores)} engine/enabler/payoff, {support_count} support/interaction)")

    # T1: overall avg density
    if avg_density >= dt["min_avg_density"]:
        msgs.append(f"[PASS] T1: Avg Synergy Density = {avg_density:.1%} (≥ {dt['min_avg_density']:.0%})")
    else:
        msgs.append(f"[FAIL] T1: Avg Synergy Density = {avg_density:.1%} (need ≥ {dt['min_avg_density']:.0%})")
        passed = False

    # T1b: engine avg density
    if engine_avg >= dt["min_engine_avg_density"]:
        msgs.append(f"[PASS] T1b: Avg Engine Density = {engine_avg:.1%} (≥ {dt['min_engine_avg_density']:.0%})")
    else:
        msgs.append(f"[FAIL] T1b: Avg Engine Density = {engine_avg:.1%} (need ≥ {dt['min_engine_avg_density']:.0%})")
        passed = False

    # T2: true isolated engine/payoff cards only
    true_isolated = [
        n for n, s in scores.items()
        if s["role"] in {"engine", "enabler", "payoff"} and s["engine_density"] <= 0.10
    ]
    isolated_all = [n for n, s in scores.items() if s["synergy_density"] <= 0.05]
    max_isolated = max(1, int(pool_size * dt["max_isolated_frac"]))

    if len(true_isolated) <= dt["max_true_isolated_engine"]:
        msgs.append(f"[PASS] T2: {len(true_isolated)} truly isolated engine/payoff cards "
                    f"(≤ {dt['max_true_isolated_engine']})")
    else:
        msgs.append(f"[FAIL] T2: {len(true_isolated)} truly isolated engine/payoff cards "
                    f"(max {dt['max_true_isolated_engine']}): "
                    + ", ".join(true_isolated[:6]) + ("..." if len(true_isolated) > 6 else ""))
        passed = False

    if isolated_all:
        support_iso = [n for n in isolated_all if scores[n]["role"] in {"support", "interaction"}]
        if support_iso:
            msgs.append(f"[INFO] T2b: {len(support_iso)} low-connectivity support/interaction cards "
                        f"(not counted against T2): {', '.join(support_iso[:6])}")

    # T3: hub cards
    hubs = [n for n, s in scores.items() if s["synergy_density"] >= dt["min_hub_density"]]
    if len(hubs) >= dt["min_hub_count"]:
        msgs.append(f"[PASS] T3: {len(hubs)} hub cards (density ≥ {dt['min_hub_density']:.0%}): "
                    + ", ".join(hubs[:5]) + ("..." if len(hubs) > 5 else ""))
    else:
        msgs.append(f"[FAIL] T3: Only {len(hubs)} hub card(s) with density ≥ {dt['min_hub_density']:.0%} "
                    f"(need {dt['min_hub_count']}+)")
        passed = False

    # T3b: support ratio
    if support_ratio <= dt["max_support_ratio"]:
        msgs.append(f"[PASS] T3b: Support/interaction ratio = {support_ratio:.1%} "
                    f"(≤ {dt['max_support_ratio']:.0%})")
    else:
        msgs.append(f"[FAIL] T3b: Support/interaction ratio = {support_ratio:.1%} "
                    f"(too high — max {dt['max_support_ratio']:.0%})")
        passed = False

    # T4: high-dependency cards
    high_dep = [f"{n} (dep={s['dependency']})" for n, s in scores.items() if s["dependency"] >= 3]
    if not high_dep:
        msgs.append("[PASS] T4: No cards with Dependency ≥ 3")
    else:
        msgs.append(f"[FAIL] T4: High-dependency cards found: {', '.join(high_dep)}")
        passed = False

    # T5: oracle coverage info
    oracle_confirmed = sum(len(s["oracle_interactions"]) for s in scores.values())
    pct = oracle_confirmed / max(sum(s["synergy_count"] for s in scores.values()), 1)
    msgs.append(f"[INFO] T5: {oracle_confirmed} oracle-confirmed interactions "
                f"({pct:.0%} of total) — remainder are tag-inferred")

    return passed, msgs


# ─── Report generation ───────────────────────────────────────────────────────

def _earliest_chain_turn(chain_cards: list, land_count: int = 24, deck_size: int = 60) -> int:
    """Estimate earliest turn a synergy chain fires (CMC-based, no ramp modeled)."""
    if not chain_cards:
        return 0
    max_cmc = max(float(c.get("cmc") or 0) for c in chain_cards)
    return max(1, int(max_cmc))


def build_report(
    scores: Dict[str, Dict],
    threshold_msgs: List[str],
    all_passed: bool,
    source_file: str,
    not_found: List[str],
    mode: str = "auto",
    inconclusive: bool = False,
) -> str:
    lines = [
        "# Gate 2.5: Synergy Evaluation",
        "",
        f"> Auto-generated by `scripts/synergy_analysis.py` from `{source_file}`",
        "> Interaction confidence: **oracle** = verified against card text · **tag** = tag-pair rule",
        "> Lands excluded from scoring. Role-aware: engine/enabler/payoff cards drive thresholds.",
        "",
        "---",
        "",
        "## Synergy Scores",
        "",
        "| Card | Qty | Role | Source Tags | Payoff Tags | Engine (Density) | Total / Weighted | Dep | Oracle | Key Partners |",
        "|------|:---:|------|------------|------------|:----------------:|:----------------:|:---:|:------:|-------------|",
    ]

    sorted_cards = sorted(
        scores.items(),
        key=lambda x: (-len(x[1].get("oracle_interactions", [])), -x[1]["synergy_count"])
    )

    for name, sc in sorted_cards:
        p          = sc["profile"]
        src        = ", ".join(sorted(p["source_tags"])) or "—"
        pay        = ", ".join(sorted(p["payoff_tags"])) or "—"
        engine_str = f"{sc.get('engine_synergy_count', 0)} ({sc.get('engine_density', 0):.0%})"
        total_str  = f"{sc['synergy_count']} / {sc.get('weighted_synergy', 0):.1f}"
        oracle_n   = len(sc["oracle_interactions"])
        partners   = list(sc["synergy_partners"])[:3]
        partner_str= ", ".join(partners) + ("…" if len(sc["synergy_partners"]) > 3 else "")
        lines.append(
            f"| {name} | {sc.get('qty',1)} | {sc.get('role','—')} | {src} | {pay} "
            f"| {engine_str} | {total_str} | {sc['dependency']} | {oracle_n} | {partner_str or '—'} |"
        )

    if not_found:
        lines += [
            "",
            f"> **Note:** {len(not_found)} card(s) not in local database — excluded from scoring:",
            f"> {', '.join(not_found[:10])}{'...' if len(not_found) > 10 else ''}",
        ]

    pool_size   = len(scores)
    dt          = _get_thresholds(pool_size, mode)
    counts      = [s["synergy_count"]   for s in scores.values()]
    densities   = [s["synergy_density"] for s in scores.values()]
    avg         = sum(counts)    / len(counts)    if counts    else 0
    avg_density = sum(densities) / len(densities) if densities else 0.0
    engine_sc   = [s for s in scores.values() if s["role"] in {"engine","enabler","payoff"}]
    engine_avg  = sum(s["engine_density"] for s in engine_sc) / max(len(engine_sc), 1)
    isolated    = [n for n, s in scores.items() if s["synergy_density"] <= 0.05]
    max_isolated= max(1, int(pool_size * dt["max_isolated_frac"]))
    hubs        = [n for n, s in scores.items() if s["synergy_density"] >= dt["min_hub_density"]]
    oracle_total= sum(len(s["oracle_interactions"]) for s in scores.values())
    support_n   = sum(1 for s in scores.values() if s["role"] in {"support","interaction"})

    lines += [
        "",
        f"**Pool size (non-land):** {pool_size}  |  **Mode:** {dt['mode_label']}",
        f"**Engine/enabler/payoff:** {len(engine_sc)}  |  **Support/interaction:** {support_n}",
        f"**Avg Synergy Count:** {avg:.1f}  |  **Avg Density:** {avg_density:.1%} (threshold ≥ {dt['min_avg_density']:.0%})",
        f"**Avg Engine Density:** {engine_avg:.1%} (threshold ≥ {dt['min_engine_avg_density']:.0%})",
        f"**Hub cards (density ≥ {dt['min_hub_density']:.0%}):** {len(hubs)} (min {dt['min_hub_count']})",
        f"**Oracle-confirmed interactions:** {oracle_total}",
        "",
        "---",
        "",
        "## Gate 2.5 Threshold Check",
        "",
    ]

    for msg in threshold_msgs:
        if msg.startswith("[PASS]"):
            prefix = "- [x]"
        elif msg.startswith("[FAIL]"):
            prefix = "- [ ]"
        else:
            prefix = "- ℹ️ "
        lines.append(f"{prefix} {msg}")

    if inconclusive:
        overall = "**⚠️ Result is INCONCLUSIVE — missing maindeck card data prevented a reliable verdict.**"
    elif all_passed:
        overall = "**✅ All thresholds passed — proceed to Gate 3.**"
    else:
        overall = "**❌ Cohesion thresholds failed — revisit maindeck engine/support balance before Gate 3.**"
    lines += ["", overall, ""]

    # Oracle-confirmed interactions
    oracle_pairs = [
        (name, partner, itype, note)
        for name, sc in sorted_cards
        for partner, itype, note, conf in sc["interactions"]
        if conf == "oracle"
    ]
    if oracle_pairs:
        lines += [
            "---", "",
            "## Oracle-Confirmed Interactions", "",
            "> These interactions were verified against actual card text — highest confidence.", "",
            "| Card A | Card B | Type | Evidence |",
            "|--------|--------|------|----------|",
        ]
        seen_oracle: Set[frozenset] = set()
        for name, partner, itype, note in oracle_pairs[:30]:
            pair = frozenset([name, partner])
            if pair not in seen_oracle:
                seen_oracle.add(pair)
                lines.append(f"| {name} | {partner} | {itype} | {note} |")
        lines.append("")

    # Redundant pairs
    seen_pairs: Set[frozenset] = set()
    redundant_pairs = []
    for name, sc in scores.items():
        for partner in sc["redundant_with"]:
            pair = frozenset([name, partner])
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                shared = sc["profile"]["broad_tags"] & scores[partner]["profile"]["broad_tags"] & ROLE_TAGS
                redundant_pairs.append((name, partner, shared))

    if redundant_pairs:
        lines += [
            "---", "",
            "## Redundant Pairs", "",
            "| Card A | Card B | Shared Role | CMC Brackets | Justification for Both |",
            "|--------|--------|-------------|:------------:|------------------------|",
        ]
        for a, b, roles in redundant_pairs[:20]:
            role_str = ", ".join(roles) if roles else "same role"
            cmc_a = scores[a]["profile"]["cmc"]
            cmc_b = scores[b]["profile"]["cmc"]
            lines.append(f"| {a} | {b} | {role_str} | {cmc_a}/{cmc_b} | *(fill in)* |")
        lines.append("")

    # Synergy chains
    lines += [
        "---", "",
        "## Synergy Chains", "",
        "> Map 2-3 chains using hub cards as anchors. Prefer oracle-confirmed interactions.",
        "> Format: [Card A] → [what A produces] → [Card B] → [outcome]", "",
    ]
    chain_anchors = [
        (name, sc) for name, sc in sorted_cards if sc["synergy_count"] >= 3
    ][:3]

    chain_timing_data = []
    if chain_anchors:
        for i, (hub_name, hub_sc) in enumerate(chain_anchors, 1):
            oracle_partners = [p for p, it, n, c in hub_sc["interactions"] if c == "oracle"]
            tag_partners    = list(hub_sc["synergy_partners"])
            partner_list    = (oracle_partners + [p for p in tag_partners if p not in oracle_partners])[:2]
            chain           = " → ".join(f"[{c}]" for c in [hub_name] + partner_list)
            oracle_label    = " ⭐oracle" if oracle_partners else ""
            chain_cards     = [scores[n]["profile"] for n in [hub_name] + partner_list if n in scores]
            earliest_turn   = _earliest_chain_turn(chain_cards)
            chain_timing_data.append((i, earliest_turn))
            timing_label    = "⚠️ SLOW" if earliest_turn >= 5 else "✅ ON CURVE"
            lines += [
                f"**Chain {i} — [{hub_name} engine]{oracle_label}:**",
                chain + " → [outcome]",
                f"Earliest firing turn: T{earliest_turn} (CMC-based, no ramp modeled) — {timing_label}",
            ]
            if earliest_turn >= 5:
                lines.append("⚠️ SLOW CHAIN: Requires T5+ to fully assemble. Verify against meta kill turn.")
            lines += ["Redundancy: *(fill in)*", "Minimum pieces to function: N of M", ""]
    else:
        lines += [
            "**Chain 1:**",
            "[Card A] → [output] → [Card B] → [outcome]",
            "Redundancy: *(fill in)*",
            "Minimum pieces to function: N of M", "",
        ]

    slow_chains = [c for c in chain_timing_data if c[1] >= 5]
    if len(slow_chains) > 1:
        threshold_msgs.append(
            f"[WARN] T6: {len(slow_chains)} synergy chains require T5+ to assemble. "
            f"Consider adding ramp or lower-CMC redundancy."
        )

    lines += [
        "---", "",
        "## Gate 2.5 Checklist", "",
        f"- [{'x' if all_passed else ' '}] All candidates scored (Synergy Count, Role Breadth, Dependency)",
        f"- [{'x' if any('T1' in m and 'PASS' in m for m in threshold_msgs) else ' '}] Avg Synergy Density ≥ {dt['min_avg_density']:.0%}",
        f"- [{'x' if any('T1b' in m and 'PASS' in m for m in threshold_msgs) else ' '}] Avg Engine Density ≥ {dt['min_engine_avg_density']:.0%}",
        f"- [{'x' if any('T2' in m and 'PASS' in m and 'T2b' not in m for m in threshold_msgs) else ' '}] ≤ {dt['max_true_isolated_engine']} true isolated engine cards",
        f"- [{'x' if len(hubs) >= dt['min_hub_count'] else ' '}] ≥ {dt['min_hub_count']} hub cards",
        f"- [{'x' if not any(s['dependency'] >= 3 for s in scores.values()) else ' '}] No card with Dependency ≥ 3",
        "- [ ] All REDUNDANT pairs justified  *(fill in above)*",
        "- [ ] 2–3 synergy chains mapped  *(fill in above)*",
        "- [ ] All analysis based on Gate 1 query results — not memory",
        "",
        "**If any item is unchecked, do not proceed to Gate 3.**",
    ]

    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="Gate 2.5 synergy analysis — role-aware, oracle-verified pairwise scoring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("input_file", help="session.md, decklist.txt, pools/ dir, or names list")
    p.add_argument("--format", choices=["auto", "session", "decklist", "names", "pools"],
                   default="auto", help="Input format (default: auto-detect)")
    p.add_argument("--output",   help="Write report to this file (default: stdout)")
    p.add_argument("--min-synergy", type=float, default=3.0,
                   help="(legacy) Minimum average synergy count — superseded by --mode thresholds")
    p.add_argument("--mode", choices=["auto", "pool", "deck"], default="auto",
                   help="Threshold calibration: pool, deck, or auto (default)")
    p.add_argument("--top", type=int, default=0, metavar="N",
                   help="Write top-N CSV ranked by composite synergy score.")
    p.add_argument("--include-sideboard", action="store_true",
                   help="Include sideboard cards in scoring (default: mainboard only).")
    p.add_argument("--allow-missing", action="store_true",
                   help="Skip inconclusive guard when maindeck cards are missing from DB.")
    p.add_argument("--score-mode", choices=["legacy", "role-aware"], default="role-aware",
                   help="Scoring model (default: role-aware).")
    p.add_argument("--primary-axis", default="",
                   help="Comma-separated mechanic override, e.g. lifegain,token,sacrifice")
    args = p.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found.", file=sys.stderr)
        sys.exit(2)

    content = input_path.read_text(encoding="utf-8") if input_path.is_file() else ""

    fmt = args.format
    if fmt == "auto":
        if "session.md" in input_path.name.lower() or "# Deck Building Session" in content:
            fmt = "session"
        elif input_path.is_dir() or (input_path.parent / "pools").exists():
            fmt = "pools"
        elif "Deck\n" in content or content.strip().startswith("Deck"):
            fmt = "decklist"
        else:
            fmt = "names"

    # Build entries list
    if fmt == "decklist":
        entries = extract_deck_entries_from_decklist(
            input_path, include_sideboard=args.include_sideboard
        )
    elif fmt == "session":
        entries = [{"name": n, "qty": 1, "section": "pool"}
                   for n in extract_names_from_session(content)]
    elif fmt == "pools":
        entries = [{"name": n, "qty": 1, "section": "pool"}
                   for n in extract_names_from_pools(input_path)]
    else:
        entries = [{"name": n, "qty": 1, "section": "pool"}
                   for n in extract_names_from_text(content)]

    seen: Set[str] = set()
    unique_names: List[str] = []
    for e in entries:
        if e["name"].lower() not in seen:
            seen.add(e["name"].lower())
            unique_names.append(e["name"])

    if not unique_names:
        print("ERROR: No card names extracted from input.", file=sys.stderr)
        sys.exit(2)

    print(f"Loaded {len(unique_names)} unique cards from {input_path.name}", file=sys.stderr)
    print("Looking up card data in local database...", file=sys.stderr)

    paths     = RepoPaths()
    card_data = load_cards_from_db(unique_names, paths)
    annotated_entries, missing = attach_card_data(entries, card_data)
    missing_main = [e["name"] for e in missing if e["section"] == "main"]
    missing_side = [e["name"] for e in missing if e["section"] == "side"]
    missing_pool = [e["name"] for e in missing if e["section"] == "pool"]
    not_found    = [e["name"] for e in missing]

    if not_found:
        print(
            f"  {len(not_found)} card(s) not found in DB: {', '.join(not_found[:5])}",
            file=sys.stderr,
        )

    # Inconclusive guard for deck mode
    effective_mode = args.mode
    if effective_mode == "auto":
        effective_mode = "pool" if len(unique_names) > 40 else "deck"

    inconclusive = False
    if effective_mode == "deck" and missing_main and not args.allow_missing:
        inconclusive = True
        print(
            f"[WARN] {len(missing_main)} maindeck card(s) missing from DB — result will be INCONCLUSIVE. "
            f"Use --allow-missing to override.",
            file=sys.stderr,
        )

    print("Scoring pairwise synergies (5-pass: tag → oracle → bridges → redundant → dependency)...",
          file=sys.stderr)

    if args.score_mode == "legacy":
        legacy_cards = {e["name"].lower(): e["data"] for e in annotated_entries if e.get("data")}
        # backfill missing as empty dicts for legacy compat
        for name in not_found:
            legacy_cards[name.lower()] = {"name": name}
        scores = score_pairwise(legacy_cards)
    else:
        scores = score_pairwise(
            annotated_entries,
            score_mode=args.score_mode,
            primary_axis=args.primary_axis,
        )

    all_passed, threshold_msgs = check_thresholds(scores, args.min_synergy, args.mode)

    report = build_report(
        scores, threshold_msgs, all_passed,
        str(input_path), not_found, args.mode,
        inconclusive=inconclusive,
    )

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    # ── Top-N ranked export ──────────────────────────────────────────────────
    if args.top and args.top > 0:
        import io as _io
        top_n  = args.top
        ranked = sorted(
            scores.items(),
            key=lambda x: (-x[1].get("engine_synergy", 0), -x[1]["weighted_synergy"],
                           -x[1]["synergy_count"]),
        )[:top_n]

        TOP_COLS = ["rank", "name", "qty", "role", "mana_cost", "cmc", "type_line", "colors",
                    "rarity", "keywords", "oracle_text", "tags", "pool",
                    "engine_score", "engine_density", "synergy_score", "weighted_score",
                    "synergy_density", "role_breadth", "oracle_interactions",
                    "dependency", "top_partners"]

        pool_data: Dict[str, Dict] = {}
        candidate_csv = None
        if args.output:
            candidate_csv = Path(args.output).parent / "candidate_pool.csv"
        elif input_path.is_file():
            candidate_csv = input_path.parent / "candidate_pool.csv"
        if candidate_csv and candidate_csv.exists():
            with open(candidate_csv, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    pool_data[row.get("name", "").strip().lower()] = row

        buf = _io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=TOP_COLS, extrasaction="ignore")
        writer.writeheader()
        for rank_i, (name, sc) in enumerate(ranked, 1):
            pr = sc["profile"]
            pd = pool_data.get(name.lower(), {})
            oracle = pd.get("oracle_text", pr.get("oracle_text", ""))
            writer.writerow({
                "rank":               rank_i,
                "name":               pr.get("name", name),
                "qty":                sc.get("qty", 1),
                "role":               sc.get("role", ""),
                "mana_cost":          pr.get("mana_cost", pd.get("mana_cost", "")),
                "cmc":                pr.get("cmc", pd.get("cmc", "")),
                "type_line":          pr.get("type_line", pd.get("type_line", "")),
                "colors":             pr.get("colors", pd.get("colors", "")),
                "rarity":             pd.get("rarity", ""),
                "keywords":           ", ".join(sorted(pr.get("keywords", set()))),
                "oracle_text":        oracle,
                "tags":               ", ".join(sorted(pr.get("broad_tags", set()))),
                "pool":               pd.get("pool", ""),
                "engine_score":       sc.get("engine_synergy_count", 0),
                "engine_density":     f"{sc.get('engine_density', 0):.1%}",
                "synergy_score":      sc["synergy_count"],
                "weighted_score":     f"{sc.get('weighted_synergy', 0):.1f}",
                "synergy_density":    f"{sc['synergy_density']:.1%}",
                "role_breadth":       sc["role_breadth"],
                "oracle_interactions":len(sc.get("oracle_interactions", [])),
                "dependency":         sc["dependency"],
                "top_partners":       " | ".join(list(sc["synergy_partners"])[:5]),
            })

        top_path = (Path(args.output).parent if args.output else input_path.parent) / f"top_{top_n}.csv"
        top_path.write_text(buf.getvalue(), encoding="utf-8")
        print(f"Top {min(top_n, len(ranked))} cards written to {top_path}", file=sys.stderr)

    sys.exit(0 if (all_passed and not inconclusive) else 1)


if __name__ == "__main__":
    main()
