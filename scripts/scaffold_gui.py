#!/usr/bin/env python3
"""
Deck Scaffold Generator — GUI (customtkinter)

A modern graphical interface for generate_deck_scaffold.py.
Presents the same wizard flow in a clean, dark-mode desktop window.

Usage:
    python scripts/scaffold_gui.py

Requirements:
    pip install customtkinter

All scaffold logic is delegated to generate_deck_scaffold.py — this file
is purely the UI layer. No business logic lives here.
"""

import subprocess
import sys
import threading
from pathlib import Path

# ── Dependency check ─────────────────────────────────────────────────────────
try:
    import customtkinter as ctk
except ImportError:
    print("customtkinter is not installed. Run: pip install customtkinter")
    sys.exit(1)

# ── Import shared data from scaffold script ───────────────────────────────────
_scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_scripts_dir))
from generate_deck_scaffold import (
    ALL_CREATURE_TYPES,
    ARCHETYPE_QUERIES,
    sanitize_folder_name,
)
from mtg_utils import RepoPaths

# ── Constants ─────────────────────────────────────────────────────────────────
ARCHETYPES = sorted(ARCHETYPE_QUERIES.keys())
ARCHETYPE_LABELS = {
    "opp_mill": "Opp Mill",
    "self_mill": "Self Mill",
    "reanimation": "Reanimation",
    # all other keys use title-cased key name as fallback
}
COLORS_MAP = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}
COLOR_ORDER = "WUBRG"
APP_TITLE = "MTG Deck Scaffold Generator"
WIN_W, WIN_H = 800, 880

# MTG color accent hex (loosely inspired by card frame colors)
ACCENT = "#4F98A3"
ACCENT_HOVER = "#227F8B"
BG = "#171614"
SURFACE = "#1C1B19"
SURFACE_ALT = "#201F1D"
BORDER = "#393836"
TEXT = "#CDCCCA"
TEXT_MUTED = "#797876"
SUCCESS = "#6DAA45"
ERROR = "#D163A7"
WARNING = "#BB653B"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def normalize_colors(raw: str) -> str:
    seen = dict.fromkeys(c for c in raw.upper() if c in COLOR_ORDER)
    return "".join(c for c in COLOR_ORDER if c in seen)


def filter_tribes(query: str) -> list:
    q = query.strip().lower()
    if not q:
        return []
    return [t for t in ALL_CREATURE_TYPES if q in t.lower()]


# ─────────────────────────────────────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────────────────────────────────────

class ScaffoldApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(APP_TITLE)
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        # State
        self.selected_colors: set = set()
        self.selected_archetypes: set = set()
        self.wildcard_var = ctk.BooleanVar(value=False)
        self.tribe_var = ctk.StringVar()
        self._tribes: list = []  # multiple tribes supported

        self._build_ui()

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        title_frame = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=56)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        ctk.CTkLabel(
            title_frame,
            text=APP_TITLE,
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=TEXT,
        ).pack(side="left", padx=20, pady=14)

        # Tab view
        self.tabs = ctk.CTkTabview(
            self,
            fg_color=BG,
            segmented_button_fg_color=SURFACE,
            segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_color=SURFACE,
            segmented_button_unselected_hover_color=SURFACE_ALT,
            text_color=TEXT,
            text_color_disabled=TEXT_MUTED,
        )
        self.tabs.pack(fill="both", expand=True, padx=0, pady=0)
        self.tabs.add("New Scaffold")
        self.tabs.add("Run Queries")
        self.tabs.add("Synergy Analysis")

        self._build_scaffold_tab()
        self._build_run_queries_tab()
        self._build_synergy_tab()

        # Inline log panel (collapsed by default)
        self._build_log_panel()

        # Shared footer
        self._build_footer()

    def _build_scaffold_tab(self):
        tab = self.tabs.tab("New Scaffold")
        self.scroll = ctk.CTkScrollableFrame(tab, fg_color=BG, scrollbar_button_color=BORDER)
        self.scroll.pack(fill="both", expand=True)

        self._section("1  Deck Name")
        self.name_entry = self._entry(placeholder="e.g. Orzhov Lifegain")

        self._section("2  Color Identity")
        self._build_color_pickers()

        self._section("3  Archetype  (select one or more)")
        self._build_archetype_grid()

        self._section("4  Creature Subtype  (required for Tribal)")
        self._build_tribe_search()

        self._section("5  Extra Search Tags  (optional)")
        self._build_tag_grid()

        self._section("6  Focus Cards  (optional)")
        self._build_focus_cards()

        self._section("7  Options")
        self._build_options()

        self._section("8  Output Directory")
        self._build_output_dir()

    def _build_run_queries_tab(self):
        tab = self.tabs.tab("Run Queries")
        frame = ctk.CTkScrollableFrame(tab, fg_color=BG, scrollbar_button_color=BORDER)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame,
            text="Execute pending search_cards.py queries in a session.md",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w", padx=24, pady=(18, 2))
        ctk.CTkLabel(
            frame,
            text="Finds all (run this query and paste results here) placeholders, runs them, and fills the results in-place.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
            wraplength=700,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 14))

        # Session file picker
        ctk.CTkLabel(frame, text="session.md", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=24)
        rq_row = ctk.CTkFrame(frame, fg_color="transparent")
        rq_row.pack(fill="x", padx=24, pady=(4, 12))
        self.rq_path_entry = ctk.CTkEntry(
            rq_row, placeholder_text="Path to session.md",
            fg_color=SURFACE, border_color=BORDER, text_color=TEXT,
            placeholder_text_color=TEXT_MUTED, font=ctk.CTkFont(size=13), height=38, corner_radius=6,
        )
        self.rq_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            rq_row, text="Browse", width=80, height=38,
            fg_color=SURFACE_ALT, hover_color=BORDER, text_color=TEXT,
            corner_radius=6, font=ctk.CTkFont(size=12),
            command=self._browse_session_file,
        ).pack(side="left")

        # Options
        self.rq_force_var = ctk.BooleanVar(value=False)
        self.rq_dryrun_var = ctk.BooleanVar(value=False)
        opts = ctk.CTkFrame(frame, fg_color="transparent")
        opts.pack(anchor="w", padx=24, pady=(0, 16))
        ctk.CTkCheckBox(opts, text="Force re-run all queries (even completed ones)",
                        variable=self.rq_force_var, font=ctk.CTkFont(size=12),
                        text_color=TEXT, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        border_color=BORDER, checkmark_color="#FFFFFF").pack(anchor="w", pady=2)
        ctk.CTkCheckBox(opts, text="Dry run (show what would run, no changes)",
                        variable=self.rq_dryrun_var, font=ctk.CTkFont(size=12),
                        text_color=TEXT, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                        border_color=BORDER, checkmark_color="#FFFFFF").pack(anchor="w", pady=2)

        ctk.CTkButton(
            frame, text="Run Queries", height=44, corner_radius=8,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_run_queries,
        ).pack(anchor="w", padx=24)

    def _build_synergy_tab(self):
        tab = self.tabs.tab("Synergy Analysis")
        frame = ctk.CTkScrollableFrame(tab, fg_color=BG, scrollbar_button_color=BORDER)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            frame,
            text="Gate 2.5 — Synergy Analysis",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w", padx=24, pady=(18, 2))
        ctk.CTkLabel(
            frame,
            text="Scores pairwise tag-based interactions for all cards in a session.md or decklist.txt. "
                 "Checks all 5 Gate 2.5 thresholds and generates a pre-filled report. "
                 "Auto mode detects pool vs deck size automatically; use pool for >40 cards, deck for ≤40.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
            wraplength=700,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 14))

        # Input file
        ctk.CTkLabel(frame, text="Input file  (session.md or decklist.txt)",
                     font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT).pack(anchor="w", padx=24)
        syn_row = ctk.CTkFrame(frame, fg_color="transparent")
        syn_row.pack(fill="x", padx=24, pady=(4, 12))
        self.syn_input_entry = ctk.CTkEntry(
            syn_row, placeholder_text="Path to session.md or decklist.txt",
            fg_color=SURFACE, border_color=BORDER, text_color=TEXT,
            placeholder_text_color=TEXT_MUTED, font=ctk.CTkFont(size=13), height=38, corner_radius=6,
        )
        self.syn_input_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            syn_row, text="Browse", width=80, height=38,
            fg_color=SURFACE_ALT, hover_color=BORDER, text_color=TEXT,
            corner_radius=6, font=ctk.CTkFont(size=12),
            command=self._browse_synergy_input,
        ).pack(side="left")

        # Output file
        ctk.CTkLabel(frame, text="Output report  (optional — leave blank to show in popup)",
                     font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT).pack(anchor="w", padx=24)
        syn_out_row = ctk.CTkFrame(frame, fg_color="transparent")
        syn_out_row.pack(fill="x", padx=24, pady=(4, 12))
        self.syn_output_entry = ctk.CTkEntry(
            syn_out_row, placeholder_text="e.g. Decks/my_deck/synergy_report.md",
            fg_color=SURFACE, border_color=BORDER, text_color=TEXT,
            placeholder_text_color=TEXT_MUTED, font=ctk.CTkFont(size=13), height=38, corner_radius=6,
        )
        self.syn_output_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            syn_out_row, text="Browse", width=80, height=38,
            fg_color=SURFACE_ALT, hover_color=BORDER, text_color=TEXT,
            corner_radius=6, font=ctk.CTkFont(size=12),
            command=self._browse_synergy_output,
        ).pack(side="left")

        # Min synergy threshold
        thresh_row = ctk.CTkFrame(frame, fg_color="transparent")
        thresh_row.pack(anchor="w", padx=24, pady=(0, 16))
        ctk.CTkLabel(thresh_row, text="Min avg synergy threshold:",
                     font=ctk.CTkFont(size=12), text_color=TEXT).pack(side="left", padx=(0, 8))
        self.syn_threshold_entry = ctk.CTkEntry(
            thresh_row, width=60, fg_color=SURFACE, border_color=BORDER,
            text_color=TEXT, font=ctk.CTkFont(size=13), height=32, corner_radius=6,
        )
        self.syn_threshold_entry.insert(0, "3.0")
        self.syn_threshold_entry.pack(side="left")

        # Analysis mode selector
        mode_row = ctk.CTkFrame(frame, fg_color="transparent")
        mode_row.pack(anchor="w", padx=24, pady=(0, 16))
        ctk.CTkLabel(mode_row, text="Analysis Mode:",
                     font=ctk.CTkFont(size=12), text_color=TEXT).pack(side="left", padx=(0, 8))
        self._synergy_mode_var = ctk.StringVar(value="auto")
        ctk.CTkOptionMenu(
            mode_row,
            values=["auto", "pool", "deck"],
            variable=self._synergy_mode_var,
            width=110,
            height=32,
            fg_color=SURFACE,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER,
            dropdown_fg_color=SURFACE,
            dropdown_hover_color=SURFACE_ALT,
            text_color=TEXT,
            dropdown_text_color=TEXT,
            font=ctk.CTkFont(size=12),
            corner_radius=6,
        ).pack(side="left")

        ctk.CTkButton(
            frame, text="Analyze Synergy", height=44, corner_radius=8,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_synergy,
        ).pack(anchor="w", padx=24)

    def _section(self, label: str):
        ctk.CTkLabel(
            self.scroll,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w", padx=24, pady=(18, 4))

    def _entry(self, placeholder: str = "") -> ctk.CTkEntry:
        e = ctk.CTkEntry(
            self.scroll,
            placeholder_text=placeholder,
            fg_color=SURFACE,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13),
            height=38,
            corner_radius=6,
        )
        e.pack(fill="x", padx=24, pady=(0, 4))
        return e

    def _build_color_pickers(self):
        frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        frame.pack(fill="x", padx=24, pady=(0, 4))
        self._color_buttons = {}
        color_hex = {"W": "#F5F0E8", "U": "#4A7FBF", "B": "#2D2D2D", "R": "#C94040", "G": "#3A7A3A"}
        color_text = {"W": "#28251D", "U": "#FFFFFF", "B": "#CDCCCA", "R": "#FFFFFF", "G": "#FFFFFF"}
        for c, name in COLORS_MAP.items():
            btn = ctk.CTkButton(
                frame,
                text=f"{c}\n{name}",
                width=108,
                height=56,
                corner_radius=8,
                fg_color=SURFACE_ALT,
                hover_color=color_hex[c],
                text_color=TEXT_MUTED,
                border_color=BORDER,
                border_width=1,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda col=c: self._toggle_color(col),
            )
            btn.pack(side="left", padx=(0, 8))
            self._color_buttons[c] = (btn, color_hex[c], color_text[c])

    def _toggle_color(self, c: str):
        btn, active_color, active_text = self._color_buttons[c]
        if c in self.selected_colors:
            self.selected_colors.discard(c)
            btn.configure(fg_color=SURFACE_ALT, text_color=TEXT_MUTED, border_color=BORDER)
        else:
            self.selected_colors.add(c)
            btn.configure(fg_color=active_color, text_color=active_text, border_color=active_color)

    def _build_archetype_grid(self):
        frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        frame.pack(fill="x", padx=24, pady=(0, 4))
        self._arch_buttons = {}

        # Custom sort: opp_mill immediately before self_mill, rest alphabetical
        mill_keys = {"opp_mill", "self_mill"}
        non_mill = [a for a in ARCHETYPES if a not in mill_keys]
        ordered = []
        for a in non_mill:
            # Insert mill pair right before the first key that sorts after "opp_mill"
            if not any(m in ordered for m in mill_keys) and a > "opp_mill":
                ordered.extend(k for k in ["opp_mill", "self_mill"] if k in ARCHETYPES)
            ordered.append(a)
        if not any(m in ordered for m in mill_keys):
            ordered.extend(k for k in ["opp_mill", "self_mill"] if k in ARCHETYPES)

        row = 0
        col = 0
        cols_per_row = 5
        for arch in ordered:
            # Insert mill group header before opp_mill
            if arch == "opp_mill":
                if col != 0:
                    row += 1
                    col = 0
                ctk.CTkLabel(
                    frame,
                    text="── Mill ──",
                    text_color=ACCENT,
                    font=ctk.CTkFont(size=11),
                ).grid(row=row, column=0, columnspan=cols_per_row, sticky="w",
                       padx=(0, 8), pady=(4, 2), in_=frame)
                row += 1
                col = 0

            label = ARCHETYPE_LABELS.get(arch, arch.replace("_", " ").title())
            btn = ctk.CTkButton(
                frame,
                text=label,
                width=130,
                height=38,
                corner_radius=6,
                fg_color=SURFACE_ALT,
                hover_color=ACCENT_HOVER,
                text_color=TEXT_MUTED,
                border_color=BORDER,
                border_width=1,
                font=ctk.CTkFont(size=12),
                command=lambda a=arch: self._toggle_archetype(a),
            )
            btn.grid(row=row, column=col, padx=(0, 8), pady=(0, 8), in_=frame)
            self._arch_buttons[arch] = btn
            col += 1
            if col >= cols_per_row:
                col = 0
                row += 1

    def _toggle_archetype(self, arch: str):
        btn = self._arch_buttons[arch]
        if arch in self.selected_archetypes:
            self.selected_archetypes.discard(arch)
            btn.configure(fg_color=SURFACE_ALT, text_color=TEXT_MUTED, border_color=BORDER)
        else:
            self.selected_archetypes.add(arch)
            btn.configure(fg_color=ACCENT, text_color="#FFFFFF", border_color=ACCENT)
        # Enable/disable tribe section
        tribal_active = "tribal" in self.selected_archetypes
        self._tribe_frame.configure(fg_color="transparent" if tribal_active else BG)
        for w in self._tribe_widgets:
            w.configure(state="normal" if tribal_active else "disabled")
        if not tribal_active:
            # Clear all tribe selections when tribal is deselected
            self._tribes.clear()
            self._refresh_tribe_chips()
            for w in self._tribe_results.winfo_children():
                w.destroy()

    def _build_tribe_search(self):
        self._tribe_frame = ctk.CTkFrame(self.scroll, fg_color=BG)
        self._tribe_frame.pack(fill="x", padx=24, pady=(0, 4))

        ctk.CTkLabel(
            self._tribe_frame,
            text="Enabled when Tribal archetype is selected above. Multiple subtypes supported.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(0, 4))

        search_entry = ctk.CTkEntry(
            self._tribe_frame,
            placeholder_text="Type to search (e.g. ang → Angel, Changeling...)",
            textvariable=self.tribe_var,
            fg_color=SURFACE,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13),
            height=38,
            corner_radius=6,
            state="disabled",
        )
        search_entry.pack(fill="x", pady=(0, 4))
        self.tribe_var.trace_add("write", self._on_tribe_search)

        self._tribe_results = ctk.CTkFrame(self._tribe_frame, fg_color=SURFACE, corner_radius=6)
        self._tribe_results.pack(fill="x")

        # Chip row for selected tribes
        self._tribe_chips_frame = ctk.CTkFrame(self._tribe_frame, fg_color="transparent")
        self._tribe_chips_frame.pack(fill="x", pady=(6, 0))

        self._tribe_widgets = [search_entry]

    def _on_tribe_search(self, *_):
        for w in self._tribe_results.winfo_children():
            w.destroy()

        query = self.tribe_var.get()
        if not query.strip():
            return

        matches = filter_tribes(query)
        if not matches:
            ctk.CTkLabel(
                self._tribe_results,
                text=f"  No types match '{query}'",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=12),
            ).pack(anchor="w", padx=8, pady=4)
            return

        show = matches[:12]
        for t in show:
            already = t in self._tribes
            btn = ctk.CTkButton(
                self._tribe_results,
                text=f"✓ {t}" if already else t,
                fg_color=ACCENT if already else "transparent",
                hover_color=SURFACE_ALT,
                text_color="#FFFFFF" if already else TEXT,
                font=ctk.CTkFont(size=12),
                anchor="w",
                height=28,
                corner_radius=4,
                command=lambda name=t: self._toggle_tribe(name),
            )
            btn.pack(fill="x", padx=4, pady=1)

        if len(matches) > 12:
            ctk.CTkLabel(
                self._tribe_results,
                text=f"  +{len(matches) - 12} more — keep typing to narrow",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=11),
            ).pack(anchor="w", padx=8, pady=(2, 4))

    def _toggle_tribe(self, name: str):
        if name in self._tribes:
            self._tribes.remove(name)
        else:
            self._tribes.append(name)
        self._refresh_tribe_chips()
        self._on_tribe_search()  # refresh dropdown checkmarks

    def _refresh_tribe_chips(self):
        for w in self._tribe_chips_frame.winfo_children():
            w.destroy()
        if not self._tribes:
            return
        for t in self._tribes:
            chip = ctk.CTkFrame(self._tribe_chips_frame, fg_color=SURFACE_ALT, corner_radius=14)
            chip.pack(side="left", padx=(0, 6), pady=2)
            ctk.CTkLabel(
                chip,
                text=t,
                font=ctk.CTkFont(size=12),
                text_color=TEXT,
            ).pack(side="left", padx=(10, 4), pady=4)
            ctk.CTkButton(
                chip,
                text="×",
                width=22,
                height=22,
                fg_color="transparent",
                hover_color=BORDER,
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=13, weight="bold"),
                corner_radius=11,
                command=lambda name=t: self._toggle_tribe(name),
            ).pack(side="left", padx=(0, 4))

    def _build_tag_grid(self):
        ALL_TAGS = [
            "lifegain", "removal", "draw", "counter", "ramp", "haste",
            "flying", "trample", "mill", "wipe", "pump", "bounce",
            "etb", "tutor", "flash", "tribal", "protection", "deathtouch",
        ]
        self._selected_tags: set = set()
        self._tag_buttons: dict = {}

        frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        frame.pack(fill="x", padx=24, pady=(0, 8))

        for i, tag in enumerate(ALL_TAGS):
            btn = ctk.CTkButton(
                frame,
                text=tag,
                width=110,
                height=32,
                corner_radius=16,
                fg_color=SURFACE_ALT,
                hover_color=ACCENT_HOVER,
                text_color=TEXT_MUTED,
                border_color=BORDER,
                border_width=1,
                font=ctk.CTkFont(size=12),
                command=lambda t=tag: self._toggle_tag(t),
            )
            btn.grid(row=i // 6, column=i % 6, padx=(0, 6), pady=(0, 6), in_=frame)
            self._tag_buttons[tag] = btn

    def _toggle_tag(self, tag: str):
        btn = self._tag_buttons[tag]
        if tag in self._selected_tags:
            self._selected_tags.discard(tag)
            btn.configure(fg_color=SURFACE_ALT, text_color=TEXT_MUTED, border_color=BORDER)
        else:
            self._selected_tags.add(tag)
            btn.configure(fg_color=ACCENT, text_color="#FFFFFF", border_color=ACCENT)

    def _build_focus_cards(self):
        """Text area for specific cards to guarantee in the candidate pool."""
        ctk.CTkLabel(
            self.scroll,
            text="One card name per line. These are looked up by exact name and added to the pool regardless of archetype queries.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
            wraplength=700,
            justify="left",
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.focus_cards_box = ctk.CTkTextbox(
            self.scroll,
            fg_color=SURFACE,
            border_color=BORDER,
            text_color=TEXT,
            font=ctk.CTkFont(family="Courier New", size=12),
            border_width=1,
            corner_radius=6,
            height=90,
            wrap="word",
        )
        self.focus_cards_box.pack(fill="x", padx=24, pady=(0, 4))
        self.focus_cards_box.insert("end", "")  # placeholder handled by hint label above

    def _build_options(self):
        frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        frame.pack(fill="x", padx=24, pady=(0, 4))
        self.skip_queries_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            frame,
            text="Skip queries  (generate template without running searches — useful offline)",
            variable=self.skip_queries_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            border_color=BORDER,
            checkmark_color="#FFFFFF",
        ).pack(anchor="w")

        self.run_synergy_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            frame,
            text="Run synergy analysis after scaffold  (generates Gate 2.5 report from session.md)",
            variable=self.run_synergy_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            border_color=BORDER,
            checkmark_color="#FFFFFF",
        ).pack(anchor="w", pady=(6, 0))

        ctk.CTkCheckBox(
            frame,
            text="Wildcard  (tribe as hint only — skips tribal --name filter, returns full archetype pool)",
            variable=self.wildcard_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT,
            fg_color=WARNING,
            hover_color=ACCENT_HOVER,
            border_color=BORDER,
            checkmark_color="#FFFFFF",
        ).pack(anchor="w", pady=(6, 0))

    def _build_output_dir(self):
        frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        frame.pack(fill="x", padx=24, pady=(0, 8))
        self.output_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Leave blank for default: Decks/",
            fg_color=SURFACE,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=13),
            height=38,
            corner_radius=6,
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            frame,
            text="Browse",
            width=80,
            height=38,
            fg_color=SURFACE_ALT,
            hover_color=BORDER,
            text_color=TEXT,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            command=self._browse_output,
        ).pack(side="left")

    def _browse_output(self):
        from tkinter import filedialog
        d = filedialog.askdirectory(title="Select output directory")
        if d:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, d)

    def _browse_session_file(self):
        from tkinter import filedialog
        f = filedialog.askopenfilename(title="Select session.md", filetypes=[("Markdown", "*.md"), ("All", "*.*")])
        if f:
            self.rq_path_entry.delete(0, "end")
            self.rq_path_entry.insert(0, f)

    def _browse_synergy_input(self):
        from tkinter import filedialog
        f = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("Markdown / Text", "*.md *.txt"), ("All", "*.*")],
        )
        if f:
            self.syn_input_entry.delete(0, "end")
            self.syn_input_entry.insert(0, f)

    def _browse_synergy_output(self):
        from tkinter import filedialog
        f = filedialog.asksaveasfilename(
            title="Save synergy report as",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All", "*.*")],
        )
        if f:
            self.syn_output_entry.delete(0, "end")
            self.syn_output_entry.insert(0, f)

    def _on_run_queries(self):
        session_file = self.rq_path_entry.get().strip()
        if not session_file:
            self._set_status("Select a session.md file first.", ERROR)
            return
        cmd = [
            sys.executable,
            str(_scripts_dir / "run_session_queries.py"),
            session_file,
        ]
        if self.rq_force_var.get():
            cmd.append("--force")
        if self.rq_dryrun_var.get():
            cmd.append("--dry-run")
        self.run_btn.configure(state="disabled", text="Running...")
        self._set_status("Running session queries...", ACCENT)
        import threading
        threading.Thread(target=self._run_tool, args=(cmd,), daemon=True).start()

    def _on_synergy(self):
        input_file = self.syn_input_entry.get().strip()
        if not input_file:
            self._set_status("Select an input file first.", ERROR)
            return
        cmd = [
            sys.executable,
            str(_scripts_dir / "synergy_analysis.py"),
            input_file,
        ]
        threshold = self.syn_threshold_entry.get().strip()
        if threshold and threshold != "3.0":
            cmd += ["--min-synergy", threshold]
        mode = self._synergy_mode_var.get()
        if mode and mode != "auto":
            cmd += ["--mode", mode]
        output_file = self.syn_output_entry.get().strip()
        if output_file:
            cmd += ["--output", output_file]
        self.run_btn.configure(state="disabled", text="Running...")
        self._set_status("Analyzing synergy...", ACCENT)
        import threading
        threading.Thread(target=self._run_tool, args=(cmd,), daemon=True).start()

    def _run_tool(self, cmd: list):
        """Generic subprocess runner — streams output into the inline log."""
        import os
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        self.after(0, self._clear_log)
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                cwd=str(RepoPaths().root), env=env,
            )
            lines = []
            for line in proc.stdout:
                lines.append(line)
                stripped = line.strip()
                if stripped:
                    self.after(0, self._append_log, stripped, ACCENT)
            proc.wait()
            output = "".join(lines).strip()
            success = proc.returncode == 0
        except Exception as e:
            output = str(e)
            success = False
        self.after(0, self._on_done, success, output)

    def _build_log_panel(self):
        """Inline collapsible log panel — replaces the popup."""
        self._log_visible = False

        self._log_toggle_frame = ctk.CTkFrame(self, fg_color=SURFACE_ALT, corner_radius=0, height=28)
        self._log_toggle_frame.pack(fill="x")
        self._log_toggle_frame.pack_propagate(False)

        self._log_toggle_btn = ctk.CTkButton(
            self._log_toggle_frame,
            text="▶  Log",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=TEXT_MUTED,
            fg_color="transparent",
            hover_color=BORDER,
            anchor="w",
            height=28,
            corner_radius=0,
            command=self._toggle_log,
        )
        self._log_toggle_btn.pack(side="left", fill="y", padx=8)

        self._log_status_inline = ctk.CTkLabel(
            self._log_toggle_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
        )
        self._log_status_inline.pack(side="left", padx=4)

        self._log_panel = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=0)
        self._log_panel.pack(fill="x")
        self._log_panel.pack_propagate(False)

        self._log_box = ctk.CTkTextbox(
            self._log_panel,
            fg_color=SURFACE,
            text_color=TEXT,
            font=ctk.CTkFont(family="Courier New", size=11),
            border_width=0,
            corner_radius=0,
            wrap="word",
            state="disabled",
        )
        self._log_box.pack(fill="both", expand=True, padx=0, pady=0)

    def _toggle_log(self):
        self._log_visible = not self._log_visible
        if self._log_visible:
            self._log_panel.configure(height=160)
            self._log_toggle_btn.configure(text="▼  Log")
        else:
            self._log_panel.configure(height=0)
            self._log_toggle_btn.configure(text="▶  Log")

    def _append_log(self, text: str, color: str = TEXT):
        """Append a line to the inline log and auto-expand it."""
        self._log_box.configure(state="normal")
        self._log_box.insert("end", text if text.endswith("\n") else text + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")
        # Auto-expand on first write
        if not self._log_visible:
            self._toggle_log()
        # Mirror latest line to the toggle bar
        short = text.strip()[:80]
        self._log_status_inline.configure(text=short, text_color=color)

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")
        self._log_status_inline.configure(text="")

    def _build_footer(self):
        sep = ctk.CTkFrame(self, height=1, fg_color=BORDER, corner_radius=0)
        sep.pack(fill="x")

        footer = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=80)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            footer,
            text="Fill in the fields above and click Generate.",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            wraplength=520,
            justify="left",
        )
        self.status_label.pack(side="left", padx=20)

        self.run_btn = ctk.CTkButton(
            footer,
            text="Generate Scaffold",
            width=160,
            height=44,
            corner_radius=8,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_generate,
        )
        self.run_btn.pack(side="right", padx=20)

    # ── Validation & Run ──────────────────────────────────────────────────────

    def _set_status(self, msg: str, color: str = TEXT_MUTED):
        self.status_label.configure(text=msg, text_color=color)

    def _on_generate(self):
        # Validate
        name = self.name_entry.get().strip()
        if not name:
            self._set_status("Deck name is required.", ERROR)
            return

        wildcard = self.wildcard_var.get()
        colors = normalize_colors("".join(self.selected_colors))
        if not colors:
            self._set_status("Select at least one color.", ERROR)
            return

        if not self.selected_archetypes:
            self._set_status("Select at least one archetype.", ERROR)
            return

        if "tribal" in self.selected_archetypes and not self._tribes:
            self._set_status("Tribal selected — add at least one creature subtype.", WARNING)
            return

        # Build CLI args
        cmd = [
            sys.executable,
            str(_scripts_dir / "generate_deck_scaffold.py"),
            "--name", name,
            "--colors", colors,
            "--archetype", *sorted(self.selected_archetypes),
        ]
        if wildcard:
            cmd.append("--wildcard")
        if self._tribes:
            cmd += ["--tribe"] + self._tribes

        if self._selected_tags:
            cmd += ["--extra-tags", ",".join(sorted(self._selected_tags))]

        output_dir = self.output_entry.get().strip()
        if output_dir:
            cmd += ["--output-dir", output_dir]

        # Focus cards
        focus_text = self.focus_cards_box.get("1.0", "end").strip()
        if focus_text:
            focus_names = [ln.strip() for ln in focus_text.splitlines() if ln.strip()]
            if focus_names:
                cmd += ["--focus-cards"] + focus_names

        if self.skip_queries_var.get():
            cmd.append("--skip-queries")

        # Run in background thread so UI stays responsive
        self.run_btn.configure(state="disabled", text="Running...")
        self._set_status("Starting...", ACCENT)
        self._output_lines: list = []
        threading.Thread(target=self._run_scaffold, args=(cmd,), daemon=True).start()

    def _run_scaffold(self, cmd: list):
        try:
            import os
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(RepoPaths().root),
                env=env,
            )
            output_lines = []
            for line in proc.stdout:
                output_lines.append(line)
                # Stream progress to status bar on the main thread
                stripped = line.strip()
                if stripped:
                    self.after(0, self._set_status, stripped[:90], ACCENT)
            proc.wait()
            output = "".join(output_lines).strip()
            success = proc.returncode == 0
        except Exception as e:
            output = str(e)
            success = False

        synergy_output = None
        if success and self.run_synergy_var.get():
            # Find the session.md path from scaffold output
            deck_dir = None
            for line in output.splitlines():
                if "Output:" in line:
                    deck_dir = line.split("Output:")[-1].strip().rstrip("/\\").rstrip()
                    break
            if deck_dir:
                session_path = Path(deck_dir) / "session.md"
                if not session_path.is_absolute():
                    session_path = RepoPaths().root / session_path
                if session_path.exists():
                    self.after(0, self._set_status, "Running synergy analysis...", ACCENT)
                    synergy_report_path = session_path.parent / "synergy_report.md"
                    syn_cmd = [
                        sys.executable,
                        str(_scripts_dir / "synergy_analysis.py"),
                        str(session_path),
                        "--output", str(synergy_report_path),
                    ]
                    import os
                    env2 = os.environ.copy()
                    env2["PYTHONIOENCODING"] = "utf-8"
                    try:
                        syn_proc = subprocess.run(
                            syn_cmd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace",
                            cwd=str(RepoPaths().root), env=env2, timeout=120,
                        )
                        # --output writes to file; read it back for the popup
                        if synergy_report_path.exists():
                            synergy_output = synergy_report_path.read_text(encoding="utf-8").strip()
                        else:
                            synergy_output = syn_proc.stdout.strip() or syn_proc.stderr.strip() or "(no output)"
                    except Exception as e:
                        synergy_output = f"Synergy analysis failed: {e}"

        self.after(0, self._on_done, success, output, synergy_output)

    def _on_done(self, success: bool, output: str, synergy_output=None):
        self.run_btn.configure(state="normal", text="Generate Scaffold")
        self._clear_log()
        if output:
            for line in output.splitlines():
                self._append_log(line, TEXT)
        if synergy_output:
            self._append_log("", TEXT)
            self._append_log("── Gate 2.5 Synergy Report ─────────────────────", ACCENT)
            for line in synergy_output.splitlines():
                color = ERROR if "[FAIL]" in line else SUCCESS if "[PASS]" in line else TEXT
                self._append_log(line, color)
        if success:
            path_hint = ""
            for line in (output or "").splitlines():
                if "Output:" in line:
                    path_hint = line.split("Output:")[-1].strip()
                    break
            msg = f"Done — {path_hint}" if path_hint else "Done."
            if synergy_output:
                pass_fail = "PASS" if "[FAIL]" not in (synergy_output or "") else "FAIL"
                msg += f"  |  Synergy: {pass_fail}"
            self._set_status(msg, SUCCESS)
        else:
            self._set_status(f"Error — see log below.", ERROR)

# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = ScaffoldApp()
    app.mainloop()


if __name__ == "__main__":
    main()
