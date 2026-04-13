#!/usr/bin/env python3
"""
Deck Scaffold Generator — GUI (customtkinter)

Usage:  python scripts/scaffold_gui.py
Requires:  pip install customtkinter
"""

import csv
import difflib
import io
import json
import os
import platform
import re
import subprocess
import sys
import threading
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import filedialog

try:
    import customtkinter as ctk
except ImportError:
    print("customtkinter is not installed. Run:  pip install customtkinter")
    sys.exit(1)

_scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_scripts_dir))
from generate_deck_scaffold import (
    ALL_CREATURE_TYPES,
    ARCHETYPE_QUERIES,
    sanitize_folder_name,
)
from mtg_utils import RepoPaths

# ─────────────────────────────────────────────────────────────────────────────
# Palette
# ─────────────────────────────────────────────────────────────────────────────
APP_TITLE = "MTG Deck Scaffold Generator"
WIN_W, WIN_H = 860, 940

ACCENT       = "#c9a227"
ACCENT_HOVER = "#a8871e"
BG           = "#0c0c0c"
CARD_BG      = "#141414"
CARD_BORDER  = "#1e1e1e"
SURFACE      = "#1a1a1a"
SURFACE_ALT  = "#222222"
BORDER       = "#333333"
TEXT         = "#e8e8e8"
TEXT_DIM     = "#999999"
TEXT_MUTED   = "#666666"
SUCCESS      = "#4ade80"
ERROR        = "#f87171"
WARNING      = "#fb923c"
INFO_BLUE    = "#60a5fa"

COLOR_ORDER = "WUBRG"

MANA_COLORS = {
    "W": {"bg": "#f9f4e0", "fg": "#1a1a1a", "dim": "#48443a", "label": "W"},
    "U": {"bg": "#1177cc", "fg": "#ffffff", "dim": "#1e3550", "label": "U"},
    "B": {"bg": "#5c3d6e", "fg": "#e0d4ee", "dim": "#2a1e32", "label": "B"},
    "R": {"bg": "#d42e2e", "fg": "#ffffff", "dim": "#501f1f", "label": "R"},
    "G": {"bg": "#1f944a", "fg": "#ffffff", "dim": "#1e3828", "label": "G"},
}
MANA_NAMES = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}

ARCHETYPE_GROUPS = {
    "Aggro":            ["aggro", "burn", "prowess", "infect"],
    "Tempo / Midrange": ["midrange", "tempo", "blink", "lifegain", "tribal"],
    "Control / Prison": ["control", "stax", "superfriends"],
    "Combo":            ["combo", "storm", "extra_turns"],
    "Graveyard":        ["graveyard", "reanimation", "flashback", "madness",
                         "self_mill", "opp_mill"],
    "Permanents":       ["tokens", "aristocrats", "enchantress", "equipment",
                         "artifacts", "vehicles", "voltron"],
    "Ramp / Big Mana":  ["ramp", "landfall", "lands", "domain", "eldrazi",
                         "energy", "proliferate"],
}
_LBL = {"opp_mill": "Opp Mill", "self_mill": "Self Mill"}
ARCH_LABEL = {k: _LBL.get(k, k.replace("_", " ").title())
              for g in ARCHETYPE_GROUPS.values() for k in g}

ALL_TAGS = [
    "lifegain", "removal", "draw", "counter", "ramp", "haste",
    "flying", "trample", "mill", "wipe", "pump", "bounce",
    "etb", "tutor", "flash", "tribal", "protection", "deathtouch",
]

SCAFFOLD_FILES = ["session.md", "candidate_pool.csv", "decklist.txt",
                  "analysis.md", "sideboard_guide.md"]

SCORE_SORT_KEYS = [
    "weighted_score", "engine_score", "synergy_density",
    "engine_density", "role_breadth", "synergy_score",
    "oracle_interactions",
]

GRID_COLS = 5
INNER_PAD = 16

_KARSTEN = {
    (1, 1): 14, (1, 2): 13, (1, 3): 12, (1, 4): 11, (1, 5): 11,
    (2, 2): 18, (2, 3): 16, (2, 4): 15, (2, 5): 14,
    (3, 3): 22, (3, 4): 20, (3, 5): 18,
}

BASIC_FOR_COLOR = {"W": "Plains", "U": "Island", "B": "Swamp",
                   "R": "Mountain", "G": "Forest"}
SUBTYPE_COLOR = {"Plains": "W", "Island": "U", "Swamp": "B",
                 "Mountain": "R", "Forest": "G"}

SETTINGS_EXT = ".scaffold.json"


# ─────────────────────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class RunResult:
    success: bool
    output: str
    synergy_output: str | None = None
    source: str = "scaffold"
    deck_dir: str | None = None
    files_found: list[str] = field(default_factory=list)
    auto_build_msg: str | None = None
    focus_log: list[tuple[str, str]] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Pure helpers
# ─────────────────────────────────────────────────────────────────────────────
def normalize_colors(raw: str) -> str:
    seen = dict.fromkeys(c for c in raw.upper() if c in COLOR_ORDER)
    return "".join(c for c in COLOR_ORDER if c in seen)


def filter_tribes(query: str) -> list[str]:
    q = query.strip().lower()
    return [t for t in ALL_CREATURE_TYPES if q in t.lower()] if q else []


def _safe_float(val) -> float:
    try:
        return float(str(val).strip().rstrip("%"))
    except (ValueError, TypeError):
        return -1.0


def _sort_key(row: dict) -> tuple:
    return tuple(-_safe_float(row.get(c, "0")) for c in SCORE_SORT_KEYS)


def _extract_deck_dir(output: str) -> str | None:
    for line in output.splitlines():
        if "Output:" in line:
            return line.split("Output:")[-1].strip().rstrip("/\\").strip()
    return None


def _verify_files(deck_dir: str) -> list[str]:
    d = Path(deck_dir)
    found = [f for f in SCAFFOLD_FILES if (d / f).exists()]
    for extra in ["synergy_report.md", "top_200.csv"]:
        if (d / extra).exists() and extra not in found:
            found.append(extra)
    return found


def _open_folder(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    if platform.system() == "Windows":
        os.startfile(str(p))
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", str(p)])
    else:
        subprocess.Popen(["xdg-open", str(p)])


def _is_land_card(row: dict) -> bool:
    front = row.get("type_line", "").split("//")[0].strip()
    main_part = front.split("\u2014")[0].strip()
    return "Land" in main_part.split()


def _card_type_group(row: dict) -> str:
    front = row.get("type_line", "").split("//")[0].lower()
    if "creature" in front:      return "Creatures"
    if "planeswalker" in front:  return "Planeswalkers"
    if "instant" in front:       return "Instants"
    if "sorcery" in front:       return "Sorceries"
    if "enchantment" in front:   return "Enchantments"
    if "artifact" in front:      return "Artifacts"
    return "Other Spells"


# ─────────────────────────────────────────────────────────────────────────────
# Fuzzy name resolution
# ─────────────────────────────────────────────────────────────────────────────
def _resolve_card_name(query, by_name):
    key = query.lower().strip()
    if key in by_name:
        return by_name[key], by_name[key].get("name", query).strip(), "exact"
    all_keys = list(by_name.keys())
    close = difflib.get_close_matches(key, all_keys, n=1, cutoff=0.72)
    if close:
        row = by_name[close[0]]
        return row, row.get("name", close[0]).strip(), "fuzzy:" + row.get("name", "")
    if len(key) >= 5:
        for pk, row in by_name.items():
            pn = row.get("name", "").strip()
            if key in pk or pk in key:
                return row, pn, "substr:" + pn
    return None, query, "not_found"


# ─────────────────────────────────────────────────────────────────────────────
# Land color detection (NO oracle parsing - only produced_mana + subtypes)
# ─────────────────────────────────────────────────────────────────────────────
def _detect_land_colors(row: dict) -> set[str]:
    """Which WUBRG colors can this land RELIABLY produce?

    ONLY trusts two sources:
      1. Scryfall 'produced_mana' field (if present in CSV)
      2. Land subtypes in type_line (Plains=W, Island=U, etc.)

    NO oracle text parsing.  Oracle text is too unreliable:
    activation costs, conditional abilities, and flavour text
    all cause false positives that let colorless garbage through.

    Returns empty set for colorless-only lands.
    """
    colors: set[str] = set()

    # 1) Scryfall produced_mana field (authoritative)
    pm = str(row.get("produced_mana", "") or "").upper()
    if pm:
        for c in "WUBRG":
            if c in pm:
                colors.add(c)
        # Field exists but only C -> colorless only
        if not colors:
            return set()
        return colors

    # 2) Land subtypes only (always reliable)
    #    "Land - Plains Swamp" -> {W, B}
    #    "Land - Locus"        -> {} (colorless)
    tl = row.get("type_line", "")
    if "\u2014" in tl:
        subtypes = tl.split("\u2014", 1)[1]
    elif " - " in tl:
        subtypes = tl.split(" - ", 1)[1]
    else:
        subtypes = ""

    for subtype, color in SUBTYPE_COLOR.items():
        if re.search(r"\b" + re.escape(subtype) + r"\b", subtypes):
            colors.add(color)

    # 3) Nothing provable -> assume colorless -> REJECT
    return colors


def _count_pips(mana_cost: str) -> dict[str, int]:
    pips = {c: 0 for c in "WUBRG"}
    for m in re.findall(r"\{([WUBRG])\}", mana_cost, re.IGNORECASE):
        pips[m.upper()] += 1
    return pips


def _karsten_required(pips: int, turn: int) -> int:
    pips = min(pips, 3)
    turn = max(1, min(turn, 5))
    return _KARSTEN.get((pips, turn), 11)


# ─────────────────────────────────────────────────────────────────────────────
# CSV sorting + merging
# ─────────────────────────────────────────────────────────────────────────────
def sort_and_rewrite_csv(filepath: Path) -> tuple[bool, int]:
    if not filepath.exists():
        return False, 0
    text = filepath.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return False, 0
    if not any(c in reader.fieldnames for c in SCORE_SORT_KEYS):
        return False, 0
    rows = list(reader)
    if not rows:
        return False, 0
    rows.sort(key=_sort_key)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=reader.fieldnames,
                       extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    filepath.write_text(buf.getvalue(), encoding="utf-8")
    return True, len(rows)


def merge_scores_into_candidate_pool(deck_dir: str) -> tuple[bool, int]:
    pool_path = Path(deck_dir) / "candidate_pool.csv"
    top_path  = Path(deck_dir) / "top_200.csv"
    if not pool_path.exists() or not top_path.exists():
        return False, 0
    scores: dict[str, dict] = {}
    top_text = top_path.read_text(encoding="utf-8")
    tr = csv.DictReader(io.StringIO(top_text))
    tf = list(tr.fieldnames or [])
    sc = [c for c in SCORE_SORT_KEYS if c in tf]
    if not sc:
        return False, 0
    for row in tr:
        n = row.get("name", "").strip()
        if n:
            scores[n] = {c: row.get(c, "") for c in sc}
    pt = pool_path.read_text(encoding="utf-8")
    pr = csv.DictReader(io.StringIO(pt))
    pf = list(pr.fieldnames or [])
    pool_rows = list(pr)
    if not pool_rows:
        return False, 0
    nc = [c for c in sc if c not in pf]
    mf = pf + nc
    for row in pool_rows:
        n = row.get("name", "").strip()
        cs = scores.get(n, {})
        for c in sc:
            v = cs.get(c, "")
            if c in nc:
                row[c] = v
            elif c in pf and not row.get(c):
                row[c] = v
    pool_rows.sort(key=_sort_key)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=mf, extrasaction="ignore",
                       lineterminator="\n")
    w.writeheader()
    w.writerows(pool_rows)
    pool_path.write_text(buf.getvalue(), encoding="utf-8")
    return True, len(pool_rows)


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-BUILD DECKLIST
# ─────────────────────────────────────────────────────────────────────────────
def auto_build_decklist(
    deck_dir: str,
    colors: str,
    focus_cards: list[str] | None = None,
) -> tuple[bool, str, list[tuple[str, str]]]:
    """Build a playable 60+15 from scored candidate_pool.csv.

    Strict mana base:
      - Colorless-only lands NEVER included
      - Only trusts produced_mana + land subtypes
      - No oracle text parsing
      - Max half land slots = nonbasic
      - All remaining = basics by Karsten gap
    """
    focus_log: list[tuple[str, str]] = []
    pool_path = Path(deck_dir) / "candidate_pool.csv"

    if not pool_path.exists():
        return False, "candidate_pool.csv not found", focus_log

    with open(pool_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return False, "Empty CSV", focus_log
        has_scores = any(c in reader.fieldnames for c in SCORE_SORT_KEYS)
        rows = list(reader)

    if len(rows) < 10:
        return False, "Only %d candidates" % len(rows), focus_log
    if not has_scores:
        return False, "No synergy scores yet", focus_log

    by_name: dict[str, dict] = {}
    for r in rows:
        n = r.get("name", "").strip()
        if n:
            by_name[n.lower()] = r

    pool_lands = [r for r in rows if _is_land_card(r)]
    nonlands   = [r for r in rows if not _is_land_card(r)]

    if not nonlands:
        return False, "No nonland cards", focus_log

    # Adaptive land count
    sample = nonlands[:min(30, len(nonlands))]
    avg_cmc = (sum(_safe_float(r.get("cmc", "0")) for r in sample)
               / max(1, len(sample)))
    n_lands    = 22 if avg_cmc < 2.3 else 26 if avg_cmc > 3.5 else 24
    n_nonlands = 60 - n_lands

    def _copies_for(r):
        cmc = _safe_float(r.get("cmc", "0"))
        leg = "Legendary" in r.get("type_line", "")
        if cmc >= 6:        return 1
        if cmc >= 5 or leg: return 2
        if cmc >= 4:        return 3
        return 4

    def _copy_reason(r, copies):
        cmc = _safe_float(r.get("cmc", "0"))
        if "Legendary" in r.get("type_line", "") and copies <= 2:
            return "Legendary"
        if cmc >= 5:
            return "CMC %d" % int(cmc)
        return ""

    # ══════════════════════════════════════════════════════════════════
    # PHASE 1: Lock focus cards
    # ══════════════════════════════════════════════════════════════════
    mainboard: list[tuple[int, str, dict]] = []
    used: set[str] = set()
    slots = 0
    focus_land_names: list[str] = []

    if focus_cards:
        focus_log.append(("Focus Card Resolution:", ACCENT))
        for fc in focus_cards:
            fc_clean = fc.strip()
            if not fc_clean:
                continue
            row, resolved, status = _resolve_card_name(fc_clean, by_name)
            if row is None:
                focus_log.append(
                    ("  \u2717 %s -- NOT FOUND" % fc_clean, ERROR))
                continue
            if resolved.lower() in used:
                focus_log.append(
                    ("  \u2713 %s -- duplicate" % fc_clean, TEXT_DIM))
                continue
            if _is_land_card(row):
                focus_land_names.append(resolved)
                mt = status.split(":")[0] if ":" in status else status
                if status == "exact":
                    focus_log.append(
                        ("  \u2713 %s -- locked as land" % resolved, SUCCESS))
                else:
                    focus_log.append(
                        ("  \u2713 \"%s\" -> %s (%s) -- locked as land"
                         % (fc_clean, resolved, mt), WARNING))
                continue
            copies = min(_copies_for(row), n_nonlands - slots)
            if copies <= 0:
                focus_log.append(
                    ("  \u26a0 %s -- no slots" % resolved, WARNING))
                continue
            mainboard.append((copies, resolved, row))
            used.add(resolved.lower())
            slots += copies
            reason = _copy_reason(row, copies)
            rs = " (%s)" % reason if reason else ""
            mt = status.split(":")[0] if ":" in status else status
            if status == "exact":
                focus_log.append(
                    ("  \u2713 %s -> %dx%s" % (resolved, copies, rs), SUCCESS))
            else:
                focus_log.append(
                    ("  \u2713 \"%s\" -> %s (%s) -> %dx%s"
                     % (fc_clean, resolved, mt, copies, rs), WARNING))
        focus_log.append(("", TEXT))

    # ══════════════════════════════════════════════════════════════════
    # PHASE 2: Fill nonlands by score
    # ══════════════════════════════════════════════════════════════════
    for r in nonlands:
        if slots >= n_nonlands:
            break
        name = r.get("name", "").strip()
        if not name or name.lower() in used:
            continue
        copies = min(_copies_for(r), n_nonlands - slots)
        if copies <= 0:
            break
        mainboard.append((copies, name, r))
        used.add(name.lower())
        slots += copies

    # ══════════════════════════════════════════════════════════════════
    # PHASE 3: Colour analysis
    # ══════════════════════════════════════════════════════════════════
    total_pips: dict[str, int] = {c: 0 for c in "WUBRG"}
    hardest: dict[str, tuple[int, int]] = {}

    for copies, _, r in mainboard:
        mc = r.get("mana_cost", "")
        cmc = max(1, int(_safe_float(r.get("cmc", "1"))))
        pips = _count_pips(mc)
        for c in "WUBRG":
            if pips[c] > 0:
                total_pips[c] += pips[c] * copies
                prev = hardest.get(c, (0, 99))
                if pips[c] > prev[0] or (pips[c] == prev[0]
                                          and cmc < prev[1]):
                    hardest[c] = (pips[c], cmc)

    active_colors = [c for c in "WUBRG"
                     if c in colors.upper() and total_pips.get(c, 0) > 0]
    if not active_colors:
        active_colors = [c for c in "WUBRG" if c in colors.upper()]
    if not active_colors:
        active_colors = ["W"]
    active_set = set(active_colors)

    min_sources: dict[str, int] = {}
    for c in active_colors:
        if c in hardest:
            p, t = hardest[c]
            min_sources[c] = _karsten_required(p, t)
        else:
            min_sources[c] = 10

    # ══════════════════════════════════════════════════════════════════
    # PHASE 4: Mana base (ultra-strict, zero colorless)
    #
    #   1. Nonbasic MUST produce active color (produced_mana or subtype)
    #   2. If we can't prove it -> rejected
    #   3. Max half land slots = nonbasic, rest = basics
    #   4. Prefer duals covering 2+ active colors
    #   5. NO utility lands, NO colorless, NO conditional sources
    # ══════════════════════════════════════════════════════════════════
    csrc: dict[str, int] = {c: 0 for c in "WUBRG"}
    land_picks: list[tuple[int, str, set[str]]] = []
    land_used: set[str] = set()
    land_slots = 0

    # Pre-filter: STRICT
    on_color: list[tuple[dict, set[str]]] = []
    rejected: list[str] = []

    for r in pool_lands:
        name = r.get("name", "").strip()
        tl = r.get("type_line", "")
        if not name or "Basic" in tl:
            continue
        produced = _detect_land_colors(r)
        relevant = produced & active_set

        if not relevant:
            rejected.append(name)
            continue

        # Double check: if produced_mana exists and is colorless-only,
        # reject even if subtypes matched (corrupted data guard)
        pm = str(r.get("produced_mana", "") or "").upper()
        if pm and not any(c in pm for c in "WUBRG"):
            rejected.append(name)
            continue

        on_color.append((r, relevant))

    if rejected:
        sample = rejected[:6]
        focus_log.append(
            ("  Rejected %d colorless/off-color lands: %s%s"
             % (len(rejected), ", ".join(sample),
                "..." if len(rejected) > 6 else ""),
             TEXT_DIM))

    # 4a) Focus lands (on-color only)
    for fname in focus_land_names:
        if land_slots >= n_lands:
            break
        row = by_name.get(fname.lower())
        if not row or fname.lower() in land_used:
            continue
        produced = _detect_land_colors(row)
        relevant = produced & active_set
        if not relevant:
            focus_log.append(
                ("  \u26a0 %s REJECTED (can't prove it makes %s mana)"
                 % (fname, "/".join(active_colors)), ERROR))
            continue
        copies = min(4, n_lands - land_slots)
        if copies <= 0:
            break
        land_picks.append((copies, fname, relevant))
        land_used.add(fname.lower())
        land_slots += copies
        for c in relevant:
            csrc[c] += copies

    # 4b) Score on-color nonbasics by Karsten gap
    def _lp(info):
        r, rel = info
        s = 0.0
        for c in rel:
            gap = max(0, min_sources.get(c, 0) - csrc.get(c, 0))
            if gap > 0:
                s += gap * (min_sources.get(c, 10) / 8.0)
        if len(rel) >= 2:
            s += len(rel) * 5.0
        s += _safe_float(r.get("weighted_score", "0")) * 0.001
        return s

    on_color.sort(key=_lp, reverse=True)

    # 4c) Pick nonbasics - max HALF of land slots
    max_nb = n_lands // 2

    for r, relevant in on_color:
        if land_slots >= max_nb:
            break
        name = r.get("name", "").strip()
        if not name or name.lower() in land_used:
            continue
        has_gap = any(csrc.get(c, 0) < min_sources.get(c, 0)
                      for c in relevant)
        if not has_gap and len(relevant) < 2:
            continue
        copies = min(4, max_nb - land_slots)
        if copies <= 0:
            break

        # Final paranoia check
        produced = _detect_land_colors(r)
        if not (produced & active_set):
            continue

        land_picks.append((copies, name, relevant))
        land_used.add(name.lower())
        land_slots += copies
        for c in relevant:
            csrc[c] += copies

    # NO "fill remaining with whatever". Every unfilled slot = basic.

    # 4d) ALL remaining = basics by Karsten gap then pip ratio
    remaining = n_lands - land_slots
    basic_alloc: list[tuple[int, str]] = []

    if remaining > 0:
        gaps = {c: max(0, min_sources.get(c, 0) - csrc.get(c, 0))
                for c in active_colors}
        total_gap = sum(gaps.values())

        if total_gap == 0:
            # All Karsten met - distribute by pip ratio
            total_p = max(1, sum(total_pips.get(c, 0)
                                 for c in active_colors))
            allocated = 0
            for i, c in enumerate(active_colors):
                if i == len(active_colors) - 1:
                    n = remaining - allocated
                else:
                    n = max(1, round(remaining * total_pips.get(c, 1)
                                     / total_p))
                n = max(0, min(n, remaining - allocated))
                if n > 0:
                    basic_alloc.append((n, BASIC_FOR_COLOR[c]))
                    csrc[c] += n
                    allocated += n
            if allocated < remaining and basic_alloc:
                on, oname = basic_alloc[0]
                basic_alloc[0] = (on + remaining - allocated, oname)
        else:
            # Distribute basics to close gaps first
            allocated = 0
            gc = [c for c in active_colors if gaps.get(c, 0) > 0]
            for i, c in enumerate(gc):
                if i == len(gc) - 1:
                    n = remaining - allocated
                else:
                    n = max(1, round(remaining * gaps[c]
                                     / max(1, total_gap)))
                n = max(1, min(n, remaining - allocated))
                if n > 0:
                    basic_alloc.append((n, BASIC_FOR_COLOR[c]))
                    csrc[c] += n
                    allocated += n
            # Leftover -> highest-pip color
            if allocated < remaining:
                left = remaining - allocated
                best = max(active_colors,
                           key=lambda c: total_pips.get(c, 0))
                found = False
                for idx, (bn, bname) in enumerate(basic_alloc):
                    if bname == BASIC_FOR_COLOR[best]:
                        basic_alloc[idx] = (bn + left, bname)
                        found = True
                        break
                if not found:
                    basic_alloc.append((left, BASIC_FOR_COLOR[best]))
                csrc[best] += left

    # ══════════════════════════════════════════════════════════════════
    # PHASE 5: Sideboard
    # ══════════════════════════════════════════════════════════════════
    sideboard: list[tuple[int, str]] = []
    sb_slots = 0
    for r in nonlands:
        if sb_slots >= 15:
            break
        name = r.get("name", "").strip()
        if not name or name.lower() in used:
            continue
        copies = min(3, 15 - sb_slots)
        sideboard.append((copies, name))
        used.add(name.lower())
        sb_slots += copies

    # ══════════════════════════════════════════════════════════════════
    # PHASE 6: Write output
    # ══════════════════════════════════════════════════════════════════
    type_groups: dict[str, list[tuple[int, str]]] = {}
    for copies, name, r in mainboard:
        grp = _card_type_group(r)
        type_groups.setdefault(grp, []).append((copies, name))

    TYPE_ORDER = ["Creatures", "Instants", "Sorceries", "Enchantments",
                  "Artifacts", "Planeswalkers", "Other Spells"]

    nb_ct = sum(c for c, _, _ in land_picks)
    ba_ct = sum(c for c, _ in basic_alloc)
    main_total = slots + nb_ct + ba_ct
    top3 = ", ".join(n for _, n, _ in mainboard[:3])

    fp = sum(1 for m, cl in focus_log
             if cl in (SUCCESS, WARNING)
             and ("\u2192" in m or "locked" in m))
    ff = sum(1 for m, cl in focus_log if cl == ERROR)

    lines = [
        "// Auto-generated decklist (%d main + %d sb)" % (main_total, sb_slots),
        "// Top synergy: %s" % top3,
        "// Avg CMC %.1f -> %d lands (%d nonbasic + %d basic)"
        % (avg_cmc, n_lands, nb_ct, ba_ct),
    ]
    if focus_cards:
        lines.append("// Focus: %d locked, %d not found" % (fp, ff))
        for m, cl in focus_log:
            if m.startswith("  "):
                lines.append("// %s" % m.strip())
    lines.append("//")
    lines.append("// Mana base (Karsten):")
    all_ok = True
    for c in active_colors:
        need = min_sources.get(c, 0)
        have = csrc.get(c, 0)
        ok = have >= need
        if not ok:
            all_ok = False
        tag = "OK" if ok else "SHORT %d" % (need - have)
        lines.append("//   %s (%s): %d/%d  [%s]"
                      % (MANA_NAMES.get(c, c), c, have, need, tag))
    if all_ok:
        lines.append("//   ALL COLORS OK")
    lines.extend(["// Review before tournament use", "", "Deck"])

    for grp in TYPE_ORDER:
        cards = type_groups.get(grp, [])
        if cards:
            lines.append("// %s" % grp)
            for copies, name in cards:
                lines.append("%d %s" % (copies, name))
            lines.append("")

    lines.append("// Lands")
    for copies, name, _ in land_picks:
        lines.append("%d %s" % (copies, name))
    for copies, name in basic_alloc:
        lines.append("%d %s" % (copies, name))
    lines.append("")
    lines.append("Sideboard")
    for copies, name in sideboard:
        lines.append("%d %s" % (copies, name))
    lines.append("")

    (Path(deck_dir) / "decklist.txt").write_text(
        "\n".join(lines), encoding="utf-8")

    shorts = []
    for c in active_colors:
        if csrc.get(c, 0) < min_sources.get(c, 0):
            shorts.append("%s (%d/%d)" % (
                MANA_NAMES.get(c, c), csrc[c], min_sources[c]))
    fn = ""
    if focus_cards:
        fn = " | Focus: %d locked" % fp
        if ff:
            fn += ", %d MISSING" % ff
    mn = (" | Mana: Karsten OK" if not shorts
          else " | MANA WARN: %s" % ", ".join(shorts))

    summary = ("%d main + %d sb | CMC %.1f | %d lands (%dnb+%db)%s%s"
               % (main_total, sb_slots, avg_cmc, n_lands, nb_ct, ba_ct,
                  fn, mn))
    return True, summary, focus_log


# ─────────────────────────────────────────────────────────────────────────────
# Fonts
# ─────────────────────────────────────────────────────────────────────────────
_F_BODY = _F_SMALL = _F_BOLD = _F_MONO = None
_F_TITLE = _F_SECTION = _F_HINT = None


def _init_fonts():
    global _F_BODY, _F_SMALL, _F_BOLD, _F_MONO, _F_TITLE, _F_SECTION, _F_HINT
    _F_BODY    = ctk.CTkFont(size=13)
    _F_SMALL   = ctk.CTkFont(size=11)
    _F_BOLD    = ctk.CTkFont(size=13, weight="bold")
    _F_MONO    = ctk.CTkFont(family="Courier New", size=11)
    _F_TITLE   = ctk.CTkFont(size=17, weight="bold")
    _F_SECTION = ctk.CTkFont(size=14, weight="bold")
    _F_HINT    = ctk.CTkFont(size=11)


# ─────────────────────────────────────────────────────────────────────────────
# Widget factories
# ─────────────────────────────────────────────────────────────────────────────
def w_entry(parent, placeholder="", **kw):
    d = dict(fg_color=SURFACE, border_color=BORDER, text_color=TEXT,
             placeholder_text_color=TEXT_MUTED, font=_F_BODY,
             height=38, corner_radius=8)
    d.update(kw)
    return ctk.CTkEntry(parent, placeholder_text=placeholder, **d)


def w_button(parent, text, command=None, *, primary=False, **kw):
    if primary:
        d = dict(fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=BG,
                 font=_F_BOLD, height=40, corner_radius=8)
    else:
        d = dict(fg_color=SURFACE_ALT, hover_color=BORDER, text_color=TEXT_DIM,
                 font=ctk.CTkFont(size=12), height=36, corner_radius=8)
    d.update(kw)
    return ctk.CTkButton(parent, text=text, command=command, **d)


def w_check(parent, text, variable, **kw):
    d = dict(font=ctk.CTkFont(size=12), text_color=TEXT_DIM,
             fg_color=ACCENT, hover_color=ACCENT_HOVER,
             border_color=BORDER, checkmark_color="#FFFFFF")
    d.update(kw)
    return ctk.CTkCheckBox(parent, text=text, variable=variable, **d)


def w_label(parent, text, *, muted=False, hint=False, bold=False, **kw):
    if bold:    font, color = _F_BOLD, TEXT
    elif hint:  font, color = _F_HINT, TEXT_MUTED
    elif muted: font, color = _F_SMALL, TEXT_DIM
    else:       font, color = _F_BODY, TEXT
    d = dict(font=font, text_color=color)
    d.update(kw)
    return ctk.CTkLabel(parent, text=text, **d)


# ─────────────────────────────────────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────────────────────────────────────
class ScaffoldApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        _init_fonts()
        self.title(APP_TITLE)
        self.geometry("%dx%d" % (WIN_W, WIN_H))
        self.minsize(760, 700)
        self.configure(fg_color=BG)
        self._repo = RepoPaths()
        self.selected_colors: set[str]     = set()
        self.selected_archetypes: set[str] = set()
        self._selected_tags: set[str]      = set()
        self._tribes: list[str]            = []
        self.wildcard_var     = ctk.BooleanVar(value=False)
        self.skip_queries_var = ctk.BooleanVar(value=False)
        self.run_synergy_var  = ctk.BooleanVar(value=True)
        self.auto_build_var   = ctk.BooleanVar(value=True)
        self.tribe_var        = ctk.StringVar()
        self._active_proc = None
        self._active_btn = None
        self._active_btn_text = ""
        self._running = False
        self._was_cancelled = False
        self._last_deck_dir = None
        self._tribe_search_job = None
        self._build_ui()

    # ═══════════════════════════════════════════════════════════════════════
    # EXPORT / IMPORT
    # ═══════════════════════════════════════════════════════════════════════
    def _export_settings(self) -> dict:
        return {
            "deck_name": self.name_entry.get().strip(),
            "colors": sorted(self.selected_colors),
            "archetypes": sorted(self.selected_archetypes),
            "tribes": list(self._tribes),
            "tags": sorted(self._selected_tags),
            "focus_cards": [l.strip() for l in
                            self.focus_box.get("1.0", "end").strip()
                            .splitlines() if l.strip()],
            "output_dir": self.output_entry.get().strip(),
            "options": {
                "skip_queries": self.skip_queries_var.get(),
                "run_synergy": self.run_synergy_var.get(),
                "auto_build": self.auto_build_var.get(),
                "wildcard": self.wildcard_var.get(),
            },
        }

    def _import_settings(self, data: dict) -> None:
        self._reset_form()
        name = data.get("deck_name", "")
        if name:
            self.name_entry.insert(0, name)
        for c in data.get("colors", []):
            if c in COLOR_ORDER and c not in self.selected_colors:
                self._toggle_color(c)
        for a in data.get("archetypes", []):
            if a in self._arch_btns and a not in self.selected_archetypes:
                self._toggle_arch(a)
        for t in data.get("tribes", []):
            if t not in self._tribes:
                self._tribes.append(t)
        self._refresh_tribe_chips()
        for t in data.get("tags", []):
            if t in self._tag_btns and t not in self._selected_tags:
                self._toggle_tag(t)
        fc = data.get("focus_cards", [])
        if fc:
            self.focus_box.insert("1.0", "\n".join(fc))
        od = data.get("output_dir", "")
        if od:
            self.output_entry.insert(0, od)
        opts = data.get("options", {})
        self.skip_queries_var.set(opts.get("skip_queries", False))
        self.run_synergy_var.set(opts.get("run_synergy", True))
        self.auto_build_var.set(opts.get("auto_build", True))
        self.wildcard_var.set(opts.get("wildcard", False))
        self._validate_live()

    def _on_save_settings(self):
        data = self._export_settings()
        dn = data.get("deck_name", "scaffold") or "scaffold"
        dn = re.sub(r"[^\w\-]", "_", dn)
        f = filedialog.asksaveasfilename(
            title="Save scaffold settings",
            defaultextension=SETTINGS_EXT,
            initialfile="%s%s" % (dn, SETTINGS_EXT),
            filetypes=[("Scaffold Settings", "*" + SETTINGS_EXT),
                       ("JSON", "*.json"), ("All", "*.*")])
        if not f:
            return
        try:
            Path(f).write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8")
            self._sm("Settings saved: %s" % Path(f).name, SUCCESS)
        except Exception as e:
            self._sm("Save failed: %s" % e, ERROR)

    def _on_load_settings(self):
        f = filedialog.askopenfilename(
            title="Load scaffold settings",
            filetypes=[("Scaffold Settings", "*" + SETTINGS_EXT),
                       ("JSON", "*.json"), ("All", "*.*")])
        if not f:
            return
        try:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
            self._import_settings(data)
            self._sm("Loaded: %s" % Path(f).name, SUCCESS)
        except Exception as e:
            self._sm("Load failed: %s" % e, ERROR)

    # ═══════════════════════════════════════════════════════════════════════
    # LAYOUT
    # ═══════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="\u2726  " + APP_TITLE, font=_F_TITLE,
                     text_color=ACCENT).pack(side="left", padx=24, pady=14)
        w_button(hdr, "\u2193 Load", self._on_load_settings,
                 width=70, height=30).pack(side="right", padx=(4, 20), pady=13)
        w_button(hdr, "\u2191 Save", self._on_save_settings,
                 width=70, height=30).pack(side="right", padx=0, pady=13)
        self.tabs = ctk.CTkTabview(
            self, fg_color=BG,
            segmented_button_fg_color=SURFACE,
            segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_color=SURFACE,
            segmented_button_unselected_hover_color=SURFACE_ALT,
            text_color=TEXT, text_color_disabled=TEXT_MUTED)
        self.tabs.pack(fill="both", expand=True)
        self.tabs.add("New Scaffold")
        self.tabs.add("Run Queries")
        self.tabs.add("Synergy Analysis")
        self._build_scaffold_tab()
        self._build_queries_tab()
        self._build_synergy_tab()
        self._build_log_panel()
        self._build_footer()

    def _card(self, parent):
        c = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=14,
                          border_color=CARD_BORDER, border_width=1)
        c.pack(fill="x", padx=10, pady=(0, 10))
        return c

    def _card_header(self, card, number, title, hint=""):
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=INNER_PAD, pady=(14, 2 if hint else 10))
        ctk.CTkLabel(row, text=number,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=BG, fg_color=ACCENT,
                     corner_radius=13, width=26, height=26
                     ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(row, text=title, font=_F_SECTION,
                     text_color=TEXT).pack(side="left")
        if hint:
            w_label(card, hint, hint=True).pack(
                anchor="w", padx=INNER_PAD, pady=(0, 8))

    def _build_scaffold_tab(self):
        tab = self.tabs.tab("New Scaffold")
        self.scroll = ctk.CTkScrollableFrame(
            tab, fg_color=BG, scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT)
        self.scroll.pack(fill="both", expand=True)
        c1 = self._card(self.scroll)
        self._card_header(c1, "1", "Deck Name")
        self.name_entry = w_entry(c1, "e.g. Orzhov Lifegain")
        self.name_entry.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        self.name_entry.bind("<KeyRelease>", lambda _: self._validate_live())
        c2 = self._card(self.scroll)
        self._card_header(c2, "2", "Mana Colours", "Select colour identity")
        self._build_colors(c2)
        c3 = self._card(self.scroll)
        self._card_header(c3, "3", "Archetype", "Select one or more")
        self._build_archetypes(c3)
        c4 = self._card(self.scroll)
        self._card_header(c4, "4", "Creature Subtype", "Required for Tribal")
        self._build_tribe(c4)
        c5 = self._card(self.scroll)
        self._card_header(c5, "5", "Extra Tags", "Optional search keywords")
        self._build_tags(c5)
        c6 = self._card(self.scroll)
        self._card_header(c6, "6", "Focus Cards",
                          "One per line. LOCKED into mainboard. Fuzzy-matched.")
        self.focus_box = ctk.CTkTextbox(
            c6, fg_color=SURFACE, border_color=BORDER, text_color=TEXT,
            font=ctk.CTkFont(family="Courier New", size=12),
            border_width=1, corner_radius=8, height=80, wrap="word")
        self.focus_box.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        c7 = self._card(self.scroll)
        self._card_header(c7, "7", "Options")
        self._build_options(c7)
        c8 = self._card(self.scroll)
        self._card_header(c8, "8", "Output Directory", "Default: Decks/")
        self._build_output(c8)

    def _build_colors(self, p):
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        self._color_btns = {}
        for c in COLOR_ORDER:
            mc = MANA_COLORS[c]
            btn = ctk.CTkButton(
                f, text="%s\n%s" % (mc["label"], MANA_NAMES[c]),
                width=118, height=62, corner_radius=12,
                fg_color=mc["dim"], hover_color=mc["bg"], text_color=mc["fg"],
                border_color=CARD_BORDER, border_width=2,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda col=c: self._toggle_color(col))
            btn.pack(side="left", padx=(0, 8))
            self._color_btns[c] = btn

    def _toggle_color(self, c):
        btn, mc = self._color_btns[c], MANA_COLORS[c]
        if c in self.selected_colors:
            self.selected_colors.discard(c)
            btn.configure(fg_color=mc["dim"], border_color=CARD_BORDER,
                          border_width=2)
        else:
            self.selected_colors.add(c)
            btn.configure(fg_color=mc["bg"], border_color=ACCENT,
                          border_width=3)
        self._validate_live()

    def _build_archetypes(self, p):
        ct = ctk.CTkFrame(p, fg_color="transparent")
        ct.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        self._arch_btns = {}
        for gn, archs in ARCHETYPE_GROUPS.items():
            h = ctk.CTkFrame(ct, fg_color="transparent")
            h.pack(fill="x", pady=(8, 4))
            ctk.CTkFrame(h, fg_color=ACCENT, width=3, height=14,
                         corner_radius=1).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(h, text=gn, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_DIM).pack(side="left")
            g = ctk.CTkFrame(ct, fg_color="transparent")
            g.pack(fill="x")
            for col in range(GRID_COLS):
                g.columnconfigure(col, weight=1, uniform="a")
            for i, a in enumerate(archs):
                lbl = ARCH_LABEL.get(a, a.replace("_", " ").title())
                btn = ctk.CTkButton(
                    g, text=lbl, height=34, corner_radius=8,
                    fg_color=SURFACE, hover_color=SURFACE_ALT,
                    text_color=TEXT_DIM, border_color=BORDER, border_width=1,
                    font=ctk.CTkFont(size=12),
                    command=lambda x=a: self._toggle_arch(x))
                btn.grid(row=i // GRID_COLS, column=i % GRID_COLS,
                         padx=3, pady=3, sticky="ew")
                self._arch_btns[a] = btn

    def _toggle_arch(self, arch):
        btn = self._arch_btns[arch]
        if arch in self.selected_archetypes:
            self.selected_archetypes.discard(arch)
            btn.configure(fg_color=SURFACE, text_color=TEXT_DIM,
                          border_color=BORDER, border_width=1)
        else:
            self.selected_archetypes.add(arch)
            btn.configure(fg_color=ACCENT, text_color=BG,
                          border_color=ACCENT, border_width=1)
        self._arch_count.configure(
            text="%d selected" % len(self.selected_archetypes))
        tribal = "tribal" in self.selected_archetypes
        for w in self._tribe_widgets:
            w.configure(state="normal" if tribal else "disabled")
        if not tribal:
            self._tribes.clear()
            self._refresh_tribe_chips()
            for w in self._tribe_results.winfo_children():
                w.destroy()
        self._validate_live()

    def _build_tribe(self, p):
        se = w_entry(p, "Type to search...", state="disabled")
        se.configure(textvariable=self.tribe_var)
        se.pack(fill="x", padx=INNER_PAD, pady=(0, 4))
        self.tribe_var.trace_add("write", self._tribe_debounce)
        self._tribe_results = ctk.CTkFrame(p, fg_color=SURFACE, corner_radius=8)
        self._tribe_results.pack(fill="x", padx=INNER_PAD)
        self._tribe_chips = ctk.CTkFrame(p, fg_color="transparent")
        self._tribe_chips.pack(fill="x", padx=INNER_PAD, pady=(4, 14))
        self._tribe_widgets = [se]

    def _tribe_debounce(self, *_):
        if self._tribe_search_job:
            self.after_cancel(self._tribe_search_job)
        self._tribe_search_job = self.after(200, self._tribe_search)

    def _tribe_search(self):
        self._tribe_search_job = None
        for w in self._tribe_results.winfo_children():
            w.destroy()
        q = self.tribe_var.get().strip()
        if not q:
            return
        matches = filter_tribes(q)
        if not matches:
            w_label(self._tribe_results, "No match for '%s'" % q,
                    hint=True).pack(anchor="w", padx=8, pady=4)
            return
        for t in matches[:10]:
            already = t in self._tribes
            ctk.CTkButton(
                self._tribe_results,
                text=("\u2713 " + t) if already else t,
                fg_color=ACCENT if already else "transparent",
                hover_color=SURFACE_ALT,
                text_color=BG if already else TEXT_DIM,
                font=ctk.CTkFont(size=12), anchor="w",
                height=28, corner_radius=6,
                command=lambda n=t: self._tribe_toggle(n)
            ).pack(fill="x", padx=4, pady=1)
        if len(matches) > 10:
            w_label(self._tribe_results, "+%d more" % (len(matches) - 10),
                    hint=True).pack(anchor="w", padx=8, pady=(2, 4))

    def _tribe_toggle(self, name):
        if name in self._tribes:
            self._tribes.remove(name)
        else:
            self._tribes.append(name)
        self._refresh_tribe_chips()
        self._tribe_search()
        self._validate_live()

    def _refresh_tribe_chips(self):
        for w in self._tribe_chips.winfo_children():
            w.destroy()
        for t in self._tribes:
            chip = ctk.CTkFrame(self._tribe_chips, fg_color=SURFACE_ALT,
                                corner_radius=14)
            chip.pack(side="left", padx=(0, 6), pady=2)
            ctk.CTkLabel(chip, text=t, font=ctk.CTkFont(size=12),
                         text_color=TEXT).pack(side="left", padx=(10, 2), pady=4)
            ctk.CTkButton(
                chip, text="\u00d7", width=24, height=24,
                fg_color="transparent", hover_color=BORDER,
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=12,
                command=lambda n=t: self._tribe_toggle(n)
            ).pack(side="left", padx=(0, 4))

    def _build_tags(self, p):
        self._tag_btns = {}
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        for col in range(6):
            f.columnconfigure(col, weight=1, uniform="tag")
        for i, tag in enumerate(ALL_TAGS):
            btn = ctk.CTkButton(
                f, text=tag, height=30, corner_radius=15,
                fg_color=SURFACE, hover_color=SURFACE_ALT,
                text_color=TEXT_MUTED, border_color=BORDER, border_width=1,
                font=ctk.CTkFont(size=11),
                command=lambda t=tag: self._toggle_tag(t))
            btn.grid(row=i // 6, column=i % 6, padx=3, pady=3, sticky="ew")
            self._tag_btns[tag] = btn

    def _toggle_tag(self, tag):
        btn = self._tag_btns[tag]
        if tag in self._selected_tags:
            self._selected_tags.discard(tag)
            btn.configure(fg_color=SURFACE, text_color=TEXT_MUTED,
                          border_color=BORDER)
        else:
            self._selected_tags.add(tag)
            btn.configure(fg_color=ACCENT, text_color=BG, border_color=ACCENT)

    def _build_options(self, p):
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        for v, t, kw in [
            (self.skip_queries_var, "Skip queries (offline template)", {}),
            (self.run_synergy_var, "Run synergy analysis after scaffold", {}),
            (self.auto_build_var, "Auto-build decklist (Karsten mana base)", {}),
            (self.wildcard_var, "Wildcard (tribe as hint only)",
             {"fg_color": WARNING}),
        ]:
            w_check(f, t, v, **kw).pack(anchor="w", pady=3)

    def _build_output(self, p):
        r = ctk.CTkFrame(p, fg_color="transparent")
        r.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        self.output_entry = w_entry(r, "Decks/")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        w_button(r, "Browse", self._browse_output, width=80).pack(side="left")

    def _build_queries_tab(self):
        tab = self.tabs.tab("Run Queries")
        f = ctk.CTkScrollableFrame(tab, fg_color=BG,
                                   scrollbar_button_color=BORDER)
        f.pack(fill="both", expand=True)
        card = ctk.CTkFrame(f, fg_color=CARD_BG, corner_radius=14,
                            border_color=CARD_BORDER, border_width=1)
        card.pack(fill="x", padx=10, pady=10)
        w_label(card, "Run Pending Session Queries", bold=True,
                text_color=ACCENT).pack(anchor="w", padx=INNER_PAD, pady=(14, 2))
        w_label(card, "Finds placeholders, runs them, fills results.",
                hint=True, wraplength=700, justify="left"
                ).pack(anchor="w", padx=INNER_PAD, pady=(0, 12))
        r = ctk.CTkFrame(card, fg_color="transparent")
        r.pack(fill="x", padx=INNER_PAD, pady=(0, 8))
        self.rq_entry = w_entry(r, "Path to session.md")
        self.rq_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        w_button(r, "Browse", self._browse_session, width=80).pack(side="left")
        self.rq_force = ctk.BooleanVar(value=False)
        self.rq_dryrun = ctk.BooleanVar(value=False)
        o = ctk.CTkFrame(card, fg_color="transparent")
        o.pack(anchor="w", padx=INNER_PAD, pady=(0, 12))
        w_check(o, "Force re-run", self.rq_force).pack(anchor="w", pady=2)
        w_check(o, "Dry run", self.rq_dryrun).pack(anchor="w", pady=2)
        self.rq_btn = w_button(card, "Run Queries", self._on_run_queries,
                               primary=True, width=160)
        self.rq_btn.pack(anchor="w", padx=INNER_PAD, pady=(0, 14))

    def _build_synergy_tab(self):
        tab = self.tabs.tab("Synergy Analysis")
        f = ctk.CTkScrollableFrame(tab, fg_color=BG,
                                   scrollbar_button_color=BORDER)
        f.pack(fill="both", expand=True)
        card = ctk.CTkFrame(f, fg_color=CARD_BG, corner_radius=14,
                            border_color=CARD_BORDER, border_width=1)
        card.pack(fill="x", padx=10, pady=10)
        w_label(card, "Gate 2.5 -- Synergy Analysis", bold=True,
                text_color=ACCENT).pack(anchor="w", padx=INNER_PAD, pady=(14, 2))
        w_label(card, "Scores interactions, checks thresholds.",
                hint=True, wraplength=700, justify="left"
                ).pack(anchor="w", padx=INNER_PAD, pady=(0, 12))
        r1 = ctk.CTkFrame(card, fg_color="transparent")
        r1.pack(fill="x", padx=INNER_PAD, pady=(0, 8))
        self.syn_in = w_entry(r1, "session.md or decklist.txt")
        self.syn_in.pack(side="left", fill="x", expand=True, padx=(0, 8))
        w_button(r1, "Browse", self._browse_syn_in, width=80).pack(side="left")
        r2 = ctk.CTkFrame(card, fg_color="transparent")
        r2.pack(fill="x", padx=INNER_PAD, pady=(0, 8))
        self.syn_out = w_entry(r2, "Output report (optional)")
        self.syn_out.pack(side="left", fill="x", expand=True, padx=(0, 8))
        w_button(r2, "Browse", self._browse_syn_out, width=80).pack(side="left")
        sr = ctk.CTkFrame(card, fg_color="transparent")
        sr.pack(anchor="w", padx=INNER_PAD, pady=(0, 12))
        w_label(sr, "Threshold:").pack(side="left", padx=(0, 4))
        self.syn_thresh = ctk.CTkEntry(
            sr, width=60, fg_color=SURFACE, border_color=BORDER,
            text_color=TEXT, font=_F_BODY, height=32, corner_radius=6)
        self.syn_thresh.insert(0, "3.0")
        self.syn_thresh.pack(side="left", padx=(0, 16))
        w_label(sr, "Mode:").pack(side="left", padx=(0, 4))
        self._syn_mode = ctk.StringVar(value="auto")
        ctk.CTkOptionMenu(
            sr, values=["auto", "pool", "deck"],
            variable=self._syn_mode, width=100, height=32,
            fg_color=SURFACE, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=SURFACE, dropdown_hover_color=SURFACE_ALT,
            text_color=TEXT, dropdown_text_color=TEXT,
            font=ctk.CTkFont(size=12), corner_radius=6).pack(side="left")
        self.syn_btn = w_button(card, "Analyze Synergy", self._on_synergy,
                                primary=True, width=180)
        self.syn_btn.pack(anchor="w", padx=INNER_PAD, pady=(0, 14))

    def _build_log_panel(self):
        self._log_visible = False
        self._log_tags = set()
        bar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=34)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self._log_toggle = ctk.CTkButton(
            bar, text="\u25b6  Log",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED, fg_color="transparent",
            hover_color=BORDER, anchor="w", height=34, corner_radius=0,
            command=self._toggle_log)
        self._log_toggle.pack(side="left", fill="y", padx=8)
        self._log_inline = w_label(bar, "", hint=True)
        self._log_inline.pack(side="left", padx=4)
        self._log_frame = ctk.CTkFrame(
            self, fg_color=SURFACE, corner_radius=0, height=0)
        self._log_frame.pack(fill="x")
        self._log_frame.pack_propagate(False)
        self._log_box = ctk.CTkTextbox(
            self._log_frame, fg_color=SURFACE, text_color=TEXT,
            font=_F_MONO, border_width=0, corner_radius=0,
            wrap="word", state="disabled")
        self._log_box.pack(fill="both", expand=True)

    def _toggle_log(self):
        self._log_visible = not self._log_visible
        self._log_frame.configure(height=220 if self._log_visible else 0)
        self._log_toggle.configure(
            text=("\u25bc  Log" if self._log_visible else "\u25b6  Log"))

    def _log_tag_for(self, color):
        tag = "c_%s" % color.replace("#", "")
        if tag not in self._log_tags:
            try:
                self._log_box._textbox.tag_configure(tag, foreground=color)
            except Exception:
                pass
            self._log_tags.add(tag)
        return tag

    def _log(self, text, color=TEXT):
        tag = self._log_tag_for(color)
        line = text if text.endswith("\n") else text + "\n"
        self._log_box.configure(state="normal")
        s = self._log_box.index("end-1c")
        self._log_box.insert("end", line)
        e = self._log_box.index("end-1c")
        try:
            self._log_box._textbox.tag_add(tag, s, e)
        except Exception:
            pass
        self._log_box.see("end")
        self._log_box.configure(state="disabled")
        if not self._log_visible:
            self._toggle_log()
        self._log_inline.configure(text=text.strip()[:90], text_color=color)

    def _log_clear(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")
        self._log_inline.configure(text="")

    def _build_footer(self):
        ctk.CTkFrame(self, height=1, fg_color=BORDER,
                      corner_radius=0).pack(fill="x")
        ft = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=72)
        ft.pack(fill="x", side="bottom")
        ft.pack_propagate(False)
        left = ctk.CTkFrame(ft, fg_color="transparent")
        left.pack(side="left", padx=20, fill="y")
        self._arch_count = ctk.CTkLabel(
            left, text="0 selected",
            font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self._arch_count.pack(anchor="w", pady=(10, 0))
        self.status = ctk.CTkLabel(
            left, text="\u2460 Enter a deck name.",
            font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
            wraplength=400, justify="left")
        self.status.pack(anchor="w", pady=(2, 0))
        right = ctk.CTkFrame(ft, fg_color="transparent")
        right.pack(side="right", padx=20, fill="y")
        self.run_btn = ctk.CTkButton(
            right, text="Generate Scaffold",
            width=200, height=44, corner_radius=10,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_generate)
        self.run_btn.pack(side="right", pady=14)
        self._open_btn = w_button(
            right, "\U0001f4c2 Open", self._open_folder_btn,
            width=90, state="disabled")
        self._open_btn.pack(side="right", padx=(0, 8), pady=14)
        w_button(right, "Reset", self._reset_form, width=60,
                 fg_color="transparent", text_color=TEXT_MUTED
                 ).pack(side="right", padx=(0, 8), pady=14)

    # ═══════════════════════════════════════════════════════════════════════
    # STATE
    # ═══════════════════════════════════════════════════════════════════════
    def _validate_live(self):
        if not self.name_entry.get().strip():
            self._sm("\u2460 Enter a deck name.", TEXT_MUTED)
            return False
        if not self.selected_colors:
            self._sm("\u2461 Select colours.", TEXT_MUTED)
            return False
        if not self.selected_archetypes:
            self._sm("\u2462 Pick archetypes.", TEXT_MUTED)
            return False
        if "tribal" in self.selected_archetypes and not self._tribes:
            self._sm("\u2463 Tribal -- pick subtype.", WARNING)
            return False
        self._sm("Ready!", SUCCESS)
        return True

    def _sm(self, msg, color=TEXT_MUTED):
        self.status.configure(text=msg, text_color=color)

    def _reset_form(self):
        self.name_entry.delete(0, "end")
        for c in list(self.selected_colors):
            self._toggle_color(c)
        for a in list(self.selected_archetypes):
            self._toggle_arch(a)
        for t in list(self._selected_tags):
            self._toggle_tag(t)
        self._tribes.clear()
        self._refresh_tribe_chips()
        for w in self._tribe_results.winfo_children():
            w.destroy()
        self.focus_box.delete("1.0", "end")
        self.output_entry.delete(0, "end")
        self.skip_queries_var.set(False)
        self.run_synergy_var.set(True)
        self.auto_build_var.set(True)
        self.wildcard_var.set(False)
        self._last_deck_dir = None
        self._open_btn.configure(state="disabled")
        self._validate_live()

    def _open_folder_btn(self):
        if self._last_deck_dir:
            _open_folder(self._last_deck_dir)

    # ═══════════════════════════════════════════════════════════════════════
    # BROWSE
    # ═══════════════════════════════════════════════════════════════════════
    def _browse_output(self):
        d = filedialog.askdirectory(title="Output directory")
        if d:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, d)

    def _browse_session(self):
        f = filedialog.askopenfilename(
            title="session.md",
            filetypes=[("Markdown", "*.md"), ("All", "*.*")])
        if f:
            self.rq_entry.delete(0, "end")
            self.rq_entry.insert(0, f)

    def _browse_syn_in(self):
        f = filedialog.askopenfilename(
            title="Input",
            filetypes=[("MD/TXT", "*.md *.txt"), ("All", "*.*")])
        if f:
            self.syn_in.delete(0, "end")
            self.syn_in.insert(0, f)

    def _browse_syn_out(self):
        f = filedialog.asksaveasfilename(
            title="Save report", defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All", "*.*")])
        if f:
            self.syn_out.delete(0, "end")
            self.syn_out.insert(0, f)

    # ═══════════════════════════════════════════════════════════════════════
    # PROCESS LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════
    def _guard(self, btn):
        if not self._running:
            return False
        if self._active_btn is btn:
            self._cancel()
            return True
        self._sm("Already running.", WARNING)
        return True

    def _start(self, btn, label):
        self._running = True
        self._was_cancelled = False
        self._active_btn = btn
        self._active_btn_text = label
        btn.configure(state="normal", text="Cancel \u2715",
                      fg_color=ERROR, hover_color="#dc2626")
        self._sm("Running...", ACCENT)
        self._log_clear()

    def _finish(self):
        if not self._running:
            return
        if self._active_btn:
            self._active_btn.configure(
                state="normal", text=self._active_btn_text,
                fg_color=ACCENT, hover_color=ACCENT_HOVER)
        self._active_proc = None
        self._running = False

    def _cancel(self):
        self._was_cancelled = True
        if self._active_proc and self._active_proc.poll() is None:
            self._active_proc.terminate()
            try:
                self._active_proc.wait(timeout=5)
            except Exception:
                self._active_proc.kill()
        self._finish()
        self._sm("Cancelled.", WARNING)
        self._log("Cancelled.", WARNING)

    def _env(self):
        e = os.environ.copy()
        e["PYTHONIOENCODING"] = "utf-8"
        return e

    # ═══════════════════════════════════════════════════════════════════════
    # COMMANDS
    # ═══════════════════════════════════════════════════════════════════════
    def _on_generate(self):
        if self._guard(self.run_btn):
            return
        if not self._validate_live():
            return
        name = self.name_entry.get().strip()
        colors = normalize_colors("".join(self.selected_colors))
        cmd = [sys.executable,
               str(_scripts_dir / "generate_deck_scaffold.py"),
               "--name", name, "--colors", colors, "--archetype"]
        cmd.extend(sorted(self.selected_archetypes))
        if self.wildcard_var.get():
            cmd.append("--wildcard")
        if self._tribes:
            cmd.append("--tribe")
            cmd.extend(self._tribes)
        if self._selected_tags:
            cmd.extend(["--extra-tags",
                        ",".join(sorted(self._selected_tags))])
        od = self.output_entry.get().strip()
        if od:
            cmd.extend(["--output-dir", od])
        ft = self.focus_box.get("1.0", "end").strip()
        fn = [l.strip() for l in ft.splitlines() if l.strip()]
        if fn:
            cmd.append("--focus-cards")
            cmd.extend(fn)
        if self.skip_queries_var.get():
            cmd.append("--skip-queries")
        rs = self.run_synergy_var.get()
        ab = self.auto_build_var.get()
        self._start(self.run_btn, "Generate Scaffold")
        threading.Thread(
            target=self._bg_scaffold,
            args=(cmd, colors, rs, ab, fn),
            daemon=True).start()

    def _on_run_queries(self):
        if self._guard(self.rq_btn):
            return
        p = self.rq_entry.get().strip()
        if not p:
            self._sm("Select session.md.", ERROR)
            return
        cmd = [sys.executable,
               str(_scripts_dir / "run_session_queries.py"), p]
        if self.rq_force.get():
            cmd.append("--force")
        if self.rq_dryrun.get():
            cmd.append("--dry-run")
        self._start(self.rq_btn, "Run Queries")
        threading.Thread(
            target=self._bg_generic, args=(cmd, "queries"),
            daemon=True).start()

    def _on_synergy(self):
        if self._guard(self.syn_btn):
            return
        inp = self.syn_in.get().strip()
        if not inp:
            self._sm("Select input.", ERROR)
            return
        cmd = [sys.executable,
               str(_scripts_dir / "synergy_analysis.py"), inp]
        t = self.syn_thresh.get().strip()
        if t and t != "3.0":
            cmd.extend(["--min-synergy", t])
        m = self._syn_mode.get()
        if m and m != "auto":
            cmd.extend(["--mode", m])
        o = self.syn_out.get().strip()
        if o:
            cmd.extend(["--output", o])
        self._start(self.syn_btn, "Analyze Synergy")
        threading.Thread(
            target=self._bg_generic, args=(cmd, "synergy"),
            daemon=True).start()

    # ═══════════════════════════════════════════════════════════════════════
    # BACKGROUND THREADS (crash-protected)
    # ═══════════════════════════════════════════════════════════════════════
    def _stream(self, cmd):
        self.after(0, self._log, "$ " + " ".join(cmd), TEXT_MUTED)
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, text=True,
            encoding="utf-8", errors="replace",
            cwd=str(self._repo.root), env=self._env())
        self._active_proc = proc
        lines = []
        for line in proc.stdout:
            lines.append(line)
            s = line.rstrip()
            if s.strip():
                c = (SUCCESS if "[OK]" in s else
                     ERROR if "ERROR" in s else
                     ACCENT if "candidates" in s.lower() else TEXT)
                self.after(0, self._log, s, c)
        proc.wait()
        return proc.returncode == 0, "".join(lines).strip()

    def _bg_generic(self, cmd, source):
        try:
            ok, out = self._stream(cmd)
        except Exception as e:
            ok, out = False, str(e)
        self.after(0, self._done, RunResult(ok, out, source=source))

    def _bg_scaffold(self, cmd, colors, run_syn, auto_build, focus_names):
        """Scaffold thread - triple try/except so GUI NEVER gets stuck."""
        try:
            ok, out = self._stream(cmd)
        except Exception as e:
            ok, out = False, str(e)

        deck_dir = None
        syn = None
        ab_msg = None
        focus_log = []

        try:
            deck_dir = _extract_deck_dir(out) if ok else None
            if deck_dir:
                dp = Path(deck_dir)
                if not dp.is_absolute():
                    dp = self._repo.root / dp
                deck_dir = str(dp)

            if ok and run_syn and deck_dir:
                try:
                    syn = self._bg_synergy(deck_dir)
                except Exception as e:
                    self.after(0, self._log,
                               "Synergy crashed: %s" % e, ERROR)
                    self.after(0, self._log, traceback.format_exc(), ERROR)

            if ok and deck_dir:
                try:
                    self._bg_sort(deck_dir)
                except Exception as e:
                    self.after(0, self._log,
                               "Sort crashed: %s" % e, ERROR)

            if ok and auto_build and deck_dir:
                try:
                    ab_ok, ab_msg, focus_log = auto_build_decklist(
                        deck_dir, colors, focus_names)
                    if ab_ok:
                        self.after(0, self._log, "", TEXT)
                        self.after(0, self._log,
                                   "--- Auto-built Decklist " + "-" * 28,
                                   SUCCESS)
                        for m, cl in focus_log:
                            if m:
                                self.after(0, self._log, m, cl)
                        self.after(0, self._log, "  %s" % ab_msg, SUCCESS)
                    else:
                        self.after(0, self._log,
                                   "  Auto-build skipped: %s" % ab_msg,
                                   TEXT_DIM)
                        ab_msg = None
                except Exception as e:
                    self.after(0, self._log,
                               "AUTO-BUILD CRASHED: %s" % e, ERROR)
                    self.after(0, self._log, traceback.format_exc(), ERROR)
                    ab_msg = None

        except Exception as e:
            self.after(0, self._log,
                       "Post-scaffold error: %s" % e, ERROR)
            self.after(0, self._log, traceback.format_exc(), ERROR)

        files = _verify_files(deck_dir) if deck_dir else []
        # THIS ALWAYS RUNS - GUI always unlocks
        self.after(0, self._done,
                   RunResult(ok, out, syn, "scaffold", deck_dir, files,
                             ab_msg, focus_log))

    def _bg_synergy(self, deck_dir):
        session = Path(deck_dir) / "session.md"
        if not session.exists():
            return None
        self.after(0, self._log, "\nRunning synergy analysis...", ACCENT)
        report = Path(deck_dir) / "synergy_report.md"
        cmd = [sys.executable,
               str(_scripts_dir / "synergy_analysis.py"),
               str(session), "--output", str(report), "--top", "200"]
        try:
            subprocess.run(
                cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL,
                cwd=str(self._repo.root), env=self._env(), timeout=120)
            if report.exists():
                return report.read_text(encoding="utf-8").strip()
            return None
        except Exception as e:
            return "Synergy failed: %s" % e

    def _bg_sort(self, deck_dir):
        d = Path(deck_dir)
        ok, n = sort_and_rewrite_csv(d / "top_200.csv")
        if ok:
            self.after(0, self._log,
                       "  Sorted top_200.csv (%d rows)" % n, SUCCESS)
        ok2, pn = merge_scores_into_candidate_pool(deck_dir)
        if ok2:
            self.after(0, self._log,
                       "  Merged scores into candidate_pool.csv (%d cards)"
                       % pn, SUCCESS)

    # ═══════════════════════════════════════════════════════════════════════
    # COMPLETION
    # ═══════════════════════════════════════════════════════════════════════
    def _done(self, r):
        was = self._was_cancelled
        self._was_cancelled = False
        self._finish()
        if was:
            return
        if r.source == "scaffold" and r.success:
            self._show_summary(r)
        if r.synergy_output:
            self._show_synergy(r.synergy_output)
        if r.success:
            if r.source == "scaffold":
                n = len(r.files_found)
                nm = Path(r.deck_dir).name if r.deck_dir else "?"
                msg = "Done -- %d files in %s" % (n, nm)
                if r.auto_build_msg:
                    msg += " | %s" % r.auto_build_msg.split("|")[0].strip()
                self._sm(msg, SUCCESS)
                if r.deck_dir and Path(r.deck_dir).exists():
                    self._last_deck_dir = r.deck_dir
                    self._open_btn.configure(state="normal")
            else:
                self._sm("Done.", SUCCESS)
        else:
            self._sm("Error -- see log.", ERROR)

    def _show_summary(self, r):
        self._log("", TEXT)
        self._log("--- Scaffold Complete " + "-" * 30, SUCCESS)
        if r.deck_dir:
            self._log("  Folder: %s" % r.deck_dir, INFO_BLUE)
        af = SCAFFOLD_FILES + ["synergy_report.md", "top_200.csv"]
        for f in af:
            if f in r.files_found:
                fp = Path(r.deck_dir) / f if r.deck_dir else None
                sz = ""
                if fp and fp.exists():
                    sz = "  (%.1f KB)" % (fp.stat().st_size / 1024)
                self._log("  \u2713 %s%s" % (f, sz), SUCCESS)
            elif f in SCAFFOLD_FILES:
                self._log("  \u2717 %s  (missing)" % f, ERROR)

    def _show_synergy(self, syn):
        self._log("", TEXT)
        self._log("--- Gate 2.5 Synergy " + "-" * 30, ACCENT)
        self._log("  (Deck feedback, not an error)", TEXT_MUTED)
        for line in syn.splitlines():
            c = (ERROR if "[FAIL]" in line else
                 SUCCESS if "[PASS]" in line else
                 INFO_BLUE if "[INFO]" in line else
                 ACCENT if line.startswith(("#", "**")) else TEXT)
            self._log(line, c)


def main():
    ScaffoldApp().mainloop()


if __name__ == "__main__":
    main()
