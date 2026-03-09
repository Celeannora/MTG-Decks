#!/usr/bin/env python3
"""
MTG Decklist Validator

Validates decklist.txt files against the cards_by_category directory database.
Ensures all cards are Standard-legal by verifying their presence in the CSV files.

Usage:
    python scripts/validate_decklist.py <path_to_decklist.txt>
    python scripts/validate_decklist.py Decks/2026-03-09_Orzhov_Lifegain/decklist.txt
"""

import sys
import csv
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple


class DecklistValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.card_database: Dict[str, List[Dict]] = {}
        self.load_database()

    def load_database(self):
        """Load all cards from the cards_by_category directory into memory."""
        cards_dir = self.repo_root / "cards_by_category directory"
        
        if not cards_dir.exists():
            print(f"❌ Error: Card database directory not found at {cards_dir}")
            sys.exit(1)

        print("Loading card database...")
        card_types = ['artifact', 'creature', 'enchantment', 'instant', 
                     'land', 'planeswalker', 'sorcery', 'other']
        
        for card_type in card_types:
            type_dir = cards_dir / card_type
            if not type_dir.exists():
                continue
                
            for csv_file in type_dir.glob('*.csv'):
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            card_name = row['name'].strip()
                            # Normalize card name for lookup (case-insensitive)
                            normalized_name = card_name.lower()
                            if normalized_name not in self.card_database:
                                self.card_database[normalized_name] = []
                            self.card_database[normalized_name].append({
                                'name': card_name,
                                'file': str(csv_file.relative_to(self.repo_root)),
                                'set': row.get('set', ''),
                                'type_line': row.get('type_line', '')
                            })
                except Exception as e:
                    print(f"⚠️  Warning: Could not read {csv_file}: {e}")
        
        print(f"✓ Loaded {len(self.card_database)} unique card names from database\n")

    def parse_decklist(self, decklist_path: Path) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
        """Parse a decklist.txt file and extract mainboard and sideboard cards."""
        if not decklist_path.exists():
            print(f"❌ Error: Decklist file not found at {decklist_path}")
            sys.exit(1)

        mainboard = []
        sideboard = []
        current_section = 'main'
        
        with open(decklist_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('//'):
                    continue
                    
                if line.lower() == 'deck':
                    current_section = 'main'
                    continue
                elif line.lower() == 'sideboard':
                    current_section = 'side'
                    continue
                
                # Parse card line: "4 Card Name (SET) Number"
                parts = line.split(None, 1)  # Split on first whitespace
                if len(parts) < 2:
                    continue
                    
                try:
                    quantity = int(parts[0])
                    rest = parts[1]
                    
                    # Extract card name (everything before the set code in parentheses)
                    if '(' in rest:
                        card_name = rest[:rest.index('(')].strip()
                    else:
                        card_name = rest.strip()
                    
                    if current_section == 'main':
                        mainboard.append((quantity, card_name))
                    else:
                        sideboard.append((quantity, card_name))
                        
                except (ValueError, IndexError):
                    continue
        
        return mainboard, sideboard

    def validate_card(self, card_name: str) -> Tuple[bool, str]:
        """Check if a card exists in the database."""
        normalized = card_name.lower()
        
        if normalized in self.card_database:
            entries = self.card_database[normalized]
            return True, entries[0]['file']
        
        return False, ""

    def validate_decklist(self, decklist_path: Path) -> bool:
        """Validate an entire decklist and print results."""
        print(f"Validating: {decklist_path}\n")
        print("=" * 70)
        
        mainboard, sideboard = self.parse_decklist(decklist_path)
        
        illegal_cards = []
        valid_mainboard = 0
        valid_sideboard = 0
        
        # Validate mainboard
        print("\n📋 MAINBOARD VALIDATION\n")
        for quantity, card_name in mainboard:
            is_valid, file_path = self.validate_card(card_name)
            if is_valid:
                print(f"✓ {quantity}x {card_name}")
                print(f"  └─ Found in: {file_path}")
                valid_mainboard += quantity
            else:
                print(f"❌ {quantity}x {card_name} - NOT FOUND IN DATABASE")
                illegal_cards.append((quantity, card_name, 'mainboard'))
        
        # Validate sideboard
        if sideboard:
            print("\n📋 SIDEBOARD VALIDATION\n")
            for quantity, card_name in sideboard:
                is_valid, file_path = self.validate_card(card_name)
                if is_valid:
                    print(f"✓ {quantity}x {card_name}")
                    print(f"  └─ Found in: {file_path}")
                    valid_sideboard += quantity
                else:
                    print(f"❌ {quantity}x {card_name} - NOT FOUND IN DATABASE")
                    illegal_cards.append((quantity, card_name, 'sideboard'))
        
        # Summary
        print("\n" + "=" * 70)
        print("\n📊 VALIDATION SUMMARY\n")
        print(f"Mainboard: {valid_mainboard} cards validated")
        if sideboard:
            print(f"Sideboard: {valid_sideboard} cards validated")
        
        if illegal_cards:
            print(f"\n❌ VALIDATION FAILED\n")
            print(f"Found {len(illegal_cards)} illegal card(s):\n")
            for quantity, card_name, section in illegal_cards:
                print(f"  • {quantity}x {card_name} ({section})")
            print("\n🚨 This deck contains cards not present in the database.")
            print("   These cards are either rotated or not Standard-legal.\n")
            return False
        else:
            print(f"\n✅ VALIDATION PASSED\n")
            print("All cards are legal and present in the database.\n")
            return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_decklist.py <path_to_decklist.txt>")
        print("Example: python scripts/validate_decklist.py Decks/2026-03-09_Orzhov_Lifegain/decklist.txt")
        sys.exit(1)
    
    # Determine repository root (assumes script is in scripts/ directory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    decklist_path = Path(sys.argv[1])
    if not decklist_path.is_absolute():
        decklist_path = repo_root / decklist_path
    
    validator = DecklistValidator(repo_root)
    is_valid = validator.validate_decklist(decklist_path)
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
