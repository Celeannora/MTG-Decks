#!/usr/bin/env python3
"""
MTG Decklist Validator (Local Mode)

Fast offline validation using the minimal local database.
Uses card_index.json pointer system for instant lookups without loading all CSVs.

Usage:
    # First, build the local database (one time)
    python scripts/build_local_database.py
    
    # Then validate decks offline
    python scripts/validate_decklist_local.py <path_to_decklist.txt>
    python scripts/validate_decklist_local.py Decks/2026-03-09_Orzhov_Lifegain/decklist.txt

Performance:
    - Loads ~300KB JSON index (instant)
    - No CSV parsing required
    - Validation completes in < 0.1 seconds
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class LocalDecklistValidator:
    def __init__(self, repo_root: Path, use_sqlite: bool = False):
        self.repo_root = repo_root
        self.local_db_dir = repo_root / "local_db"
        self.use_sqlite = use_sqlite
        
        # Load database
        if use_sqlite:
            self.load_sqlite_db()
        else:
            self.load_json_index()
    
    def load_json_index(self):
        """Load the lightweight JSON pointer index."""
        index_file = self.local_db_dir / "card_index.json"
        
        if not index_file.exists():
            print(f"❌ Error: Local database not found at {index_file}")
            print("\nPlease build the local database first:")
            print("  python scripts/build_local_database.py\n")
            sys.exit(1)
        
        print("Loading local database...")
        with open(index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.card_index = data['cards']
        self.total_cards = data['total_cards']
        
        print(f"✓ Loaded {self.total_cards:,} cards from local index\n")
    
    def load_sqlite_db(self):
        """Load the SQLite database (alternative to JSON)."""
        db_file = self.local_db_dir / "card_details.db"
        
        if not db_file.exists():
            print(f"❌ Error: SQLite database not found at {db_file}")
            print("\nPlease build the local database first:")
            print("  python scripts/build_local_database.py\n")
            sys.exit(1)
        
        print("Connecting to SQLite database...")
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        
        # Get total count
        self.cursor.execute("SELECT COUNT(*) FROM cards")
        self.total_cards = self.cursor.fetchone()[0]
        
        print(f"✓ Connected to database ({self.total_cards:,} cards)\n")
    
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
                parts = line.split(None, 1)
                if len(parts) < 2:
                    continue
                    
                try:
                    quantity = int(parts[0])
                    rest = parts[1]
                    
                    # Extract card name
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
    
    def validate_card_json(self, card_name: str) -> Tuple[bool, Optional[Dict]]:
        """Check if a card exists using JSON index."""
        normalized = card_name.lower()
        
        if normalized in self.card_index:
            return True, self.card_index[normalized]
        
        return False, None
    
    def validate_card_sqlite(self, card_name: str) -> Tuple[bool, Optional[Dict]]:
        """Check if a card exists using SQLite database."""
        normalized = card_name.lower()
        
        self.cursor.execute(
            "SELECT name, type_line, mana_cost, source_file FROM cards WHERE name_lower = ?",
            (normalized,)
        )
        
        result = self.cursor.fetchone()
        if result:
            return True, {
                'name': result[0],
                'type_line': result[1],
                'mana_cost': result[2],
                'file': result[3]
            }
        
        return False, None
    
    def validate_card(self, card_name: str) -> Tuple[bool, Optional[Dict]]:
        """Validate a card (dispatches to JSON or SQLite method)."""
        if self.use_sqlite:
            return self.validate_card_sqlite(card_name)
        else:
            return self.validate_card_json(card_name)
    
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
            is_valid, card_info = self.validate_card(card_name)
            if is_valid:
                print(f"✓ {quantity}x {card_name}")
                if card_info:
                    type_info = card_info.get('type_line', card_info.get('type', 'unknown'))
                    print(f"  └─ {type_info}")
                valid_mainboard += quantity
            else:
                print(f"❌ {quantity}x {card_name} - NOT FOUND IN DATABASE")
                illegal_cards.append((quantity, card_name, 'mainboard'))
        
        # Validate sideboard
        if sideboard:
            print("\n📋 SIDEBOARD VALIDATION\n")
            for quantity, card_name in sideboard:
                is_valid, card_info = self.validate_card(card_name)
                if is_valid:
                    print(f"✓ {quantity}x {card_name}")
                    if card_info:
                        type_info = card_info.get('type_line', card_info.get('type', 'unknown'))
                        print(f"  └─ {type_info}")
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
        print("Usage: python scripts/validate_decklist_local.py <path_to_decklist.txt>")
        print("Example: python scripts/validate_decklist_local.py Decks/2026-03-09_Orzhov_Lifegain/decklist.txt")
        print("\nOptions:")
        print("  --sqlite    Use SQLite database instead of JSON index")
        sys.exit(1)
    
    # Check for SQLite flag
    use_sqlite = '--sqlite' in sys.argv
    if use_sqlite:
        sys.argv.remove('--sqlite')
    
    # Determine repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    decklist_path = Path(sys.argv[1])
    if not decklist_path.is_absolute():
        decklist_path = repo_root / decklist_path
    
    validator = LocalDecklistValidator(repo_root, use_sqlite=use_sqlite)
    is_valid = validator.validate_decklist(decklist_path)
    
    # Close SQLite connection if used
    if use_sqlite and hasattr(validator, 'conn'):
        validator.conn.close()
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
