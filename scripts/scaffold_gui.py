#!/usr/bin/env python3
"""
Deck Scaffold Generator — GUI (customtkinter)

Usage:  python scripts/scaffold_gui.py
Requires:  pip install customtkinter
"""

import csv
import difflib
import io
import os
import platform
import re
import subprocess
import sys
import threading
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

# Karsten mana source requirements (60-card, by on-curve turn)
_KARSTEN = {
    (1, 1): 14, (1, 2): 13, (1, 3): 12, (1, 4): 11, (1, 5): 11,
    (2, 2): 18, (2, 3): 16, (2, 4): 15, (2, 5): 14,
    (3, 3): 22, (3, 4): 20, (3, 5): 18,
}

BASIC_FOR_COLOR = {"W": "Plains", "U": "Island", "B": "Swamp",
                   "R": "Mountain", "G": "Forest"}
SUBTYPE_COLOR   = {"Plains": "W", "Island": "U", "Swamp": "B",
                   "Mountain": "R", "Forest": "G"}


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


def _safe_float(val: str) -> float:
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
    if "creature" in front:
        return "Creatures"
    if "planeswalker" in front:
        return "Planeswalkers"
    if "instant" in front:
        return "Instants"
    if "sorcery" in front:
        return "Sorceries"
    if "enchantment" in front:
        return "Enchantments"
    if "artifact" in front:
        return "Artifacts"
    return "Other Spells"


# ─────────────────────────────────────────────────────────────────────────────
# Fuzzy name resolution
# ─────────────────────────────────────────────────────────────────────────────
def _resolve_card_name(query, by_name):
    key = query.lower().strip()
    if key in by_name:
        actual = by_name[key].get("name", query).strip()
        return by_name[key], actual, "exact"
    all_keys = list(by_name.keys())
    close = difflib.get_close_matches(key, all_keys, n=1, cutoff=0.72)
    if close:
        row = by_name[close[0]]
        actual = row.get("name", close[0]).strip()
        return row, actual, f"fuzzy:{actual}"
    if len(key) >= 5:
        for pool_key, row in by_name.items():
            pool_name = row.get("name", "").strip()
            if key in pool_key or pool_key in key:
                return row, pool_name, f"substr:{pool_name}"
    return None, query, "not_found"


# ─────────────────────────────────────────────────────────────────────────────
# Land color detection
# ─────────────────────────────────────────────────────────────────────────────
_ADD_MANA_RE = re.compile(r"\{([WUBRGC])\}", re.IGNORECASE)


def _detect_land_colors(row: dict) -> set[str]:
    """Which WUBRG colors can this land produce?
    Returns empty set for colorless-only lands."""
    colors: set[str] = set()
    tl = row.get("type_line", "")
    oracle = row.get("oracle_text", "")

    for subtype, color in SUBTYPE_COLOR.items():
        if subtype in tl:
            colors.add(color)

    for match in _ADD_MANA_RE.finditer(oracle):
        sym = match.group(1).upper()
        if sym in "WUBRG":
            colors.add(sym)

    oracle_lower = oracle.lower()
    if any(phrase in oracle_lower for phrase in
           ["any color", "any type", "mana of any", "any one color",
            "any combination of colors"]):
        colors.update("WUBRG")

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
    present = [c for c in SCORE_SORT_KEYS if c in reader.fieldnames]
    if not present:
        return False, 0
    rows = list(reader)
    if not rows:
        return False, 0
    rows.sort(key=_sort_key)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=reader.fieldnames,
                            extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    filepath.write_text(buf.getvalue(), encoding="utf-8")
    return True, len(rows)


def merge_scores_into_candidate_pool(deck_dir: str) -> tuple[bool, int]:
    pool_path = Path(deck_dir) / "candidate_pool.csv"
    top_path  = Path(deck_dir) / "top_200.csv"
    if not pool_path.exists() or not top_path.exists():
        return False, 0
    scores: dict[str, dict] = {}
    top_text = top_path.read_text(encoding="utf-8")
    top_reader = csv.DictReader(io.StringIO(top_text))
    top_fields = list(top_reader.fieldnames or [])
    score_cols = [c for c in SCORE_SORT_KEYS if c in top_fields]
    if not score_cols:
        return False, 0
    for row in top_reader:
        name = row.get("name", "").strip()
        if name:
            scores[name] = {col: row.get(col, "") for col in score_cols}
    pool_text = pool_path.read_text(encoding="utf-8")
    pool_reader = csv.DictReader(io.StringIO(pool_text))
    pool_fields = list(pool_reader.fieldnames or [])
    pool_rows = list(pool_reader)
    if not pool_rows:
        return False, 0
    new_cols = [c for c in score_cols if c not in pool_fields]
    merged_fields = pool_fields + new_cols
    for row in pool_rows:
        name = row.get("name", "").strip()
        card_scores = scores.get(name, {})
        for col in score_cols:
            val = card_scores.get(col, "")
            if col in new_cols:
                row[col] = val
            elif col in pool_fields and not row.get(col):
                row[col] = val
    pool_rows.sort(key=_sort_key)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=merged_fields,
                            extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(pool_rows)
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

    Mana base rules (strict):
      - A nonbasic land is ONLY picked if it produces at least one of
        the deck's active colors.  Zero exceptions.
      - Colorless-only lands are NEVER included.
      - Any land slot not filled by an on-color nonbasic becomes a basic.
      - Basics are distributed to meet Karsten thresholds first, then
        proportional to pip count.

    Returns (success, summary, focus_log).
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
        return False, f"Only {len(rows)} candidates (need 10+)", focus_log
    if not has_scores:
        return False, "No synergy scores (run synergy first)", focus_log

    by_name: dict[str, dict] = {}
    for r in rows:
        n = r.get("name", "").strip()
        if n:
            by_name[n.lower()] = r

    pool_lands = [r for r in rows if _is_land_card(r)]
    nonlands   = [r for r in rows if not _is_land_card(r)]

    if not nonlands:
        return False, "No nonland cards in pool", focus_log

    # ── Adaptive land count ───────────────────────────────────────────
    sample = nonlands[:min(30, len(nonlands))]
    avg_cmc = (sum(_safe_float(r.get("cmc", "0")) for r in sample)
               / max(1, len(sample)))
    n_lands    = 22 if avg_cmc < 2.3 else 26 if avg_cmc > 3.5 else 24
    n_nonlands = 60 - n_lands

    def _copies_for(r):
        cmc = _safe_float(r.get("cmc", "0"))
        is_leg = "Legendary" in r.get("type_line", "")
        if cmc >= 6:     return 1
        if cmc >= 5 or is_leg: return 2
        if cmc >= 4:     return 3
        return 4

    def _copy_reason(r, copies):
        cmc = _safe_float(r.get("cmc", "0"))
        is_leg = "Legendary" in r.get("type_line", "")
        if is_leg and copies <= 2: return "Legendary"
        if cmc >= 5: return f"CMC {cmc:.0f}"
        return ""

    # ══════════════════════════════════════════════════════════════════
    # PHASE 1 — LOCK FOCUS CARDS
    # ══════════════════════════════════════════════════════════════════
    mainboard: list[tuple[int, str, dict]] = []
    used_names: set[str] = set()
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
                    (f"  \u2717 {fc_clean} \u2014 NOT FOUND in pool!",
                     ERROR))
                continue
            if resolved.lower() in used_names:
                focus_log.append(
                    (f"  \u2713 {fc_clean} \u2014 already added", TEXT_DIM))
                continue
            if _is_land_card(row):
                focus_land_names.append(resolved)
                mt = status.split(":")[0] if ":" in status else status
                if status == "exact":
                    focus_log.append(
                        (f"  \u2713 {resolved} \u2014 locked as land",
                         SUCCESS))
                else:
                    focus_log.append(
                        (f"  \u2713 \"{fc_clean}\" \u2192 {resolved} "
                         f"({mt}) \u2014 locked as land", WARNING))
                continue

            copies = min(_copies_for(row), n_nonlands - slots)
            if copies <= 0:
                focus_log.append(
                    (f"  \u26a0 {resolved} \u2014 no slots left", WARNING))
                continue

            mainboard.append((copies, resolved, row))
            used_names.add(resolved.lower())
            slots += copies

            reason = _copy_reason(row, copies)
            rs = f" ({reason})" if reason else ""
            mt = status.split(":")[0] if ":" in status else status
            if status == "exact":
                focus_log.append(
                    (f"  \u2713 {resolved} \u2192 {copies}x{rs}", SUCCESS))
            else:
                focus_log.append(
                    (f"  \u2713 \"{fc_clean}\" \u2192 {resolved} "
                     f"({mt}) \u2192 {copies}x{rs}", WARNING))
        focus_log.append(("", TEXT))

    # ══════════════════════════════════════════════════════════════════
    # PHASE 2 — FILL REMAINING NONLAND SLOTS BY SCORE
    # ══════════════════════════════════════════════════════════════════
    for r in nonlands:
        if slots >= n_nonlands:
            break
        name = r.get("name", "").strip()
        if not name or name.lower() in used_names:
            continue
        copies = min(_copies_for(r), n_nonlands - slots)
        if copies <= 0:
            break
        mainboard.append((copies, name, r))
        used_names.add(name.lower())
        slots += copies

    # ══════════════════════════════════════════════════════════════════
    # PHASE 3 — ANALYSE COLOR REQUIREMENTS
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
    # PHASE 4 — BUILD MANA BASE (strict on-color only)
    # ══════════════════════════════════════════════════════════════════
    color_sources: dict[str, int] = {c: 0 for c in "WUBRG"}
    land_picks: list[tuple[int, str, set[str]]] = []
    land_used: set[str] = set()
    land_slots = 0

    # Pre-compute on-color nonbasic lands ONLY
    # A land must produce at least one active color to be considered.
    on_color_lands: list[tuple[dict, set[str]]] = []
    for r in pool_lands:
        name = r.get("name", "").strip()
        tl = r.get("type_line", "")
        if not name or "Basic" in tl:
            continue
        produced = _detect_land_colors(r)
        # STRICT: must produce at least one of the deck's active colors
        if produced & active_set:
            on_color_lands.append((r, produced))
        # If it produces ZERO active colors → not considered. Period.

    # 4a) Lock focus lands (only if on-color)
    for fname in focus_land_names:
        if land_slots >= n_lands:
            break
        row = by_name.get(fname.lower())
        if not row or fname.lower() in land_used:
            continue
        produced = _detect_land_colors(row)
        if not (produced & active_set):
            # Focus land is colorless — skip it, warn in log
            focus_log.append(
                (f"  \u26a0 {fname} skipped (produces no on-color mana)",
                 WARNING))
            continue
        copies = min(4, n_lands - land_slots)
        if copies <= 0:
            break
        land_picks.append((copies, fname, produced))
        land_used.add(fname.lower())
        land_slots += copies
        for c in produced & active_set:
            color_sources[c] += copies

    # 4b) Score on-color nonbasics by how much they close Karsten gaps
    def _land_priority(info):
        r, produced = info
        score = 0.0
        relevant = produced & active_set
        for c in relevant:
            gap = max(0, min_sources.get(c, 0) - color_sources.get(c, 0))
            if gap > 0:
                score += gap * (min_sources.get(c, 10) / 10.0)
        # Dual+ lands covering multiple needed colors get a bonus
        score += len(relevant) * 3.0
        # Tiebreak by synergy score
        score += _safe_float(r.get("weighted_score", "0")) * 0.01
        return score

    on_color_lands.sort(key=_land_priority, reverse=True)

    # 4c) Pick on-color nonbasics (cap at half of land slots so basics
    #     always have room to meet Karsten)
    max_nonbasic = n_lands // 2  # e.g. 12 of 24 → always 12+ basics

    for r, produced in on_color_lands:
        if land_slots >= max_nonbasic:
            break
        name = r.get("name", "").strip()
        if not name or name.lower() in land_used:
            continue
        # Double-check: must cover at least one active color with a gap
        relevant = produced & active_set
        has_gap = any(
            color_sources.get(c, 0) < min_sources.get(c, 0)
            for c in relevant
        )
        if not has_gap:
            # All colors this land produces are already satisfied.
            # Only include if it covers 2+ active colors (still useful).
            if len(relevant) < 2:
                continue
        copies = min(4, max_nonbasic - land_slots)
        if copies <= 0:
            break
        land_picks.append((copies, name, produced))
        land_used.add(name.lower())
        land_slots += copies
        for c in relevant:
            color_sources[c] += copies

    # NO PHASE 4d. No colorless lands. No "fill remaining with anything".
    # Every unfilled slot becomes a basic. This is intentional.

    # 4e) Fill ALL remaining land slots with basics to meet Karsten
    remaining = n_lands - land_slots
    basic_alloc: list[tuple[int, str]] = []

    if remaining > 0:
        # Calculate gap per color
        gaps: dict[str, int] = {}
        for c in active_colors:
            gaps[c] = max(0, min_sources.get(c, 0)
                          - color_sources.get(c, 0))

        total_gap = sum(gaps.values())

        if total_gap == 0:
            # All Karsten thresholds met — distribute by pip ratio
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
                    color_sources[c] += n
                    allocated += n
            if allocated < remaining and basic_alloc:
                old_n, old_name = basic_alloc[0]
                basic_alloc[0] = (old_n + remaining - allocated, old_name)
        else:
            # Distribute basics to close gaps first
            allocated = 0
            gap_colors = [c for c in active_colors if gaps.get(c, 0) > 0]
            no_gap     = [c for c in active_colors if gaps.get(c, 0) == 0]

            for i, c in enumerate(gap_colors):
                if i == len(gap_colors) - 1 and not no_gap:
                    n = remaining - allocated
                else:
                    n = max(1, round(remaining * gaps[c]
                                     / max(1, total_gap)))
                n = max(1, min(n, remaining - allocated))
                if n > 0:
                    basic_alloc.append((n, BASIC_FOR_COLOR[c]))
                    color_sources[c] += n
                    allocated += n

            # Any leftover → highest-pip color
            if allocated < remaining:
                leftover = remaining - allocated
                best = max(active_colors,
                           key=lambda c: total_pips.get(c, 0))
                found = False
                for idx, (bn, bname) in enumerate(basic_alloc):
                    if bname == BASIC_FOR_COLOR[best]:
                        basic_alloc[idx] = (bn + leftover, bname)
                        found = True
                        break
                if not found:
                    basic_alloc.append((leftover, BASIC_FOR_COLOR[best]))
                color_sources[best] += leftover

    # ══════════════════════════════════════════════════════════════════
    # PHASE 5 — SIDEBOARD
    # ══════════════════════════════════════════════════════════════════
    sideboard: list[tuple[int, str]] = []
    sb_slots = 0
    for r in nonlands:
        if sb_slots >= 15:
            break
        name = r.get("name", "").strip()
        if not name or name.lower() in used_names:
            continue
        copies = min(3, 15 - sb_slots)
        sideboard.append((copies, name))
        used_names.add(name.lower())
        sb_slots += copies

    # ══════════════════════════════════════════════════════════════════
    # PHASE 6 — OUTPUT
    # ══════════════════════════════════════════════════════════════════
    type_groups: dict[str, list[tuple[int, str]]] = {}
    for copies, name, r in mainboard:
        grp = _card_type_group(r)
        type_groups.setdefault(grp, []).append((copies, name))

    TYPE_ORDER = ["Creatures", "Instants", "Sorceries", "Enchantments",
                  "Artifacts", "Planeswalkers", "Other Spells"]

    main_total = slots + sum(c for c, _, _ in land_picks) + \
                 sum(c for c, _ in basic_alloc)
    sb_total = sb_slots
    top3 = ", ".join(n for _, n, _ in mainboard[:3])

    focus_placed = sum(1 for msg, clr in focus_log
                       if clr in (SUCCESS, WARNING)
                       and ("\u2192" in msg or "locked" in msg))
    focus_failed = sum(1 for msg, clr in focus_log if clr == ERROR)

    lines = [
        f"// Auto-generated decklist ({main_total} main + {sb_total} sb)",
        f"// Top picks by synergy:  {top3}",
        f"// Avg CMC {avg_cmc:.1f} -> {n_lands} lands "
        f"({sum(c for c,_,_ in land_picks)} nonbasic + "
        f"{sum(c for c,_ in basic_alloc)} basic)",
    ]

    if focus_cards:
        lines.append(f"// Focus cards: {focus_placed} locked, "
                     f"{focus_failed} not found")
        for msg, clr in focus_log:
            if msg.startswith("  "):
                lines.append(f"// {msg.strip()}")

    lines.append("//")
    lines.append("// Mana base (Karsten validation):")
    all_ok = True
    for c in active_colors:
        needed = min_sources.get(c, 0)
        have   = color_sources.get(c, 0)
        ok = have >= needed
        if not ok:
            all_ok = False
        tag = "OK" if ok else f"SHORT by {needed - have}"
        lines.append(f"//   {MANA_NAMES.get(c, c)} ({c}): "
                     f"{have} sources / {needed} needed  [{tag}]")
    if all_ok:
        lines.append("//   ALL COLORS: Karsten thresholds met")

    lines.extend([
        "// Review with AI analysis before tournament use",
        "",
        "Deck",
    ])

    for grp in TYPE_ORDER:
        cards = type_groups.get(grp, [])
        if cards:
            lines.append(f"// {grp}")
            for copies, name in cards:
                lines.append(f"{copies} {name}")
            lines.append("")

    lines.append("// Lands")
    for copies, name, _ in land_picks:
        lines.append(f"{copies} {name}")
    for copies, name in basic_alloc:
        lines.append(f"{copies} {name}")
    lines.append("")
    lines.append("Sideboard")
    for copies, name in sideboard:
        lines.append(f"{copies} {name}")
    lines.append("")

    out_path = Path(deck_dir) / "decklist.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")

    shortfalls = []
    for c in active_colors:
        needed = min_sources.get(c, 0)
        have   = color_sources.get(c, 0)
        if have < needed:
            shortfalls.append(f"{MANA_NAMES.get(c,c)} ({have}/{needed})")

    focus_note = ""
    if focus_cards:
        focus_note = f" | Focus: {focus_placed} locked"
        if focus_failed:
            focus_note += f", {focus_failed} MISSING"

    mana_note = " | Mana: Karsten OK" if not shortfalls else \
                f" | MANA WARNING: {', '.join(shortfalls)}"

    nonbasic_ct = sum(c for c, _, _ in land_picks)
    basic_ct    = sum(c for c, _ in basic_alloc)
    summary = (f"{main_total}-card main + {sb_total} sb | "
               f"CMC {avg_cmc:.1f} | {n_lands} lands "
               f"({nonbasic_ct} nonbasic + {basic_ct} basic)"
               f"{focus_note}{mana_note}")
    return True, summary, focus_log


# ─────────────────────────────────────────────────────────────────────────────
# Fonts
# ─────────────────────────────────────────────────────────────────────────────
_F_BODY: ctk.CTkFont | None = None
_F_SMALL: ctk.CTkFont | None = None
_F_BOLD: ctk.CTkFont | None = None
_F_MONO: ctk.CTkFont | None = None
_F_TITLE: ctk.CTkFont | None = None
_F_SECTION: ctk.CTkFont | None = None
_F_HINT: ctk.CTkFont | None = None


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
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.minsize(760, 700)
        self.resizable(True, True)
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

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=56)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="\u2726  " + APP_TITLE, font=_F_TITLE,
                     text_color=ACCENT).pack(side="left", padx=24, pady=14)
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
        c.pack(fill="x", padx=10, pady=(0, 10)); return c

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
        self.scroll = ctk.CTkScrollableFrame(tab, fg_color=BG,
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=ACCENT)
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
        self.focus_box = ctk.CTkTextbox(c6, fg_color=SURFACE,
            border_color=BORDER, text_color=TEXT,
            font=ctk.CTkFont(family="Courier New", size=12),
            border_width=1, corner_radius=8, height=80, wrap="word")
        self.focus_box.pack(fill="x", padx=INNER_PAD, pady=(0, 14))

        c7 = self._card(self.scroll)
        self._card_header(c7, "7", "Options")
        self._build_options(c7)

        c8 = self._card(self.scroll)
        self._card_header(c8, "8", "Output Directory", "Default: Decks/")
        self._build_output(c8)

    def _build_colors(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        self._color_btns = {}
        for c in COLOR_ORDER:
            mc = MANA_COLORS[c]
            btn = ctk.CTkButton(frame, text=f"{mc['label']}\n{MANA_NAMES[c]}",
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

    def _build_archetypes(self, parent):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        self._arch_btns = {}
        for gn, archs in ARCHETYPE_GROUPS.items():
            hdr = ctk.CTkFrame(container, fg_color="transparent")
            hdr.pack(fill="x", pady=(8, 4))
            ctk.CTkFrame(hdr, fg_color=ACCENT, width=3, height=14,
                         corner_radius=1).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(hdr, text=gn, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_DIM).pack(side="left")
            grid = ctk.CTkFrame(container, fg_color="transparent")
            grid.pack(fill="x")
            for col in range(GRID_COLS):
                grid.columnconfigure(col, weight=1, uniform="a")
            for i, arch in enumerate(archs):
                lbl = ARCH_LABEL.get(arch, arch.replace("_"," ").title())
                btn = ctk.CTkButton(grid, text=lbl, height=34, corner_radius=8,
                    fg_color=SURFACE, hover_color=SURFACE_ALT, text_color=TEXT_DIM,
                    border_color=BORDER, border_width=1,
                    font=ctk.CTkFont(size=12),
                    command=lambda a=arch: self._toggle_arch(a))
                btn.grid(row=i//GRID_COLS, column=i%GRID_COLS,
                         padx=3, pady=3, sticky="ew")
                self._arch_btns[arch] = btn

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
        n = len(self.selected_archetypes)
        self._arch_count.configure(text=f"{n} selected" if n else "0 selected")
        tribal_on = "tribal" in self.selected_archetypes
        for w in self._tribe_widgets:
            w.configure(state="normal" if tribal_on else "disabled")
        if not tribal_on:
            self._tribes.clear(); self._refresh_tribe_chips()
            for w in self._tribe_results.winfo_children(): w.destroy()
        self._validate_live()

    def _build_tribe(self, parent):
        se = w_entry(parent, "Type to search\u2026", state="disabled")
        se.configure(textvariable=self.tribe_var)
        se.pack(fill="x", padx=INNER_PAD, pady=(0, 4))
        self.tribe_var.trace_add("write", self._tribe_debounce)
        self._tribe_results = ctk.CTkFrame(parent, fg_color=SURFACE,
                                           corner_radius=8)
        self._tribe_results.pack(fill="x", padx=INNER_PAD)
        self._tribe_chips = ctk.CTkFrame(parent, fg_color="transparent")
        self._tribe_chips.pack(fill="x", padx=INNER_PAD, pady=(4, 14))
        self._tribe_widgets = [se]

    def _tribe_debounce(self, *_):
        if self._tribe_search_job:
            self.after_cancel(self._tribe_search_job)
        self._tribe_search_job = self.after(200, self._tribe_do_search)

    def _tribe_do_search(self):
        self._tribe_search_job = None
        for w in self._tribe_results.winfo_children(): w.destroy()
        q = self.tribe_var.get().strip()
        if not q: return
        matches = filter_tribes(q)
        if not matches:
            w_label(self._tribe_results, f"No match for '{q}'",
                    hint=True).pack(anchor="w", padx=8, pady=4); return
        for t in matches[:10]:
            already = t in self._tribes
            ctk.CTkButton(self._tribe_results,
                text=("\u2713 "+t) if already else t,
                fg_color=ACCENT if already else "transparent",
                hover_color=SURFACE_ALT,
                text_color=BG if already else TEXT_DIM,
                font=ctk.CTkFont(size=12), anchor="w",
                height=28, corner_radius=6,
                command=lambda n=t: self._toggle_tribe(n)
            ).pack(fill="x", padx=4, pady=1)
        if len(matches)>10:
            w_label(self._tribe_results, f"+{len(matches)-10} more",
                    hint=True).pack(anchor="w", padx=8, pady=(2,4))

    def _toggle_tribe(self, name):
        if name in self._tribes: self._tribes.remove(name)
        else: self._tribes.append(name)
        self._refresh_tribe_chips(); self._tribe_do_search()
        self._validate_live()

    def _refresh_tribe_chips(self):
        for w in self._tribe_chips.winfo_children(): w.destroy()
        for t in self._tribes:
            chip = ctk.CTkFrame(self._tribe_chips, fg_color=SURFACE_ALT,
                                corner_radius=14)
            chip.pack(side="left", padx=(0,6), pady=2)
            ctk.CTkLabel(chip, text=t, font=ctk.CTkFont(size=12),
                         text_color=TEXT).pack(side="left", padx=(10,2), pady=4)
            ctk.CTkButton(chip, text="\u00d7", width=24, height=24,
                fg_color="transparent", hover_color=BORDER,
                text_color=TEXT_MUTED, font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=12, command=lambda n=t: self._toggle_tribe(n)
            ).pack(side="left", padx=(0,4))

    def _build_tags(self, parent):
        self._tag_btns = {}
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        for col in range(6):
            frame.columnconfigure(col, weight=1, uniform="tag")
        for i, tag in enumerate(ALL_TAGS):
            btn = ctk.CTkButton(frame, text=tag, height=30, corner_radius=15,
                fg_color=SURFACE, hover_color=SURFACE_ALT,
                text_color=TEXT_MUTED, border_color=BORDER, border_width=1,
                font=ctk.CTkFont(size=11),
                command=lambda t=tag: self._toggle_tag(t))
            btn.grid(row=i//6, column=i%6, padx=3, pady=3, sticky="ew")
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

    def _build_options(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        for var, txt, kw in [
            (self.skip_queries_var, "Skip queries (offline template)", {}),
            (self.run_synergy_var, "Run synergy analysis after scaffold", {}),
            (self.auto_build_var, "Auto-build decklist (Karsten mana base)", {}),
            (self.wildcard_var, "Wildcard (tribe as hint only)",
             {"fg_color": WARNING}),
        ]:
            w_check(frame, txt, var, **kw).pack(anchor="w", pady=3)

    def _build_output(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=INNER_PAD, pady=(0, 14))
        self.output_entry = w_entry(row, "Decks/")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0,8))
        w_button(row, "Browse", self._browse_output, width=80).pack(side="left")

    def _build_queries_tab(self):
        tab = self.tabs.tab("Run Queries")
        frame = ctk.CTkScrollableFrame(tab, fg_color=BG,
                                       scrollbar_button_color=BORDER)
        frame.pack(fill="both", expand=True)
        card = ctk.CTkFrame(frame, fg_color=CARD_BG, corner_radius=14,
                            border_color=CARD_BORDER, border_width=1)
        card.pack(fill="x", padx=10, pady=10)
        w_label(card, "Run Pending Session Queries", bold=True,
                text_color=ACCENT).pack(anchor="w", padx=INNER_PAD, pady=(14,2))
        w_label(card, "Finds placeholders in session.md, runs them, "
                "fills results.", hint=True, wraplength=700, justify="left"
                ).pack(anchor="w", padx=INNER_PAD, pady=(0,12))
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=INNER_PAD, pady=(0,8))
        self.rq_entry = w_entry(row, "Path to session.md")
        self.rq_entry.pack(side="left", fill="x", expand=True, padx=(0,8))
        w_button(row, "Browse", self._browse_session, width=80).pack(side="left")
        self.rq_force = ctk.BooleanVar(value=False)
        self.rq_dryrun = ctk.BooleanVar(value=False)
        opts = ctk.CTkFrame(card, fg_color="transparent")
        opts.pack(anchor="w", padx=INNER_PAD, pady=(0,12))
        w_check(opts, "Force re-run", self.rq_force).pack(anchor="w", pady=2)
        w_check(opts, "Dry run", self.rq_dryrun).pack(anchor="w", pady=2)
        self.rq_btn = w_button(card, "Run Queries", self._on_run_queries,
                               primary=True, width=160)
        self.rq_btn.pack(anchor="w", padx=INNER_PAD, pady=(0,14))

    def _build_synergy_tab(self):
        tab = self.tabs.tab("Synergy Analysis")
        frame = ctk.CTkScrollableFrame(tab, fg_color=BG,
                                       scrollbar_button_color=BORDER)
        frame.pack(fill="both", expand=True)
        card = ctk.CTkFrame(frame, fg_color=CARD_BG, corner_radius=14,
                            border_color=CARD_BORDER, border_width=1)
        card.pack(fill="x", padx=10, pady=10)
        w_label(card, "Gate 2.5 \u2014 Synergy Analysis", bold=True,
                text_color=ACCENT).pack(anchor="w", padx=INNER_PAD, pady=(14,2))
        w_label(card, "Scores pairwise interactions, checks thresholds.",
                hint=True, wraplength=700, justify="left"
                ).pack(anchor="w", padx=INNER_PAD, pady=(0,12))
        r1 = ctk.CTkFrame(card, fg_color="transparent")
        r1.pack(fill="x", padx=INNER_PAD, pady=(0,8))
        self.syn_in = w_entry(r1, "session.md or decklist.txt")
        self.syn_in.pack(side="left", fill="x", expand=True, padx=(0,8))
        w_button(r1, "Browse", self._browse_syn_in, width=80).pack(side="left")
        r2 = ctk.CTkFrame(card, fg_color="transparent")
        r2.pack(fill="x", padx=INNER_PAD, pady=(0,8))
        self.syn_out = w_entry(r2, "Output report (optional)")
        self.syn_out.pack(side="left", fill="x", expand=True, padx=(0,8))
        w_button(r2, "Browse", self._browse_syn_out, width=80).pack(side="left")
        srow = ctk.CTkFrame(card, fg_color="transparent")
        srow.pack(anchor="w", padx=INNER_PAD, pady=(0,12))
        w_label(srow, "Threshold:").pack(side="left", padx=(0,4))
        self.syn_thresh = ctk.CTkEntry(srow, width=60, fg_color=SURFACE,
            border_color=BORDER, text_color=TEXT, font=_F_BODY,
            height=32, corner_radius=6)
        self.syn_thresh.insert(0, "3.0")
        self.syn_thresh.pack(side="left", padx=(0,16))
        w_label(srow, "Mode:").pack(side="left", padx=(0,4))
        self._syn_mode = ctk.StringVar(value="auto")
        ctk.CTkOptionMenu(srow, values=["auto","pool","deck"],
            variable=self._syn_mode, width=100, height=32,
            fg_color=SURFACE, button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=SURFACE, dropdown_hover_color=SURFACE_ALT,
            text_color=TEXT, dropdown_text_color=TEXT,
            font=ctk.CTkFont(size=12), corner_radius=6).pack(side="left")
        self.syn_btn = w_button(card, "Analyze Synergy", self._on_synergy,
                                primary=True, width=180)
        self.syn_btn.pack(anchor="w", padx=INNER_PAD, pady=(0,14))

    def _build_log_panel(self):
        self._log_visible = False; self._log_tags = set()
        bar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=34)
        bar.pack(fill="x"); bar.pack_propagate(False)
        self._log_toggle = ctk.CTkButton(bar, text="\u25b6  Log",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_MUTED,
            fg_color="transparent", hover_color=BORDER, anchor="w",
            height=34, corner_radius=0, command=self._toggle_log)
        self._log_toggle.pack(side="left", fill="y", padx=8)
        self._log_inline = w_label(bar, "", hint=True)
        self._log_inline.pack(side="left", padx=4)
        self._log_frame = ctk.CTkFrame(self, fg_color=SURFACE,
                                       corner_radius=0, height=0)
        self._log_frame.pack(fill="x"); self._log_frame.pack_propagate(False)
        self._log_box = ctk.CTkTextbox(self._log_frame, fg_color=SURFACE,
            text_color=TEXT, font=_F_MONO, border_width=0, corner_radius=0,
            wrap="word", state="disabled")
        self._log_box.pack(fill="both", expand=True)

    def _toggle_log(self):
        self._log_visible = not self._log_visible
        self._log_frame.configure(height=220 if self._log_visible else 0)
        self._log_toggle.configure(
            text=("\u25bc  Log" if self._log_visible else "\u25b6  Log"))

    def _log_tag(self, color):
        tag = f"c_{color.replace('#','')}"
        if tag not in self._log_tags:
            try: self._log_box._textbox.tag_configure(tag, foreground=color)
            except: pass
            self._log_tags.add(tag)
        return tag

    def _log(self, text, color=TEXT):
        tag = self._log_tag(color)
        line = text if text.endswith("\n") else text+"\n"
        self._log_box.configure(state="normal")
        start = self._log_box.index("end-1c")
        self._log_box.insert("end", line)
        end = self._log_box.index("end-1c")
        try: self._log_box._textbox.tag_add(tag, start, end)
        except: pass
        self._log_box.see("end"); self._log_box.configure(state="disabled")
        if not self._log_visible: self._toggle_log()
        self._log_inline.configure(text=text.strip()[:90], text_color=color)

    def _log_clear(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0","end")
        self._log_box.configure(state="disabled")
        self._log_inline.configure(text="")

    def _build_footer(self):
        ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")
        footer = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=72)
        footer.pack(fill="x", side="bottom"); footer.pack_propagate(False)
        left = ctk.CTkFrame(footer, fg_color="transparent")
        left.pack(side="left", padx=20, fill="y")
        self._arch_count = ctk.CTkLabel(left, text="0 selected",
            font=ctk.CTkFont(size=12), text_color=TEXT_MUTED)
        self._arch_count.pack(anchor="w", pady=(10,0))
        self.status = ctk.CTkLabel(left,
            text="\u2460 Enter a deck name to get started.",
            font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
            wraplength=400, justify="left")
        self.status.pack(anchor="w", pady=(2,0))
        right = ctk.CTkFrame(footer, fg_color="transparent")
        right.pack(side="right", padx=20, fill="y")
        self.run_btn = ctk.CTkButton(right, text="Generate Scaffold",
            width=200, height=44, corner_radius=10,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_generate)
        self.run_btn.pack(side="right", pady=14)
        self._open_btn = w_button(right, "\U0001f4c2 Open Folder",
            self._open_folder_btn, width=110, state="disabled")
        self._open_btn.pack(side="right", padx=(0,8), pady=14)
        w_button(right, "Reset", self._reset_form, width=70,
                 fg_color="transparent", text_color=TEXT_MUTED
                 ).pack(side="right", padx=(0,8), pady=14)

    # ─── State ────────────────────────────────────────────────────────────
    def _validate_live(self):
        if not self.name_entry.get().strip():
            self._sm("\u2460 Enter a deck name.", TEXT_MUTED); return False
        if not self.selected_colors:
            self._sm("\u2461 Select mana colours.", TEXT_MUTED); return False
        if not self.selected_archetypes:
            self._sm("\u2462 Pick archetypes.", TEXT_MUTED); return False
        if "tribal" in self.selected_archetypes and not self._tribes:
            self._sm("\u2463 Tribal \u2014 pick a subtype.", WARNING); return False
        self._sm("Ready to generate!", SUCCESS); return True

    def _sm(self, msg, color=TEXT_MUTED):
        self.status.configure(text=msg, text_color=color)

    def _reset_form(self):
        self.name_entry.delete(0, "end")
        for c in list(self.selected_colors): self._toggle_color(c)
        for a in list(self.selected_archetypes): self._toggle_arch(a)
        for t in list(self._selected_tags): self._toggle_tag(t)
        self._tribes.clear(); self._refresh_tribe_chips()
        for w in self._tribe_results.winfo_children(): w.destroy()
        self.focus_box.delete("1.0","end"); self.output_entry.delete(0,"end")
        self.skip_queries_var.set(False); self.run_synergy_var.set(True)
        self.auto_build_var.set(True); self.wildcard_var.set(False)
        self._last_deck_dir = None
        self._open_btn.configure(state="disabled"); self._validate_live()

    def _open_folder_btn(self):
        if self._last_deck_dir: _open_folder(self._last_deck_dir)

    # ─── Browse ───────────────────────────────────────────────────────────
    def _browse_output(self):
        d = filedialog.askdirectory(title="Output directory")
        if d: self.output_entry.delete(0,"end"); self.output_entry.insert(0,d)
    def _browse_session(self):
        f = filedialog.askopenfilename(title="session.md",
            filetypes=[("Markdown","*.md"),("All","*.*")])
        if f: self.rq_entry.delete(0,"end"); self.rq_entry.insert(0,f)
    def _browse_syn_in(self):
        f = filedialog.askopenfilename(title="Input file",
            filetypes=[("MD/TXT","*.md *.txt"),("All","*.*")])
        if f: self.syn_in.delete(0,"end"); self.syn_in.insert(0,f)
    def _browse_syn_out(self):
        f = filedialog.asksaveasfilename(title="Save report",
            defaultextension=".md", filetypes=[("Markdown","*.md"),("All","*.*")])
        if f: self.syn_out.delete(0,"end"); self.syn_out.insert(0,f)

    # ─── Process lifecycle ────────────────────────────────────────────────
    def _guard(self, btn):
        if not self._running: return False
        if self._active_btn is btn: self._cancel(); return True
        self._sm("Already running.", WARNING); return True

    def _start(self, btn, label):
        self._running = True; self._was_cancelled = False
        self._active_btn = btn; self._active_btn_text = label
        btn.configure(state="normal", text="Cancel \u2715",
                      fg_color=ERROR, hover_color="#dc2626")
        self._sm("Running\u2026", ACCENT); self._log_clear()

    def _finish(self):
        if not self._running: return
        if self._active_btn:
            self._active_btn.configure(state="normal",
                text=self._active_btn_text,
                fg_color=ACCENT, hover_color=ACCENT_HOVER)
        self._active_proc = None; self._running = False

    def _cancel(self):
        self._was_cancelled = True
        if self._active_proc and self._active_proc.poll() is None:
            self._active_proc.terminate()
            try: self._active_proc.wait(timeout=5)
            except: self._active_proc.kill()
        self._finish(); self._sm("Cancelled.", WARNING)
        self._log("Cancelled.", WARNING)

    def _env(self):
        e = os.environ.copy(); e["PYTHONIOENCODING"]="utf-8"; return e

    # ─── Commands ─────────────────────────────────────────────────────────
    def _on_generate(self):
        if self._guard(self.run_btn): return
        if not self._validate_live(): return
        name = self.name_entry.get().strip()
        colors = normalize_colors("".join(self.selected_colors))
        cmd = [sys.executable,
               str(_scripts_dir/"generate_deck_scaffold.py"),
               "--name", name, "--colors", colors, "--archetype"]
        cmd.extend(sorted(self.selected_archetypes))
        if self.wildcard_var.get(): cmd.append("--wildcard")
        if self._tribes:
            cmd.append("--tribe"); cmd.extend(self._tribes)
        if self._selected_tags:
            cmd.extend(["--extra-tags",",".join(sorted(self._selected_tags))])
        od = self.output_entry.get().strip()
        if od: cmd.extend(["--output-dir", od])
        focus_text = self.focus_box.get("1.0","end").strip()
        focus_names = [l.strip() for l in focus_text.splitlines() if l.strip()]
        if focus_names:
            cmd.append("--focus-cards"); cmd.extend(focus_names)
        if self.skip_queries_var.get(): cmd.append("--skip-queries")
        run_syn = self.run_synergy_var.get()
        auto_build = self.auto_build_var.get()
        self._start(self.run_btn, "Generate Scaffold")
        threading.Thread(target=self._bg_scaffold,
            args=(cmd, colors, run_syn, auto_build, focus_names),
            daemon=True).start()

    def _on_run_queries(self):
        if self._guard(self.rq_btn): return
        p = self.rq_entry.get().strip()
        if not p: self._sm("Select session.md first.", ERROR); return
        cmd = [sys.executable, str(_scripts_dir/"run_session_queries.py"), p]
        if self.rq_force.get(): cmd.append("--force")
        if self.rq_dryrun.get(): cmd.append("--dry-run")
        self._start(self.rq_btn, "Run Queries")
        threading.Thread(target=self._bg_generic, args=(cmd,"queries"),
                         daemon=True).start()

    def _on_synergy(self):
        if self._guard(self.syn_btn): return
        inp = self.syn_in.get().strip()
        if not inp: self._sm("Select input file first.", ERROR); return
        cmd = [sys.executable, str(_scripts_dir/"synergy_analysis.py"), inp]
        t = self.syn_thresh.get().strip()
        if t and t!="3.0": cmd.extend(["--min-synergy",t])
        m = self._syn_mode.get()
        if m and m!="auto": cmd.extend(["--mode",m])
        o = self.syn_out.get().strip()
        if o: cmd.extend(["--output",o])
        self._start(self.syn_btn, "Analyze Synergy")
        threading.Thread(target=self._bg_generic, args=(cmd,"synergy"),
                         daemon=True).start()

    # ─── Background threads ───────────────────────────────────────────────
    def _stream(self, cmd):
        self.after(0, self._log, "$ "+" ".join(cmd), TEXT_MUTED)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace",
            cwd=str(self._repo.root), env=self._env())
        self._active_proc = proc
        lines = []
        for line in proc.stdout:
            lines.append(line); s = line.rstrip()
            if s.strip():
                c = (SUCCESS if "[OK]" in s else ERROR if "ERROR" in s
                     else ACCENT if "candidates" in s.lower() else TEXT)
                self.after(0, self._log, s, c)
        proc.wait()
        return proc.returncode==0, "".join(lines).strip()

    def _bg_generic(self, cmd, source):
        try: ok, out = self._stream(cmd)
        except Exception as e: ok, out = False, str(e)
        self.after(0, self._done, RunResult(ok, out, source=source))

    def _bg_scaffold(self, cmd, colors, run_syn, auto_build, focus_names):
        try: ok, out = self._stream(cmd)
        except Exception as e: ok, out = False, str(e)
        deck_dir = _extract_deck_dir(out) if ok else None
        if deck_dir:
            dp = Path(deck_dir)
            if not dp.is_absolute(): dp = self._repo.root / dp
            deck_dir = str(dp)
        syn = None
        if ok and run_syn and deck_dir:
            syn = self._bg_synergy(deck_dir)
        if ok and deck_dir:
            self._bg_sort(deck_dir)
        ab_msg = None; focus_log = []
        if ok and auto_build and deck_dir:
            ab_ok, ab_msg, focus_log = auto_build_decklist(
                deck_dir, colors, focus_names)
            if ab_ok:
                self.after(0, self._log, "", TEXT)
                self.after(0, self._log,
                    "\u2500"*3+" Auto-built Decklist "+"\u2500"*28, SUCCESS)
                for msg, clr in focus_log:
                    if msg: self.after(0, self._log, msg, clr)
                self.after(0, self._log, f"  {ab_msg}", SUCCESS)
            else:
                self.after(0, self._log,
                    f"  Auto-build skipped: {ab_msg}", TEXT_DIM)
                ab_msg = None
        files = _verify_files(deck_dir) if deck_dir else []
        self.after(0, self._done,
            RunResult(ok, out, syn, "scaffold", deck_dir, files,
                      ab_msg, focus_log))

    def _bg_synergy(self, deck_dir):
        session = Path(deck_dir)/"session.md"
        if not session.exists(): return None
        self.after(0, self._log, "\nRunning synergy analysis\u2026", ACCENT)
        report = Path(deck_dir)/"synergy_report.md"
        cmd = [sys.executable, str(_scripts_dir/"synergy_analysis.py"),
               str(session), "--output", str(report), "--top", "200"]
        try:
            subprocess.run(cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
                cwd=str(self._repo.root), env=self._env(), timeout=120)
            if report.exists():
                return report.read_text(encoding="utf-8").strip()
            return None
        except Exception as e: return f"Synergy failed: {e}"

    def _bg_sort(self, deck_dir):
        d = Path(deck_dir)
        changed, n = sort_and_rewrite_csv(d/"top_200.csv")
        if changed:
            self.after(0, self._log,
                f"  Sorted top_200.csv ({n:,} rows)", SUCCESS)
        merged, pn = merge_scores_into_candidate_pool(deck_dir)
        if merged:
            self.after(0, self._log,
                f"  Merged scores into candidate_pool.csv ({pn:,} cards)",
                SUCCESS)

    # ─── Completion ───────────────────────────────────────────────────────
    def _done(self, r):
        cancelled = self._was_cancelled
        self._was_cancelled = False; self._finish()
        if cancelled: return
        if r.source=="scaffold" and r.success: self._show_summary(r)
        if r.synergy_output: self._show_synergy(r.synergy_output)
        if r.success:
            if r.source=="scaffold":
                n = len(r.files_found)
                name = Path(r.deck_dir).name if r.deck_dir else "?"
                msg = f"Done \u2014 {n} files in {name}"
                if r.auto_build_msg:
                    msg += f"  |  {r.auto_build_msg.split('|')[0].strip()}"
                elif r.synergy_output:
                    v = "PASS" if "[FAIL]" not in r.synergy_output else "FAIL"
                    msg += f"  |  Synergy: {v}"
                self._sm(msg, SUCCESS)
                if r.deck_dir and Path(r.deck_dir).exists():
                    self._last_deck_dir = r.deck_dir
                    self._open_btn.configure(state="normal")
            else: self._sm("Done.", SUCCESS)
        else: self._sm("Error \u2014 see log.", ERROR)

    def _show_summary(self, r):
        self._log("", TEXT)
        self._log("\u2500"*3+" Scaffold Complete "+"\u2500"*30, SUCCESS)
        if r.deck_dir: self._log(f"  Folder: {r.deck_dir}", INFO_BLUE)
        all_f = SCAFFOLD_FILES+["synergy_report.md","top_200.csv"]
        for f in all_f:
            if f in r.files_found:
                fp = Path(r.deck_dir)/f if r.deck_dir else None
                sz = ""
                if fp and fp.exists():
                    kb = fp.stat().st_size/1024; sz = f"  ({kb:,.1f} KB)"
                self._log(f"  \u2713 {f}{sz}", SUCCESS)
            elif f in SCAFFOLD_FILES:
                self._log(f"  \u2717 {f}  (missing)", ERROR)
        missing = [f for f in SCAFFOLD_FILES if f not in r.files_found]
        self._log("", TEXT)
        if missing: self._log(f"  WARNING: {len(missing)} file(s) missing!", WARNING)
        else: self._log("  All files created.", SUCCESS)

    def _show_synergy(self, syn):
        self._log("", TEXT)
        self._log("\u2500"*3+" Gate 2.5 Synergy "+"\u2500"*30, ACCENT)
        self._log("  (Deck feedback, not an error)", TEXT_MUTED)
        self._log("", TEXT)
        for line in syn.splitlines():
            c = (ERROR if "[FAIL]" in line else SUCCESS if "[PASS]" in line
                 else INFO_BLUE if "[INFO]" in line
                 else ACCENT if line.startswith(("#","**")) else TEXT)
            self._log(line, c)


def main():
    ScaffoldApp().mainloop()

if __name__ == "__main__":
    main()
