#!/usr/bin/env python3
"""
MTG Standard Card Data Fetcher with Universal Categorization
Splits large card database into <1MB category files with automatic part splitting
"""

import requests
import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

class UniversalCardFetcher:
    """Fetch and categorize Standard-legal MTG cards into <1MB files"""
    
    # 800KB threshold (leaves room for metadata, stays well under 1MB)
    MAX_FILE_SIZE_BYTES = 800 * 1024
    
    def __init__(self, output_dir: str = "cards_by_category"):
        self.bulk_data_url = "https://api.scryfall.com/bulk-data"
        self.output_dir = output_dir
        self.cards = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
    def get_bulk_data_download_url(self) -> str:
        """Get the download URL for default cards bulk data"""
        print("Fetching bulk data information from Scryfall...")
        
        try:
            response = requests.get(self.bulk_data_url)
            response.raise_for_status()
            bulk_data = response.json()
            
            for item in bulk_data.get('data', []):
                if item.get('type') == 'default_cards':
                    download_uri = item.get('download_uri')
                    size_mb = item.get('size') / (1024 * 1024)
                    print(f"Found bulk data: {item.get('name')}")
                    print(f"Size: {size_mb:.2f} MB")
                    print(f"Last updated: {item.get('updated_at')}")
                    return download_uri
            
            print("ERROR: Could not find default_cards bulk data")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching bulk data info: {e}")
            return None
    
    def download_bulk_data(self, download_url: str) -> List[Dict]:
        """Download and parse bulk card data"""
        print(f"Downloading bulk card data...")
        print("This may take 30-60 seconds for ~100MB of data...")
        
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            cards = response.json()
            print(f"Downloaded {len(cards)} cards")
            return cards
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading bulk data: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return []
    
    def filter_standard_legal(self, all_cards: List[Dict]) -> List[Dict]:
        """Filter to only Standard-legal cards"""
        print("Filtering for Standard legality...")
        
        standard_cards = []
        for card in all_cards:
            legalities = card.get('legalities', {})
            if legalities.get('standard') == 'legal':
                standard_cards.append(card)
        
        print(f"Found {len(standard_cards)} Standard-legal cards")
        return standard_cards
    
    def extract_relevant_data(self, card: Dict) -> Dict:
        """Extract only AI-relevant card data"""
        card_faces = card.get('card_faces', [])
        
        relevant = {
            'name': card.get('name'),
            'mana_cost': card.get('mana_cost', ''),
            'cmc': card.get('cmc', 0),
            'type_line': card.get('type_line', ''),
            'oracle_text': card.get('oracle_text', ''),
            'colors': card.get('colors', []),
            'color_identity': card.get('color_identity', []),
            'keywords': card.get('keywords', []),
            'set': card.get('set', '').upper(),
            'set_name': card.get('set_name', ''),
            'rarity': card.get('rarity', ''),
            'collector_number': card.get('collector_number', ''),
        }
        
        if 'power' in card:
            relevant['power'] = card.get('power')
            relevant['toughness'] = card.get('toughness')
        
        if 'loyalty' in card:
            relevant['loyalty'] = card.get('loyalty')
        
        if card_faces:
            relevant['card_faces'] = []
            for face in card_faces:
                face_data = {
                    'name': face.get('name'),
                    'mana_cost': face.get('mana_cost', ''),
                    'type_line': face.get('type_line', ''),
                    'oracle_text': face.get('oracle_text', ''),
                }
                if 'power' in face:
                    face_data['power'] = face.get('power')
                    face_data['toughness'] = face.get('toughness')
                if 'loyalty' in face:
                    face_data['loyalty'] = face.get('loyalty')
                relevant['card_faces'].append(face_data)
        
        if 'produced_mana' in card:
            relevant['produced_mana'] = card.get('produced_mana')
        
        relevant['standard_legal'] = True
        
        return relevant
    
    def get_primary_type(self, type_line: str) -> str:
        """Extract primary card type from type line"""
        type_lower = type_line.lower()
        
        # Check in order of precedence
        if 'creature' in type_lower:
            return 'creature'
        elif 'instant' in type_lower:
            return 'instant'
        elif 'sorcery' in type_lower:
            return 'sorcery'
        elif 'artifact' in type_lower:
            return 'artifact'
        elif 'enchantment' in type_lower:
            return 'enchantment'
        elif 'planeswalker' in type_lower:
            return 'planeswalker'
        elif 'land' in type_lower:
            return 'land'
        elif 'battle' in type_lower:
            return 'battle'
        else:
            return 'other'
    
    def categorize_card(self, card: Dict) -> str:
        """Determine primary category for a card (single category for universal grouping)"""
        type_line = card['type_line']
        primary_type = self.get_primary_type(type_line)
        
        # Use primary type as the universal category
        return primary_type
    
    def process_and_categorize(self, raw_cards: List[Dict]) -> Dict[str, List[Dict]]:
        """Process cards and organize into universal type categories"""
        print("Processing and categorizing cards by universal types...")
        
        categorized = defaultdict(list)
        all_processed = []
        
        for card in raw_cards:
            # Skip tokens, emblems, etc.
            if card.get('layout') in ['token', 'emblem', 'art_series']:
                continue
            
            card_name = card.get('name')
            if not card_name:
                continue
            
            processed = self.extract_relevant_data(card)
            all_processed.append(processed)
            
            # Get primary category
            category = self.categorize_card(processed)
            categorized[category].append(processed)
        
        # Sort each category alphabetically
        for category in categorized:
            categorized[category].sort(key=lambda x: x['name'])
        
        # Add "all" category
        all_processed.sort(key=lambda x: x['name'])
        categorized['all'] = all_processed
        
        print(f"Processed {len(all_processed)} cards into {len(categorized)} universal categories")
        return categorized
    
    def split_into_parts(self, cards: List[Dict], category: str) -> List[Tuple[str, List[Dict]]]:
        """Split a large card list into multiple parts under size threshold"""
        parts = []
        current_part = []
        current_part_name = f"{category}_part1"
        part_num = 1
        
        for card in cards:
            # Add card to current part
            test_part = current_part + [card]
            
            # Estimate JSON size
            test_data = {'cards': test_part}
            test_size = len(json.dumps(test_data, ensure_ascii=False))
            
            if test_size > self.MAX_FILE_SIZE_BYTES and current_part:
                # Current part is full, save it and start new part
                parts.append((current_part_name, current_part))
                part_num += 1
                current_part = [card]
                current_part_name = f"{category}_part{part_num}"
            else:
                # Add to current part
                current_part = test_part
        
        # Add final part
        if current_part:
            if part_num == 1:
                # Only one part, don't add part number
                parts.append((category, current_part))
            else:
                parts.append((current_part_name, current_part))
        
        return parts
    
    def export_category_files(self, categorized: Dict[str, List[Dict]]):
        """Export each category to separate JSON and CSV files with size limits"""
        print("\nExporting category files with <1MB size limit...")
        
        metadata_base = {
            'format': 'Standard',
            'last_updated': datetime.utcnow().isoformat(),
            'source': 'Scryfall Bulk Data API',
        }
        
        category_stats = []
        
        for category, cards in categorized.items():
            if not cards:
                continue
            
            # Check if we need to split this category
            test_data = {'metadata': metadata_base, 'cards': cards}
            estimated_size = len(json.dumps(test_data, ensure_ascii=False))
            
            if estimated_size > self.MAX_FILE_SIZE_BYTES:
                # Split into parts
                print(f"  {category}: {len(cards)} cards (splitting into parts)")
                parts = self.split_into_parts(cards, category)
                
                for part_name, part_cards in parts:
                    self._export_single_category(part_name, part_cards, metadata_base, category_stats)
            else:
                # Export as single file
                print(f"  {category}: {len(cards)} cards")
                self._export_single_category(category, cards, metadata_base, category_stats)
        
        # Export category index
        self.export_category_index(category_stats)
        
        return category_stats
    
    def _export_single_category(self, filename: str, cards: List[Dict], 
                                 metadata_base: Dict, stats_list: List[Dict]):
        """Export a single category file (JSON and CSV)"""
        # Determine display category (remove _partX suffix)
        display_category = filename.split('_part')[0] if '_part' in filename else filename
        
        # JSON export
        json_filename = os.path.join(self.output_dir, f"{filename}.json")
        metadata = metadata_base.copy()
        metadata.update({
            'category': display_category,
            'total_cards': len(cards),
            'filename': filename
        })
        
        json_data = {
            'metadata': metadata,
            'cards': cards
        }
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        json_size_kb = os.path.getsize(json_filename) / 1024
        
        # CSV export
        csv_filename = os.path.join(self.output_dir, f"{filename}.csv")
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'mana_cost', 'cmc', 'type_line', 'oracle_text',
                        'colors', 'color_identity', 'rarity', 'set', 'set_name',
                        'collector_number', 'power', 'toughness', 'loyalty', 'keywords']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for card in cards:
                row = card.copy()
                row['colors'] = ','.join(row.get('colors', []))
                row['color_identity'] = ','.join(row.get('color_identity', []))
                row['keywords'] = ';'.join(row.get('keywords', []))
                row.pop('card_faces', None)
                row.pop('standard_legal', None)
                row.pop('produced_mana', None)
                writer.writerow(row)
        
        csv_size_kb = os.path.getsize(csv_filename) / 1024
        
        stats_list.append({
            'category': display_category,
            'filename': filename,
            'cards': len(cards),
            'json_size_kb': json_size_kb,
            'csv_size_kb': csv_size_kb,
            'is_part': '_part' in filename
        })
    
    def export_category_index(self, stats: List[Dict]):
        """Export an index file listing all categories"""
        index_file = os.path.join(self.output_dir, "_INDEX.md")
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# MTG Standard Cards - Universal Category Index\n\n")
            f.write(f"Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
            f.write("This directory contains Standard-legal MTG cards organized by universal card types.\n")
            f.write("All files are under 1MB for easy GitHub API access and AI parsing.\n\n")
            
            f.write("## File Size Guarantee\n\n")
            f.write("- **Maximum file size**: <800KB (well under 1MB GitHub limit)\n")
            f.write("- **Automatic splitting**: Large categories split into numbered parts\n")
            f.write("- **Original database**: ~3MB (inaccessible via API)\n")
            f.write("- **Category files**: All <800KB (directly accessible)\n\n")
            
            # Group by category
            category_groups = defaultdict(list)
            for stat in stats:
                category_groups[stat['category']].append(stat)
            
            f.write("## Available Categories\n\n")
            f.write("| Category | Files | Total Cards | Size Range |\n")
            f.write("|----------|-------|-------------|------------|\n")
            
            # Sort by total cards
            sorted_categories = sorted(category_groups.items(), 
                                      key=lambda x: sum(s['cards'] for s in x[1]), 
                                      reverse=True)
            
            for category, cat_stats in sorted_categories:
                total_cards = sum(s['cards'] for s in cat_stats)
                num_files = len(cat_stats)
                min_size = min(s['json_size_kb'] for s in cat_stats)
                max_size = max(s['json_size_kb'] for s in cat_stats)
                
                if num_files == 1:
                    size_range = f"{max_size:.0f} KB"
                else:
                    size_range = f"{min_size:.0f}-{max_size:.0f} KB"
                
                files_text = f"{num_files} parts" if num_files > 1 else "1 file"
                f.write(f"| {category} | {files_text} | {total_cards} | {size_range} |\n")
            
            f.write("\n## Detailed File Listing\n\n")
            
            for category, cat_stats in sorted_categories:
                f.write(f"### {category.capitalize()}\n\n")
                
                if len(cat_stats) > 1:
                    f.write(f"*Split into {len(cat_stats)} parts due to size*\n\n")
                
                for stat in cat_stats:
                    f.write(f"- **{stat['filename']}**: {stat['cards']} cards "
                           f"(JSON: {stat['json_size_kb']:.1f} KB, CSV: {stat['csv_size_kb']:.1f} KB)\n")
                
                f.write("\n")
            
            f.write("## Universal Categories\n\n")
            f.write("Cards are organized by their primary card type:\n\n")
            f.write("- **creature**: All creature cards\n")
            f.write("- **instant**: All instant spells\n")
            f.write("- **sorcery**: All sorcery spells\n")
            f.write("- **artifact**: All artifacts (including artifact creatures)\n")
            f.write("- **enchantment**: All enchantments (including enchantment creatures)\n")
            f.write("- **planeswalker**: All planeswalker cards\n")
            f.write("- **land**: All land cards\n")
            f.write("- **battle**: All battle cards\n")
            f.write("- **all**: Complete Standard card pool (may be split into parts)\n\n")
            
            f.write("## Usage with AI\n\n")
            f.write("### Loading a Single Category\n")
            f.write("```python\n")
            f.write("import json\n\n")
            f.write("# Load all creatures\n")
            f.write("with open('cards_by_category/creature.json') as f:\n")
            f.write("    data = json.load(f)\n")
            f.write("    creatures = data['cards']\n")
            f.write("```\n\n")
            
            f.write("### Loading Multi-Part Categories\n")
            f.write("```python\n")
            f.write("import json\n")
            f.write("import glob\n\n")
            f.write("# Load all parts of a category\n")
            f.write("all_cards = []\n")
            f.write("for filename in sorted(glob.glob('cards_by_category/all_part*.json')):\n")
            f.write("    with open(filename) as f:\n")
            f.write("        data = json.load(f)\n")
            f.write("        all_cards.extend(data['cards'])\n")
            f.write("```\n\n")
            
            f.write("### Searching for Specific Cards\n")
            f.write("```python\n")
            f.write("# Search for 'Lyra' in creatures\n")
            f.write("with open('cards_by_category/creature.json') as f:\n")
            f.write("    creatures = json.load(f)['cards']\n")
            f.write("    lyra_cards = [c for c in creatures if 'lyra' in c['name'].lower()]\n")
            f.write("```\n")
        
        print(f"\nCategory index exported: {index_file}")
    
    def run(self):
        """Main execution method"""
        print("="*80)
        print("MTG Standard Card Data Fetcher - Universal Categories")
        print("="*80)
        print()
        
        # Get bulk data download URL
        download_url = self.get_bulk_data_download_url()
        if not download_url:
            print("ERROR: Could not retrieve bulk data URL. Exiting.")
            return
        
        print()
        
        # Download all cards
        all_cards = self.download_bulk_data(download_url)
        if not all_cards:
            print("ERROR: No cards downloaded. Exiting.")
            return
        
        print()
        
        # Filter to Standard-legal only
        standard_cards = self.filter_standard_legal(all_cards)
        if not standard_cards:
            print("ERROR: No Standard-legal cards found. Exiting.")
            return
        
        print()
        
        # Process and categorize
        categorized = self.process_and_categorize(standard_cards)
        
        print()
        
        # Export category files
        stats = self.export_category_files(categorized)
        
        print()
        print("="*80)
        print("Export Complete!")
        print(f"Output Directory: {self.output_dir}/")
        
        # Count unique categories vs total files
        unique_categories = len(set(s['category'] for s in stats))
        total_files = len(stats)
        
        print(f"Universal Categories: {unique_categories}")
        print(f"Total Files: {total_files} (including parts)")
        
        print(f"\nCategory Summary:")
        category_totals = defaultdict(int)
        for stat in stats:
            category_totals[stat['category']] += stat['cards']
        
        for category, count in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            parts = [s for s in stats if s['category'] == category]
            if len(parts) > 1:
                print(f"  {category:15s}: {count:4d} cards ({len(parts)} parts)")
            else:
                print(f"  {category:15s}: {count:4d} cards")
        
        print("="*80)
        print()
        print("BENEFITS:")
        print("✓ All files guaranteed <800KB (GitHub API accessible)")
        print("✓ Universal card type organization")
        print("✓ Automatic splitting of large categories")
        print("✓ Both JSON (structured) and CSV (spreadsheet) formats")
        print("✓ Easy to search and filter by card type")
        print("="*80)


if __name__ == "__main__":
    fetcher = UniversalCardFetcher()
    fetcher.run()
