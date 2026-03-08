#!/usr/bin/env python3
"""
MTG Standard Card Data Fetcher - CSV-Only Version
Splits large card database into <400KB CSV files for optimal GitHub API access
"""

import requests
import csv
import os
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

class UniversalCardFetcher:
    """Fetch and categorize Standard-legal MTG cards into CSV files"""
    
    # 400KB threshold (stays well under 1MB GitHub limit)
    MAX_FILE_SIZE_BYTES = 400 * 1024
    
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
        except Exception as e:
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
        """Extract only AI-relevant card data for CSV"""
        relevant = {
            'name': card.get('name', ''),
            'mana_cost': card.get('mana_cost', ''),
            'cmc': card.get('cmc', 0),
            'type_line': card.get('type_line', ''),
            'oracle_text': card.get('oracle_text', ''),
            'colors': ','.join(card.get('colors', [])),
            'color_identity': ','.join(card.get('color_identity', [])),
            'keywords': ';'.join(card.get('keywords', [])),
            'set': card.get('set', '').upper(),
            'set_name': card.get('set_name', ''),
            'rarity': card.get('rarity', ''),
            'collector_number': card.get('collector_number', ''),
            'power': card.get('power', ''),
            'toughness': card.get('toughness', ''),
            'loyalty': card.get('loyalty', ''),
        }
        
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
        """Determine primary category for a card"""
        type_line = card['type_line']
        return self.get_primary_type(type_line)
    
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
    
    def estimate_csv_size(self, cards: List[Dict]) -> int:
        """Estimate CSV file size in bytes"""
        if not cards:
            return 0
        
        # Sample-based estimation
        sample_size = min(10, len(cards))
        sample_bytes = []
        
        for card in cards[:sample_size]:
            row_parts = []
            for key in ['name', 'mana_cost', 'cmc', 'type_line', 'oracle_text', 
                       'colors', 'color_identity', 'rarity', 'set', 'set_name',
                       'collector_number', 'power', 'toughness', 'loyalty', 'keywords']:
                value = str(card.get(key, ''))
                # CSV escaping
                if ',' in value or '"' in value or '\n' in value:
                    value = f'"{value.replace('"', '""')}"'
                row_parts.append(value)
            row_str = ','.join(row_parts) + '\n'
            sample_bytes.append(len(row_str.encode('utf-8')))
        
        avg_row_size = sum(sample_bytes) / len(sample_bytes)
        # Add header size
        header = 'name,mana_cost,cmc,type_line,oracle_text,colors,color_identity,rarity,set,set_name,collector_number,power,toughness,loyalty,keywords\n'
        header_size = len(header.encode('utf-8'))
        
        return int(avg_row_size * len(cards) + header_size)
    
    def split_into_parts(self, cards: List[Dict], category: str) -> List[Tuple[str, List[Dict]]]:
        """Split a large card list into multiple parts under size threshold"""
        estimated_size = self.estimate_csv_size(cards)
        
        if estimated_size <= self.MAX_FILE_SIZE_BYTES:
            return [(category, cards)]
        
        # Calculate number of parts needed
        num_parts = (estimated_size // self.MAX_FILE_SIZE_BYTES) + 1
        cards_per_part = len(cards) // num_parts + 1
        
        parts = []
        for i in range(num_parts):
            start_idx = i * cards_per_part
            end_idx = min((i + 1) * cards_per_part, len(cards))
            part_cards = cards[start_idx:end_idx]
            
            if part_cards:
                part_name = f"{category}_part{i+1}"
                parts.append((part_name, part_cards))
        
        return parts
    
    def write_csv_file(self, filename: str, cards: List[Dict]):
        """Write cards to CSV file"""
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        fieldnames = ['name', 'mana_cost', 'cmc', 'type_line', 'oracle_text',
                     'colors', 'color_identity', 'rarity', 'set', 'set_name',
                     'collector_number', 'power', 'toughness', 'loyalty', 'keywords']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cards)
        
        size_kb = os.path.getsize(filepath) / 1024
        return size_kb
    
    def export_category_files(self, categorized: Dict[str, List[Dict]]):
        """Export each category to CSV files with size limits"""
        print("\nExporting category CSV files with <400KB size limit...")
        
        category_stats = []
        
        for category, cards in categorized.items():
            if not cards:
                continue
            
            parts = self.split_into_parts(cards, category)
            
            if len(parts) > 1:
                print(f"  {category}: {len(cards)} cards ({len(parts)} parts)")
            else:
                print(f"  {category}: {len(cards)} cards")
            
            for filename, part_cards in parts:
                size_kb = self.write_csv_file(filename, part_cards)
                category_stats.append({
                    'category': category,
                    'filename': filename,
                    'cards': len(part_cards),
                    'size_kb': size_kb,
                    'is_part': '_part' in filename
                })
                print(f"    → {filename}.csv ({len(part_cards)} cards, {size_kb:.1f} KB)")
        
        # Export category index
        self.export_category_index(category_stats)
        
        return category_stats
    
    def export_category_index(self, stats: List[Dict]):
        """Export an index file listing all categories"""
        index_file = os.path.join(self.output_dir, "_INDEX.md")
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("# MTG Standard Cards - CSV Format\n\n")
            f.write(f"Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
            f.write("This directory contains Standard-legal MTG cards organized by universal card types.\n")
            f.write("All files are CSV format and under 400KB for optimal GitHub API access.\n\n")
            
            # Group by category
            category_groups = defaultdict(list)
            for stat in stats:
                category_groups[stat['category']].append(stat)
            
            f.write("## Available Categories\n\n")
            f.write("| Category | Files | Total Cards | Size Range |\n")
            f.write("|----------|-------|-------------|------------|\n")
            
            sorted_categories = sorted(category_groups.items(), 
                                      key=lambda x: sum(s['cards'] for s in x[1]), 
                                      reverse=True)
            
            for category, cat_stats in sorted_categories:
                total_cards = sum(s['cards'] for s in cat_stats)
                num_files = len(cat_stats)
                min_size = min(s['size_kb'] for s in cat_stats)
                max_size = max(s['size_kb'] for s in cat_stats)
                
                if num_files == 1:
                    size_range = f"{max_size:.0f} KB"
                else:
                    size_range = f"{min_size:.0f}-{max_size:.0f} KB"
                
                files_text = f"{num_files} parts" if num_files > 1 else "1 file"
                f.write(f"| {category} | {files_text} | {total_cards} | {size_range} |\n")
            
            f.write("\n## Detailed File Listing\n\n")
            
            for category, cat_stats in sorted_categories:
                f.write(f"### {category.capitalize()}\n\n")
                
                for stat in cat_stats:
                    f.write(f"- **{stat['filename']}.csv**: {stat['cards']} cards "
                           f"({stat['size_kb']:.1f} KB)\n")
                
                f.write("\n")
            
            f.write("## CSV Format\n\n")
            f.write("Each CSV file contains the following columns:\n\n")
            f.write("- `name`: Card name\n")
            f.write("- `mana_cost`: Mana cost\n")
            f.write("- `cmc`: Converted mana cost\n")
            f.write("- `type_line`: Full type line\n")
            f.write("- `oracle_text`: Card rules text\n")
            f.write("- `colors`: Card colors (comma-separated)\n")
            f.write("- `color_identity`: Color identity (comma-separated)\n")
            f.write("- `rarity`: Card rarity\n")
            f.write("- `set`: Set code\n")
            f.write("- `set_name`: Full set name\n")
            f.write("- `collector_number`: Collector number\n")
            f.write("- `power`: Creature power\n")
            f.write("- `toughness`: Creature toughness\n")
            f.write("- `loyalty`: Planeswalker loyalty\n")
            f.write("- `keywords`: Keywords (semicolon-separated)\n")
        
        print(f"\nCategory index exported: {index_file}")
    
    def run(self):
        """Main execution method"""
        print("="*80)
        print("MTG Standard Card Data Fetcher - CSV-Only")
        print("="*80)
        print()
        
        download_url = self.get_bulk_data_download_url()
        if not download_url:
            print("ERROR: Could not retrieve bulk data URL. Exiting.")
            return
        
        print()
        
        all_cards = self.download_bulk_data(download_url)
        if not all_cards:
            print("ERROR: No cards downloaded. Exiting.")
            return
        
        print()
        
        standard_cards = self.filter_standard_legal(all_cards)
        if not standard_cards:
            print("ERROR: No Standard-legal cards found. Exiting.")
            return
        
        print()
        
        categorized = self.process_and_categorize(standard_cards)
        
        print()
        
        stats = self.export_category_files(categorized)
        
        print()
        print("="*80)
        print("Export Complete!")
        print(f"Output Directory: {self.output_dir}/")
        print(f"Format: CSV only")
        
        unique_categories = len(set(s['category'] for s in stats))
        total_files = len(stats)
        
        print(f"Categories: {unique_categories}")
        print(f"Total Files: {total_files}")
        print("="*80)


if __name__ == "__main__":
    fetcher = UniversalCardFetcher()
    fetcher.run()
