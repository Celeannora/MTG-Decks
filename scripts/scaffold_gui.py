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
COLORS_MAP = {"W": "White", "U": "Blue", "B": "Black", "R": "Red", "G": "Green"}
COLOR_ORDER = "WUBRG"
APP_TITLE = "MTG Deck Scaffold Generator"
WIN_W, WIN_H = 760, 700

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

        # Scrollable content
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG, scrollbar_button_color=BORDER)
        self.scroll.pack(fill="both", expand=True, padx=0, pady=0)

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

        self._section("6  Options")
        self._build_options()

        self._section("7  Output Directory")
        self._build_output_dir()

        # Status + Run button
        self._build_footer()

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
        for i, arch in enumerate(ARCHETYPES):
            btn = ctk.CTkButton(
                frame,
                text=arch.capitalize(),
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
            btn.grid(row=i // 5, column=i % 5, padx=(0, 8), pady=(0, 8), in_=frame)
            self._arch_buttons[arch] = btn

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
        if self._tribes:
            cmd += ["--tribe"] + self._tribes

        if self._selected_tags:
            cmd += ["--extra-tags", ",".join(sorted(self._selected_tags))]

        output_dir = self.output_entry.get().strip()
        if output_dir:
            cmd += ["--output-dir", output_dir]

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

        self.after(0, self._on_done, success, output)

    def _on_done(self, success: bool, output: str):
        self.run_btn.configure(state="normal", text="Generate Scaffold")
        if success:
            # Extract output path from the script's stdout
            path_hint = ""
            for line in output.splitlines():
                if "Output:" in line:
                    path_hint = line.split("Output:")[-1].strip()
                    break
            msg = f"Done! Scaffold created at {path_hint}" if path_hint else "Scaffold generated successfully."
            self._set_status(msg, SUCCESS)
            self._show_output_popup(output)
        else:
            self._set_status(f"Error: {output[:120]}", ERROR)
            self._show_output_popup(output, error=True)

    def _show_output_popup(self, output: str, error: bool = False):
        win = ctk.CTkToplevel(self)
        win.title("Error" if error else "Scaffold Output")
        win.geometry("680x420")
        win.configure(fg_color=BG)
        win.lift()
        win.focus()

        ctk.CTkLabel(
            win,
            text="Error" if error else "Scaffold Generated",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=ERROR if error else SUCCESS,
        ).pack(anchor="w", padx=20, pady=(16, 4))

        box = ctk.CTkTextbox(
            win,
            fg_color=SURFACE,
            text_color=TEXT,
            font=ctk.CTkFont(family="Courier New", size=12),
            border_color=BORDER,
            border_width=1,
            corner_radius=6,
            wrap="word",
        )
        box.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        box.insert("end", output)
        box.configure(state="disabled")

        ctk.CTkButton(
            win,
            text="Close",
            fg_color=SURFACE_ALT,
            hover_color=BORDER,
            text_color=TEXT,
            corner_radius=6,
            command=win.destroy,
        ).pack(pady=(0, 16))


# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = ScaffoldApp()
    app.mainloop()


if __name__ == "__main__":
    main()
