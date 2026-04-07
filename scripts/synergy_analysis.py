#!/usr/bin/env python3
"""
Synergy Analysis — Gate 2.5 Automation

Reads a card list (from a session.md candidate pool, a decklist.txt, a pool
CSV file, or a plain text file) and produces a Gate 2.5 synergy report:

  - Builds a directional synergy profile for every card (source vs. payoff tags,
    creature subtypes, keywords, CMC, oracle text)
  - Scores pairwise interactions in four passes:
      Pass 1 — Rule-based tag matching (source_tags → payoff_tags)
      Pass 2 — Oracle text cross-reference (subtype + keyword verification)
      Pass 3 — CMC-bracket-aware REDUNDANT detection (narrow roles only)
      Pass 4 — Oracle-text dependency scoring (Auras, Equipment, conditionals)
  - Checks all Gate 2.5 thresholds with pool-vs-deck calibration
  - Writes a pre-populated Gate 2.5 markdown block you can paste into session.md

Usage:
    # Analyze candidate pool extracted from a session.md
    python scripts/synergy_analysis.py Decks/2026-04-03_My_Deck/session.md

    # Analyze a finished decklist.txt
    python scripts/synergy_analysis.py Decks/2026-04-03_My_Deck/decklist.txt

    # Analyze pool CSV files in a pools/ directory
    python scripts/synergy_analysis.py Decks/2026-04-03_My_Deck/ --format pools

    # Analyze a plain card-name list (one name per line)
    python scripts/synergy_analysis.py my_candidates.txt --format names

    # Write report to a file instead of stdout
    python scripts/synergy_analysis.py session.md --output report.md

    # Force pool or deck threshold calibration
    python scripts/synergy_analysis.py decklist.txt --mode deck

Flags:
    --format    Input format: auto (default), session, decklist, names, pools
    --output    Write markdown report to this file (default: stdout)
    --mode      Threshold calibration: pool (large candidate pool, loose),
                deck (final 60-card, strict), or auto (default, size-based)

Exit codes:
    0  All Gate 2.5 thresholds passed
    1  One or more thresholds failed
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
# Format: (field_on_A, value_A, field_on_B, value_B, interaction_type, note_template)
# field must be one of: source_tags, payoff_tags, broad_tags, subtypes, keywords
# Rules are checked in both A→B and B→A directions.

INTERACTION_RULES: List[Tuple[str, str, str, str, str, str]] = [
    # ── FEEDS: A produces a resource, B consumes it ──────────────────────────
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

    # ── TRIGGERS: A's presence fires B's triggered ability ───────────────────
    ("source_tags", "token",       "payoff_tags", "token",       "TRIGGERS", "{a} creates tokens → {b}'s token-creation trigger fires"),

    # ── ENABLES: A makes B functional, cheaper, or castable ──────────────────
    ("broad_tags",  "ramp",        "broad_tags",  "wipe",        "ENABLES",  "{a} ramps mana → {b} expensive wipe becomes castable"),
    ("broad_tags",  "ramp",        "broad_tags",  "reanimation", "ENABLES",  "{a} ramps mana → {b} reanimation spell becomes castable"),
    ("broad_tags",  "ramp",        "broad_tags",  "pump",        "ENABLES",  "{a} produces mana → {b} activated pump ability"),
    ("broad_tags",  "protection",  "broad_tags",  "tribal",      "ENABLES",  "{a} protects key piece → {b} tribal engine survives"),
    ("broad_tags",  "tutor",       "broad_tags",  "draw",        "ENABLES",  "{a} tutors → {b} draw engine found reliably"),
    ("broad_tags",  "protection",  "source_tags", "lifegain",    "ENABLES",  "{a} protects → {b} lifegain engine survives removal"),

    # ── AMPLIFIES: A multiplies or scales B's output ─────────────────────────
    ("source_tags", "token",       "broad_tags",  "wipe",        "AMPLIFIES","Tokens → sacrifice synergy: {a} creates fodder for {b}"),
    ("broad_tags",  "pump",        "broad_tags",  "tribal",      "AMPLIFIES","Tribal anthem: {a} pump stacks with {b} tribal bonus"),
    ("source_tags", "pump",        "source_tags", "pump",        "AMPLIFIES","{a} + {b} both add counters — outputs stack"),

    # ── PROTECTS: A shields B or the strategy from disruption ────────────────
    ("broad_tags",  "protection",  "broad_tags",  "removal",     "PROTECTS", "{a} protects key creatures → {b} removal suite operates safely"),
    ("broad_tags",  "counter",     "broad_tags",  "protection",  "PROTECTS", "{a} counters removal → {b} protected threat survives"),
    ("broad_tags",  "bounce",      "broad_tags",  "counter",     "PROTECTS", "{a} bounces threats → {b} backup counter coverage"),
]

# Narrow roles for REDUNDANT detection — deliberately omits broad strategy tags
# (lifegain, tribal, mill, draw) since a deck intentionally runs multiples of these.
# Only same-function, same-CMC-bracket cards are flagged redundant.
ROLE_TAGS = {"wipe", "counter", "tutor", "reanimation"}

# ─── Keywords worth cross-referencing in oracle text ────────────────────────
_ORACLE_KEYWORDS = {
    "flying", "lifelink", "deathtouch", "first strike", "double strike",
    "vigilance", "trample", "haste", "menace", "reach", "indestructible",
}

# ─── Dependency oracle patterns (pattern, weight, label) ────────────────────
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
            except Exception:
                continue

    return found


# Matches Gate 3 table rows: | 4 | Card Name | ... |
_GATE3_ROW_RE = re.compile(r"\|\s*(\d+)\s*\|\s*([^|\n]{2,60})\s*\|")

_SKIP_HEADERS = {
    "card name", "card", "qty", "quantity", "mana", "source file",
    "set/collector", "role/justification", "role", "color", "total pips",
    "key cards", "required sources", "actual sources", "status",
    "land name", "colors produced", "label", "command",
}


def extract_names_from_session(content: str) -> List[str]:
    """
    Extract unique card names from a session.md by parsing:
    1. Gate 3 card selection tables (| Qty | Card Name | ... |)
    2. search_cards.py CSV output inside fenced code blocks
    """
    names: List[str] = []
    seen: Set[str] = set()

    def add(name: str):
        key = name.lower().strip()
        if key and key not in seen and len(key) >= 3:
            seen.add(key)
            names.append(name.strip())

    # 1. Parse Gate 3/5 card selection tables
    gate_sections = re.split(r"# GATE [35][^#]*", content)
    for section in gate_sections[1:]:
        for line in section.splitlines():
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) < 3:
                continue
            qty_cell = parts[0]
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

    # 2. Parse CSV output in fenced code blocks (name is first column)
    code_blocks = re.findall(r"```[^\n]*\n(.*?)```", content, re.DOTALL)
    for block in code_blocks:
        lines = block.splitlines()
        # Skip the header row
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
    """Extract mainboard + sideboard card names from a decklist.txt."""
    main, side = parse_decklist(path)
    return [name for _, name in main + side]


def extract_names_from_pools(input_path: Path) -> List[str]:
    """Read all pool_*.csv files from the pools/ directory."""
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
    """One card name per line."""
    names = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("//"):
            names.append(line)
    return names


# ─── Synergy scoring ─────────────────────────────────────────────────────────

def score_pairwise(cards: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Compute synergy scores using directional profiles.

    Pass 1 — Rule-based: check INTERACTION_RULES against source/payoff/broad tags.
    Pass 2 — Oracle cross-reference: scan card B's oracle text for card A's
             subtypes and keywords. Produces oracle-confirmed TRIGGERS.
    Pass 3 — REDUNDANT: cards sharing a narrow role tag at the same CMC bracket.
    Pass 4 — Dependency: regex suite against oracle text.
    """
    # Build profiles, excluding lands
    profiles: Dict[str, dict] = {}
    for name, data in cards.items():
        p = compute_synergy_profile(data)
        if p["is_land"]:
            continue
        profiles[name] = p

    scores: Dict[str, Dict] = {
        name: {
            "profile":            profiles[name],
            "synergy_partners":   set(),
            "role_breadth_types": set(),
            "dependency":         0,
            "interactions":       [],   # (partner, itype, note, confidence)
            "redundant_with":     [],
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
                # A → B
                if val_a in pa[field_a] and val_b in pb[field_b]:
                    note = note_tmpl.format(a=name_a, b=name_b)
                    scores[name_a]["interactions"].append((name_b, itype, note, "tag"))
                    if itype != "REDUNDANT":
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_a]["role_breadth_types"].add(itype)
                        scores[name_b]["role_breadth_types"].add(itype)
                # B → A
                if val_a in pb[field_a] and val_b in pa[field_b]:
                    note = note_tmpl.format(a=name_b, b=name_a)
                    scores[name_b]["interactions"].append((name_a, itype, note, "tag"))
                    if itype != "REDUNDANT":
                        scores[name_a]["synergy_partners"].add(name_b)
                        scores[name_b]["synergy_partners"].add(name_a)
                        scores[name_b]["role_breadth_types"].add(itype)
                        scores[name_a]["role_breadth_types"].add(itype)

    # ── Pass 2: Oracle text cross-reference ──────────────────────────────────
    # Does B's oracle text explicitly mention A's subtypes or keywords?
    for i, name_a in enumerate(names):
        pa = profiles[name_a]
        for name_b in names[i + 1:]:
            pb = profiles[name_b]

            # B's oracle mentions A's subtypes
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

            # A's oracle mentions B's subtypes
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

            # B's oracle mentions A's high-value keywords
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

    # ── Pass 3: REDUNDANT detection (CMC-bracket aware, narrow roles only) ───
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
    pool_size = len(scores)
    max_possible = max(pool_size - 1, 1)

    for name in scores:
        sc = scores[name]
        sc["synergy_count"] = len(sc["synergy_partners"])
        sc["synergy_density"] = sc["synergy_count"] / max_possible
        sc["role_breadth"] = len(sc["role_breadth_types"])
        sc["oracle_interactions"] = [
            (p, it, n) for p, it, n, conf in sc["interactions"] if conf == "oracle"
        ]

    return scores


# ─── Threshold calibration ───────────────────────────────────────────────────

def _get_thresholds(pool_size: int, mode: str = "auto") -> dict:
    """
    Return Gate 2.5 thresholds calibrated to pool size and mode.

    pool  — large candidate pool, pre-selection (loose)
    deck  — final 60-card deck, post-selection (strict)
    auto  — infer from size: pool if > 40, deck otherwise
    """
    if mode == "auto":
        mode = "pool" if pool_size > 40 else "deck"

    if mode == "deck":
        return {
            "min_avg_density":   0.35,
            "max_isolated_frac": 0.07,
            "min_hub_density":   0.50,
            "min_hub_count":     2,
            "mode_label":        "deck (strict)",
        }
    else:
        return {
            "min_avg_density":   0.20,
            "max_isolated_frac": 0.15,
            "min_hub_density":   0.40,
            "min_hub_count":     2,
            "mode_label":        "pool (loose)",
        }


def check_thresholds(
    scores: Dict[str, Dict],
    min_avg: float,
    mode: str = "auto",
) -> Tuple[bool, List[str]]:
    """Check all Gate 2.5 thresholds. Returns (all_passed, list_of_messages)."""
    msgs: List[str] = []
    passed = True

    if not scores:
        return False, ["No cards to evaluate."]

    pool_size = len(scores)
    dt = _get_thresholds(pool_size, mode)
    densities = [s["synergy_density"] for s in scores.values()]
    avg_density = sum(densities) / len(densities)

    msgs.append(f"[INFO] Mode: {dt['mode_label']} — {pool_size} non-land cards evaluated")

    # T1: average density
    if avg_density >= dt["min_avg_density"]:
        msgs.append(f"[PASS] T1: Avg Synergy Density = {avg_density:.1%} (≥ {dt['min_avg_density']:.0%})")
    else:
        msgs.append(f"[FAIL] T1: Avg Synergy Density = {avg_density:.1%} (need ≥ {dt['min_avg_density']:.0%})")
        passed = False

    # T2: isolated cards (density ≤ 5%)
    isolated = [n for n, s in scores.items() if s["synergy_density"] <= 0.05]
    max_isolated = max(1, int(pool_size * dt["max_isolated_frac"]))
    if len(isolated) <= max_isolated:
        msgs.append(f"[PASS] T2: {len(isolated)} isolated cards (≤ max {max_isolated})")
    else:
        msgs.append(
            f"[FAIL] T2: {len(isolated)} isolated cards (max {max_isolated}): "
            + ", ".join(isolated[:6]) + ("..." if len(isolated) > 6 else "")
        )
        passed = False

    # T3: hub cards
    hubs = [n for n, s in scores.items() if s["synergy_density"] >= dt["min_hub_density"]]
    if len(hubs) >= dt["min_hub_count"]:
        msgs.append(
            f"[PASS] T3: {len(hubs)} hub cards (density ≥ {dt['min_hub_density']:.0%}): "
            + ", ".join(hubs[:5]) + ("..." if len(hubs) > 5 else "")
        )
    else:
        msgs.append(f"[FAIL] T3: Only {len(hubs)} hub card(s) with density ≥ {dt['min_hub_density']:.0%} (need {dt['min_hub_count']}+)")
        passed = False

    # T4: high-dependency cards
    high_dep = [f"{n} (dep={s['dependency']})" for n, s in scores.items() if s["dependency"] >= 3]
    if not high_dep:
        msgs.append("[PASS] T4: No cards with Dependency ≥ 3")
    else:
        msgs.append(f"[FAIL] T4: High-dependency cards found: {', '.join(high_dep)}")
        passed = False

    # T5 (info): oracle-confirmed coverage
    oracle_confirmed = sum(len(s["oracle_interactions"]) for s in scores.values())
    pct = oracle_confirmed / max(sum(s["synergy_count"] for s in scores.values()), 1)
    msgs.append(
        f"[INFO] T5: {oracle_confirmed} oracle-confirmed interactions "
        f"({pct:.0%} of total) — remainder are tag-inferred"
    )

    return passed, msgs


# ─── Report generation ───────────────────────────────────────────────────────

def build_report(
    scores: Dict[str, Dict],
    threshold_msgs: List[str],
    all_passed: bool,
    source_file: str,
    not_found: List[str],
    mode: str = "auto",
) -> str:
    lines = [
        "# Gate 2.5: Synergy Evaluation",
        "",
        f"> Auto-generated by `scripts/synergy_analysis.py` from `{source_file}`",
        "> Interaction confidence: **oracle** = verified against card text · **tag** = tag-pair rule",
        "> Lands excluded from scoring. Review ENABLES/AMPLIFIES/PROTECTS manually for context.",
        "",
        "---",
        "",
        "## Synergy Scores",
        "",
        "| Card | Source Tags | Payoff Tags | Synergy (Density) | Breadth | Dep | Oracle | Key Partners |",
        "|------|------------|------------|:-----------------:|:-------:|:---:|:------:|-------------|",
    ]

    # Sort: oracle interactions first, then synergy count
    sorted_cards = sorted(
        scores.items(),
        key=lambda x: (-len(x[1].get("oracle_interactions", [])), -x[1]["synergy_count"])
    )

    for name, sc in sorted_cards:
        p = sc["profile"]
        src = ", ".join(sorted(p["source_tags"])) or "—"
        pay = ", ".join(sorted(p["payoff_tags"])) or "—"
        density_str = f"{sc['synergy_count']} ({sc['synergy_density']:.0%})"
        oracle_n = len(sc["oracle_interactions"])
        partners = list(sc["synergy_partners"])[:3]
        partner_str = ", ".join(partners) + ("…" if len(sc["synergy_partners"]) > 3 else "")
        lines.append(
            f"| {name} | {src} | {pay} | {density_str} "
            f"| {sc['role_breadth']} | {sc['dependency']} | {oracle_n} | {partner_str or '—'} |"
        )

    if not_found:
        lines += [
            "",
            f"> **Note:** {len(not_found)} card(s) not in local database — scored as 0 tags:",
            f"> {', '.join(not_found[:10])}{'...' if len(not_found) > 10 else ''}",
        ]

    pool_size = len(scores)
    dt = _get_thresholds(pool_size, mode)
    counts = [s["synergy_count"] for s in scores.values()]
    densities = [s["synergy_density"] for s in scores.values()]
    avg = sum(counts) / len(counts) if counts else 0
    avg_density = sum(densities) / len(densities) if densities else 0.0
    isolated = [n for n, s in scores.items() if s["synergy_density"] <= 0.05]
    max_isolated = max(1, int(pool_size * dt["max_isolated_frac"]))
    hubs = [n for n, s in scores.items() if s["synergy_density"] >= dt["min_hub_density"]]
    oracle_total = sum(len(s["oracle_interactions"]) for s in scores.values())

    lines += [
        "",
        f"**Pool size (non-land):** {pool_size}  |  **Mode:** {dt['mode_label']}",
        f"**Avg Synergy Count:** {avg:.1f}  |  **Avg Density:** {avg_density:.1%} (threshold ≥ {dt['min_avg_density']:.0%})",
        f"**Isolated (density ≤ 5%):** {len(isolated)} (max {max_isolated})  |  "
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

    overall = (
        "**✅ All thresholds passed — proceed to Gate 3.**"
        if all_passed else
        "**❌ One or more thresholds failed — revisit candidate pool before Gate 3.**"
    )
    lines += ["", overall, ""]

    # Oracle-confirmed interactions section
    oracle_pairs = [
        (name, partner, itype, note)
        for name, sc in sorted_cards
        for partner, itype, note, conf in sc["interactions"]
        if conf == "oracle"
    ]
    if oracle_pairs:
        lines += [
            "---",
            "",
            "## Oracle-Confirmed Interactions",
            "",
            "> These interactions were verified against actual card text — highest confidence.",
            "",
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
            "---",
            "",
            "## Redundant Pairs",
            "",
            "| Card A | Card B | Shared Role | CMC Brackets | Justification for Both |",
            "|--------|--------|-------------|:------------:|------------------------|",
        ]
        for a, b, roles in redundant_pairs[:20]:
            role_str = ", ".join(roles) if roles else "same role"
            cmc_a = scores[a]["profile"]["cmc"]
            cmc_b = scores[b]["profile"]["cmc"]
            lines.append(f"| {a} | {b} | {role_str} | {cmc_a}/{cmc_b} | *(fill in)* |")
        lines.append("")

    # Synergy chains scaffold — anchor on cards with oracle interactions
    lines += [
        "---",
        "",
        "## Synergy Chains",
        "",
        "> Map 2-3 chains using hub cards as anchors. Prefer oracle-confirmed interactions.",
        "> Format: [Card A] → [what A produces] → [Card B] → [outcome]",
        "",
    ]
    # Prefer oracle-heavy, high-synergy cards as anchors
    chain_anchors = [
        (name, sc) for name, sc in sorted_cards
        if sc["synergy_count"] >= 3
    ][:3]

    if chain_anchors:
        for i, (hub_name, hub_sc) in enumerate(chain_anchors, 1):
            # Prefer oracle-confirmed partners for the chain
            oracle_partners = [p for p, it, n, c in hub_sc["interactions"] if c == "oracle"]
            tag_partners = list(hub_sc["synergy_partners"])
            partner_list = (oracle_partners + [p for p in tag_partners if p not in oracle_partners])[:2]
            chain = " → ".join(f"[{c}]" for c in [hub_name] + partner_list)
            oracle_label = " ⭐oracle" if oracle_partners else ""
            lines += [
                f"**Chain {i} — [{hub_name} engine]{oracle_label}:**",
                chain + " → [outcome]",
                "Redundancy: *(fill in — which pieces have substitutes?)*",
                "Minimum pieces to function: N of M",
                "",
            ]
    else:
        lines += [
            "**Chain 1:**",
            "[Card A] → [output] → [Card B] → [outcome]",
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
        f"- [{'x' if any('T1' in m and 'PASS' in m for m in threshold_msgs) else ' '}] Avg Synergy Density ≥ {dt['min_avg_density']:.0%}",
        f"- [{'x' if len(isolated) <= max_isolated else ' '}] ≤ {max_isolated} isolated cards",
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
        description="Gate 2.5 synergy analysis — directional, oracle-verified pairwise scoring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("input_file", help="session.md, decklist.txt, pools/ dir, or names list")
    p.add_argument("--format", choices=["auto", "session", "decklist", "names", "pools"],
                   default="auto", help="Input format (default: auto-detect)")
    p.add_argument("--output", help="Write report to this file (default: stdout)")
    p.add_argument("--min-synergy", type=float, default=3.0,
                   help="(legacy) Minimum average synergy count — superseded by --mode thresholds")
    p.add_argument("--mode", choices=["auto", "pool", "deck"], default="auto",
                   help="Threshold calibration: pool (large candidate pool, loose) or "
                        "deck (final 60-card, strict). Default: auto-detect from size.")
    args = p.parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found.", file=sys.stderr)
        sys.exit(2)

    content = input_path.read_text(encoding="utf-8") if input_path.is_file() else ""

    # Auto-detect format
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

    if fmt == "session":
        names = extract_names_from_session(content)
    elif fmt == "decklist":
        names = extract_names_from_decklist(input_path)
    elif fmt == "pools":
        names = extract_names_from_pools(input_path)
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
        print(
            f"  {len(not_found)} card(s) not found in DB (will score as 0 tags): "
            f"{', '.join(not_found[:5])}",
            file=sys.stderr,
        )

    for name in not_found:
        card_data[name.lower()] = {"name": name}

    print(f"Scoring pairwise synergies (4-pass: tag → oracle → redundant → dependency)...", file=sys.stderr)
    scores = score_pairwise(card_data)
    all_passed, threshold_msgs = check_thresholds(scores, args.min_synergy, args.mode)

    report = build_report(
        scores, threshold_msgs, all_passed,
        str(input_path), not_found, args.mode,
    )

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
