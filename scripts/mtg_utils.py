#!/usr/bin/env python3
"""
Shared utilities for MTG deck building scripts.

Provides:
  - RepoPaths: centralised directory-name configuration (no hardcoded paths)
  - parse_decklist: MTGA-format decklist parser

Every directory name that scripts rely on is defined once in RepoPaths.
To rename a folder, change it here and every script picks up the change.
"""

from pathlib import Path
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Centralised repo path configuration
# ---------------------------------------------------------------------------

class RepoPaths:
    """Single source of truth for every repo directory name.

    Usage::

        from mtg_utils import RepoPaths
        paths = RepoPaths()                      # auto-detect repo root
        paths = RepoPaths(root=some_path)         # explicit root

        paths.cards_dir   # .../cards_by_category
        paths.decks_dir   # .../Decks
        paths.local_db    # .../local_db
        paths.scripts_dir # .../scripts
        paths.templates   # .../.github/DECK_TEMPLATE
    """

    # ---- configurable directory names (change here, nowhere else) ---------
    CARDS_DIR_NAME      = "cards_by_category"
    DECKS_DIR_NAME      = "Decks"
    LOCAL_DB_DIR_NAME   = "local_db"
    SCRIPTS_DIR_NAME    = "scripts"
    TEMPLATES_DIR_NAME  = ".github/DECK_TEMPLATE"

    def __init__(self, root: Path | None = None) -> None:
        if root is None:
            # Default: assume this file lives in <repo>/scripts/
            root = Path(__file__).resolve().parent.parent
        self.root = root

    # ---- resolved absolute paths ------------------------------------------
    @property
    def cards_dir(self) -> Path:
        return self.root / self.CARDS_DIR_NAME

    @property
    def decks_dir(self) -> Path:
        return self.root / self.DECKS_DIR_NAME

    @property
    def local_db(self) -> Path:
        return self.root / self.LOCAL_DB_DIR_NAME

    @property
    def scripts_dir(self) -> Path:
        return self.root / self.SCRIPTS_DIR_NAME

    @property
    def templates(self) -> Path:
        return self.root / self.TEMPLATES_DIR_NAME


def parse_decklist(
    decklist_path: Path,
) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    """
    Parse an MTGA-format decklist.txt file.

    Returns:
        (mainboard, sideboard) where each is a list of (quantity, card_name).

    Handles::
        - Lines starting with '//' or '#' are treated as comments.
        - 'Deck' / 'deck' toggles mainboard section.
        - 'Sideboard' / 'sideboard' toggles sideboard section.
        - Set codes like '(OTJ) 042' are stripped from card names.
        - Blank lines are ignored.
    """
    mainboard: List[Tuple[int, str]] = []
    sideboard: List[Tuple[int, str]] = []
    current_section = 'main'

    with open(decklist_path, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('//') or line.startswith('#'):
                continue
            lower = line.lower()
            if lower == 'deck':
                current_section = 'main'
                continue
            if lower == 'sideboard':
                current_section = 'side'
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            try:
                quantity = int(parts[0])
            except ValueError:
                continue
            rest = parts[1]
            card_name = rest.split('(')[0].strip() if '(' in rest else rest.strip()
            if not card_name:
                continue
            if current_section == 'main':
                mainboard.append((quantity, card_name))
            else:
                sideboard.append((quantity, card_name))

    return mainboard, sideboard
