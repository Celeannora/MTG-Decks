#!/usr/bin/env python3
"""
Build Local Database for Offline Validation

Creates a minimal database structure for local/offline deck validation:
1. card_index.json - Lightweight pointer system (~200-300KB)
2. card_names.txt - Simple text list of all legal card names (~100KB)
3. Optional: card_details.db - SQLite database for full card info (~800KB)

Total size: < 1MB for fast loading and offline use.

Usage:
    python scripts/build_local_database.py

Output:
    local_db/
    ├── card_index.json      # Pointer index: card_name -> file location
    ├── card_names.txt       # Simple list of all legal cards
    └── card_details.db      # SQLite DB with full card data (optional)
"""

import csv
import json
import sqlite3
import os
from pathlib import Path
from typing import Dict, List, Set


class LocalDatabaseBuilder:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.cards_dir = repo_root / "cards_by_category directory"
        self.output_dir = repo_root / "local_db"
        
        # Data structures
        self.card_index: Dict[str, Dict] = {}  # card_name_lower -> {name, type, file}
        self.card_names: Set[str] = set()
        
    def build(self):
        """Build all local database files."""
        print("Building local database for offline validation...\n")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Step 1: Scan all CSV files and build index
        print("[1/4] Scanning card database...")
        self.scan_database()
        
        # Step 2: Generate card_index.json (pointer system)
        print("[2/4] Creating card_index.json...")
        self.create_pointer_index()
        
        # Step 3: Generate card_names.txt (simple list)
        print("[3/4] Creating card_names.txt...")
        self.create_names_list()
        
        # Step 4: Generate SQLite database (optional, full data)
        print("[4/4] Creating card_details.db...")
        self.create_sqlite_db()
        
        self.print_summary()
        
    def scan_database(self):
        """Scan all CSV files and collect card information."""
        card_types = ['artifact', 'creature', 'enchantment', 'instant', 
                     'land', 'planeswalker', 'sorcery', 'other']
        
        total_files = 0
        total_cards = 0
        
        for card_type in card_types:
            type_dir = self.cards_dir / card_type
            if not type_dir.exists():
                continue
            
            for csv_file in sorted(type_dir.glob('*.csv')):
                total_files += 1
                file_rel_path = str(csv_file.relative_to(self.repo_root))
                
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            card_name = row['name'].strip()
                            card_name_lower = card_name.lower()
                            
                            # Add to names set
                            self.card_names.add(card_name)
                            
                            # Add to index (only store first occurrence)
                            if card_name_lower not in self.card_index:
                                self.card_index[card_name_lower] = {
                                    'name': card_name,
                                    'type': card_type,
                                    'file': file_rel_path,
                                    'mana_cost': row.get('mana_cost', ''),
                                    'type_line': row.get('type_line', '')
                                }
                            
                            total_cards += 1
                            
                except Exception as e:
                    print(f"  ⚠️  Warning: Could not read {csv_file.name}: {e}")
        
        print(f"  ✓ Scanned {total_files} files")
        print(f"  ✓ Found {len(self.card_index)} unique cards ({total_cards} total entries)\n")
        
    def create_pointer_index(self):
        """Create JSON index with pointers to source files."""
        output_file = self.output_dir / "card_index.json"
        
        # Create minimal index structure
        index_data = {
            'version': '1.0',
            'generated': '2026-03-09',
            'total_cards': len(self.card_index),
            'cards': self.card_index
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)
        
        file_size = output_file.stat().st_size
        print(f"  ✓ Created {output_file.name} ({file_size:,} bytes)\n")
        
    def create_names_list(self):
        """Create simple text file with all legal card names."""
        output_file = self.output_dir / "card_names.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for name in sorted(self.card_names):
                f.write(name + '\n')
        
        file_size = output_file.stat().st_size
        print(f"  ✓ Created {output_file.name} ({file_size:,} bytes)\n")
        
    def create_sqlite_db(self):
        """Create SQLite database with full card details."""
        output_file = self.output_dir / "card_details.db"
        
        # Remove existing database
        if output_file.exists():
            output_file.unlink()
        
        # Create new database
        conn = sqlite3.connect(output_file)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE cards (
                name TEXT PRIMARY KEY,
                name_lower TEXT,
                mana_cost TEXT,
                cmc REAL,
                type_line TEXT,
                oracle_text TEXT,
                colors TEXT,
                color_identity TEXT,
                rarity TEXT,
                set_code TEXT,
                set_name TEXT,
                collector_number TEXT,
                power TEXT,
                toughness TEXT,
                loyalty TEXT,
                keywords TEXT,
                card_type TEXT,
                source_file TEXT
            )
        ''')
        
        # Create index for fast lookups
        cursor.execute('CREATE INDEX idx_name_lower ON cards(name_lower)')
        cursor.execute('CREATE INDEX idx_type ON cards(card_type)')
        
        # Scan and insert all cards
        card_types = ['artifact', 'creature', 'enchantment', 'instant', 
                     'land', 'planeswalker', 'sorcery', 'other']
        
        inserted_cards = set()  # Track unique cards
        
        for card_type in card_types:
            type_dir = self.cards_dir / card_type
            if not type_dir.exists():
                continue
            
            for csv_file in sorted(type_dir.glob('*.csv')):
                file_rel_path = str(csv_file.relative_to(self.repo_root))
                
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            card_name = row['name'].strip()
                            card_name_lower = card_name.lower()
                            
                            # Only insert first occurrence of each unique card
                            if card_name_lower in inserted_cards:
                                continue
                            
                            inserted_cards.add(card_name_lower)
                            
                            cursor.execute('''
                                INSERT INTO cards VALUES (
                                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                )
                            ''', (
                                card_name,
                                card_name_lower,
                                row.get('mana_cost', ''),
                                float(row.get('cmc', 0)) if row.get('cmc') else None,
                                row.get('type_line', ''),
                                row.get('oracle_text', ''),
                                row.get('colors', ''),
                                row.get('color_identity', ''),
                                row.get('rarity', ''),
                                row.get('set', ''),
                                row.get('set_name', ''),
                                row.get('collector_number', ''),
                                row.get('power', ''),
                                row.get('toughness', ''),
                                row.get('loyalty', ''),
                                row.get('keywords', ''),
                                card_type,
                                file_rel_path
                            ))
                            
                except Exception as e:
                    print(f"  ⚠️  Warning: Could not process {csv_file.name}: {e}")
        
        conn.commit()
        conn.close()
        
        file_size = output_file.stat().st_size
        print(f"  ✓ Created {output_file.name} ({file_size:,} bytes)")
        print(f"  ✓ Inserted {len(inserted_cards)} unique cards\n")
        
    def print_summary(self):
        """Print summary of generated files."""
        print("=" * 70)
        print("\n📦 LOCAL DATABASE SUMMARY\n")
        
        total_size = 0
        for file in self.output_dir.glob('*'):
            size = file.stat().st_size
            total_size += size
            print(f"  {file.name:<25} {size:>10,} bytes")
        
        print(f"\n  {'Total size:':<25} {total_size:>10,} bytes")
        print(f"  {'Total size:':<25} {total_size / 1024:.1f} KB")
        print(f"  {'Total size:':<25} {total_size / (1024 * 1024):.2f} MB\n")
        
        print("✅ Local database created successfully!\n")
        print("Files created in: local_db/")
        print("  • card_index.json   - Fast pointer lookup (recommended)")
        print("  • card_names.txt    - Simple name list for grep/search")
        print("  • card_details.db   - Full SQLite database\n")


def main():
    # Determine repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    builder = LocalDatabaseBuilder(repo_root)
    builder.build()


if __name__ == "__main__":
    main()
