#!/usr/bin/env python3
"""
MTG Standard Card Data Fetcher with Category Splitting
Splits large card database into smaller, AI-accessible category files
"""

import requests
import json
import csv
import os
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

class CategorizedCardFetcher:
    """Fetch and categorize Standard-legal MTG cards into manageable files"""
    
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
        
        relevant['standard_legal'] = card.get('legalities', {}).get('standard') == 'legal'
        
        return relevant
    
    def categorize_card(self, card: Dict) -> List[str]:
        """Determine which categories a card belongs to (can be multiple)"""
        categories = []
        type_line = card['type_line'].lower()
        oracle_text = card.get('oracle_text', '').lower()
        keywords = [k.lower() for k in card.get('keywords', [])]
        
        # Card types
        if 'creature' in type_line:
            categories.append('creatures')
            
            # Creature subtypes
            if 'angel' in type_line:
                categories.append('angels')
            if 'dragon' in type_line:
                categories.append('dragons')
            if 'vampire' in type_line:
                categories.append('vampires')
            if 'zombie' in type_line:
                categories.append('zombies')
            if 'elf' in type_line:
                categories.append('elves')
            if 'goblin' in type_line:
                categories.append('goblins')
            if 'merfolk' in type_line:
                categories.append('merfolk')
            if 'human' in type_line:
                categories.append('humans')
        
        if 'instant' in type_line:
            categories.append('instants')
        
        if 'sorcery' in type_line:
            categories.append('sorceries')
        
        if 'enchantment' in type_line:
            categories.append('enchantments')
        
        if 'artifact' in type_line:
            categories.append('artifacts')
        
        if 'planeswalker' in type_line:
            categories.append('planeswalkers')
        
        if 'land' in type_line:
            categories.append('lands')
        
        # Mechanics and themes
        if 'gain' in oracle_text and 'life' in oracle_text:
            categories.append('lifegain')
        
        if 'mill' in oracle_text or 'library into' in oracle_text or 'graveyard from your library' in oracle_text:
            categories.append('mill')
        
        if 'draw' in oracle_text and 'card' in oracle_text:
            categories.append('card_draw')
        
        if 'counter target' in oracle_text:
            categories.append('counterspells')
        
        if ('destroy' in oracle_text or 'exile' in oracle_text or 
            'damage to target' in oracle_text or 'deals' in oracle_text):
            categories.append('removal')
        
        if 'flying' in keywords or 'flying' in oracle_text:
            categories.append('flying')
        
        if 'first strike' in keywords or 'double strike' in keywords:
            categories.append('first_strike')
        
        if 'lifelink' in keywords:
            categories.append('lifelink')
        
        if 'flash' in keywords:
            categories.append('flash')
        
        if 'haste' in keywords:
            categories.append('haste')
        
        if 'vigilance' in keywords:
            categories.append('vigilance')
        
        if 'trample' in keywords:
            categories.append('trample')
        
        # Color categories
        colors = card.get('colors', [])
        if not colors:
            categories.append('colorless')
        else:
            if 'W' in colors:
                categories.append('white')
            if 'U' in colors:
                categories.append('blue')
            if 'B' in colors:
                categories.append('black')
            if 'R' in colors:
                categories.append('red')
            if 'G' in colors:
                categories.append('green')
            
            if len(colors) > 1:
                categories.append('multicolor')
        
        # Rarity
        categories.append(f"rarity_{card['rarity']}")
        
        # CMC ranges
        cmc = card.get('cmc', 0)
        if cmc == 0:
            categories.append('cmc_0')
        elif cmc <= 2:
            categories.append('cmc_1_2')
        elif cmc <= 4:
            categories.append('cmc_3_4')
        elif cmc <= 6:
            categories.append('cmc_5_6')
        else:
            categories.append('cmc_7_plus')
        
        return categories
    
    def process_and_categorize(self, raw_cards: List[Dict]) -> Dict[str, List[Dict]]:
        """Process cards and organize into categories"""
        print("Processing and categorizing cards...")
        
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
            
            # Get categories for this card
            card_categories = self.categorize_card(processed)
            
            # Add to each category
            for category in card_categories:
                categorized[category].append(processed)
        
        # Sort each category alphabetically
        for category in categorized:
            categorized[category].sort(key=lambda x: x['name'])
        
        # Add "all" category
        all_processed.sort(key=lambda x: x['name'])
        categorized['all'] = all_processed
        
        print(f"Processed {len(all_processed)} cards into {len(categorized)} categories")
        return categorized
    
    def export_category_files(self, categorized: Dict[str, List[Dict]]):
        """Export each category to separate JSON and CSV files"""
        print("\nExporting category files...")
        
        metadata = {
            'format': 'Standard',
            'last_updated': datetime.utcnow().isoformat(),
            'source': 'Scryfall Bulk Data API',
        }
        
        category_stats = []
        
        for category, cards in categorized.items():
            # Skip empty categories
            if not cards:
                continue
            
            # JSON export
            json_filename = os.path.join(self.output_dir, f"{category}.json")
            json_data = {
                'metadata': {**metadata, 'category': category, 'total_cards': len(cards)},
                'cards': cards
            }
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            json_size_kb = os.path.getsize(json_filename) / 1024
            
            # CSV export
            csv_filename = os.path.join(self.output_dir, f"{category}.csv")
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
            
            category_stats.append({
                'category': category,
                'cards': len(cards),
                'json_size_kb': json_size_kb,
                'csv_size_kb': csv_size_kb
            })
        
        # Export category index
        self.export_category_index(category_stats)
        
        return category_stats
    
    def export_category_index(self, stats: List[Dict]):
        """Export an index file listing all categories"""
        index_file = os.path.join(self.output_dir, "_INDEX.md")
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# MTG Standard Cards - Category Index\n\n")
            f.write(f"Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
            f.write("This directory contains Standard-legal MTG cards split into manageable categories.\n")
            f.write("Each category has both JSON and CSV formats for easy parsing.\n\n")
            f.write("## File Size Benefits\n\n")
            f.write("- Original database: ~3MB JSON (too large for GitHub API)\n")
            f.write("- Category files: Typically 10-200KB (easily accessible)\n")
            f.write("- AI tools can load specific categories as needed\n\n")
            f.write("## Available Categories\n\n")
            
            # Sort by card count
            stats.sort(key=lambda x: x['cards'], reverse=True)
            
            f.write("| Category | Cards | JSON Size | CSV Size |\n")
            f.write("|----------|-------|-----------|----------|\n")
            
            for stat in stats:
                f.write(f"| {stat['category']} | {stat['cards']} | "
                       f"{stat['json_size_kb']:.1f} KB | {stat['csv_size_kb']:.1f} KB |\n")
            
            f.write("\n## Category Descriptions\n\n")
            f.write("### Card Types\n")
            f.write("- `creatures`, `instants`, `sorceries`, `enchantments`, `artifacts`, `planeswalkers`, `lands`\n\n")
            
            f.write("### Creature Tribes\n")
            f.write("- `angels`, `dragons`, `vampires`, `zombies`, `elves`, `goblins`, `merfolk`, `humans`\n\n")
            
            f.write("### Mechanics & Themes\n")
            f.write("- `lifegain`, `mill`, `card_draw`, `counterspells`, `removal`\n")
            f.write("- `flying`, `first_strike`, `lifelink`, `flash`, `haste`, `vigilance`, `trample`\n\n")
            
            f.write("### Colors\n")
            f.write("- `white`, `blue`, `black`, `red`, `green`, `colorless`, `multicolor`\n\n")
            
            f.write("### Rarity\n")
            f.write("- `rarity_common`, `rarity_uncommon`, `rarity_rare`, `rarity_mythic`\n\n")
            
            f.write("### CMC Ranges\n")
            f.write("- `cmc_0`, `cmc_1_2`, `cmc_3_4`, `cmc_5_6`, `cmc_7_plus`\n\n")
            
            f.write("### Special\n")
            f.write("- `all` - Complete Standard card pool\n\n")
            
            f.write("## Usage with AI\n\n")
            f.write("```python\n")
            f.write("# Example: Load only angels for an angel tribal deck\n")
            f.write("import json\n")
            f.write("with open('cards_by_category/angels.json') as f:\n")
            f.write("    data = json.load(f)\n")
            f.write("    angels = data['cards']\n")
            f.write("```\n")
        
        print(f"\nCategory index exported: {index_file}")
    
    def run(self):
        """Main execution method"""
        print("="*80)
        print("MTG Standard Card Data Fetcher with Category Splitting")
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
        print(f"Total Categories: {len(stats)}")
        print(f"\nTop 10 Largest Categories:")
        for stat in sorted(stats, key=lambda x: x['cards'], reverse=True)[:10]:
            print(f"  {stat['category']:20s}: {stat['cards']:4d} cards "
                  f"({stat['json_size_kb']:.1f} KB)")
        print("="*80)
        print()
        print("BENEFITS:")
        print("✓ Small files (<200KB each) easily accessible by AI")
        print("✓ Load only relevant categories for faster processing")
        print("✓ No GitHub API file size limitations")
        print("✓ Cards can appear in multiple categories")
        print("✓ Both JSON (structured) and CSV (spreadsheet) formats")
        print("="*80)


if __name__ == "__main__":
    fetcher = CategorizedCardFetcher()
    fetcher.run()
