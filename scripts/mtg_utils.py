#!/usr/bin/env python3
"""
Shared utilities for MTG deck building scripts.

Imported by validate_decklist.py and validate_decklist_local.py to avoid
code duplication.
"""

from pathlib import Path
from typing import List, Tuple


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
