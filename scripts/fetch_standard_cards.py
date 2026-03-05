#!/usr/bin/env python3
"""
MTG Standard Card Data Fetcher (Bulk Data Optimized)
Uses Scryfall's bulk data API for efficient, complete card data retrieval
"""

import requests
import json
from datetime import datetime
from typing import List, Dict

class StandardCardFetcher:
    """Fetch and process Standard-legal MTG cards from Scryfall bulk data"""
    
    def __init__(self):
        self.bulk_data_url = "https://api.scryfall.com/bulk-data"
        self.cards = []
        
    def get_bulk_data_download_url(self) -> str:
        """Get the download URL for default cards bulk data"""
        print("Fetching bulk data information from Scryfall...")
        
        try:
            response = requests.get(self.bulk_data_url)
            response.raise_for_status()
            bulk_data = response.json()
            
            # Find the "Default Cards" bulk data type
            # This contains one entry per card (not per printing)
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
            
            # Parse the large JSON file
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
        
        # Handle split/modal cards
        card_faces = card.get('card_faces', [])
        
        # Basic card info
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
        
        # Add power/toughness for creatures
        if 'power' in card:
            relevant['power'] = card.get('power')
            relevant['toughness'] = card.get('toughness')
        
        # Add loyalty for planeswalkers
        if 'loyalty' in card:
            relevant['loyalty'] = card.get('loyalty')
        
        # Handle split/modal/adventure cards
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
        
        # Produced mana (for lands/mana rocks)
        if 'produced_mana' in card:
            relevant['produced_mana'] = card.get('produced_mana')
        
        # Legality confirmation
        relevant['standard_legal'] = card.get('legalities', {}).get('standard') == 'legal'
        
        return relevant
    
    def process_cards(self, raw_cards: List[Dict]) -> List[Dict]:
        """Process raw card data into AI-friendly format"""
        print("Processing card data...")
        processed = []
        
        for card in raw_cards:
            # Skip tokens, art cards, etc.
            if card.get('layout') in ['token', 'emblem', 'art_series']:
                continue
            
            # Skip digital-only cards if you want paper-legal only
            # if card.get('digital', False):
            #     continue
                
            card_name = card.get('name')
            if not card_name:
                continue
            
            relevant_data = self.extract_relevant_data(card)
            processed.append(relevant_data)
        
        # Sort alphabetically by name
        processed.sort(key=lambda x: x['name'])
        
        print(f"Processed {len(processed)} cards")
        return processed
    
    def export_json(self, cards: List[Dict], filename: str = "standard_cards.json"):
        """Export to JSON format"""
        output = {
            'metadata': {
                'format': 'Standard',
                'last_updated': datetime.utcnow().isoformat(),
                'total_cards': len(cards),
                'source': 'Scryfall Bulk Data API',
                'data_type': 'default_cards'
            },
            'cards': cards
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        file_size_mb = len(json.dumps(output)) / (1024 * 1024)
        print(f"Exported JSON: {filename} ({file_size_mb:.2f} MB)")
        return filename
    
    def export_text(self, cards: List[Dict], filename: str = "standard_cards.txt"):
        """Export to human-readable text format"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"MTG Standard Legal Cards\n")
            f.write(f"Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
            f.write(f"Total Cards: {len(cards)}\n")
            f.write(f"Source: Scryfall Bulk Data API\n")
            f.write("="*80 + "\n\n")
            
            for card in cards:
                f.write(f"Name: {card['name']}\n")
                f.write(f"Cost: {card['mana_cost']} (CMC: {card['cmc']})\n")
                f.write(f"Type: {card['type_line']}\n")
                
                if card.get('card_faces'):
                    for i, face in enumerate(card['card_faces'], 1):
                        f.write(f"  Face {i}: {face['name']} - {face['mana_cost']}\n")
                        f.write(f"    {face['type_line']}\n")
                        f.write(f"    {face['oracle_text']}\n")
                else:
                    f.write(f"Text: {card['oracle_text']}\n")
                
                if card.get('power'):
                    f.write(f"P/T: {card['power']}/{card['toughness']}\n")
                if card.get('loyalty'):
                    f.write(f"Loyalty: {card['loyalty']}\n")
                
                f.write(f"Set: {card['set_name']} ({card['set']}) #{card['collector_number']}\n")
                f.write(f"Rarity: {card['rarity'].capitalize()}\n")
                f.write(f"Colors: {', '.join(card['colors']) if card['colors'] else 'Colorless'}\n")
                
                if card.get('keywords'):
                    f.write(f"Keywords: {', '.join(card['keywords'])}\n")
                
                f.write("\n" + "-"*80 + "\n\n")
        
        print(f"Exported TXT: {filename}")
        return filename
    
    def export_csv(self, cards: List[Dict], filename: str = "standard_cards.csv"):
        """Export to CSV format for spreadsheet analysis"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['name', 'mana_cost', 'cmc', 'type_line', 'oracle_text', 
                         'colors', 'color_identity', 'rarity', 'set', 'set_name', 
                         'collector_number', 'power', 'toughness', 'loyalty', 'keywords']
            
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for card in cards:
                row = card.copy()
                # Convert lists to strings for CSV
                row['colors'] = ','.join(row.get('colors', []))
                row['color_identity'] = ','.join(row.get('color_identity', []))
                row['keywords'] = ','.join(row.get('keywords', []))
                # Remove card_faces for CSV simplicity
                row.pop('card_faces', None)
                row.pop('standard_legal', None)
                writer.writerow(row)
        
        print(f"Exported CSV: {filename}")
        return filename
    
    def run(self):
        """Main execution method"""
        print("="*80)
        print("MTG Standard Card Data Fetcher (Bulk Data API)")
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
        
        # Process cards
        processed_cards = self.process_cards(standard_cards)
        
        print()
        
        # Export all formats
        json_file = self.export_json(processed_cards)
        txt_file = self.export_text(processed_cards)
        csv_file = self.export_csv(processed_cards)
        
        print()
        print("="*80)
        print("Export Complete!")
        print(f"JSON: {json_file} (AI-optimized)")
        print(f"TXT:  {txt_file} (Human-readable)")
        print(f"CSV:  {csv_file} (Spreadsheet analysis)")
        print("="*80)
        print()
        print("ADVANTAGES OF BULK DATA API:")
        print("✓ Single request instead of 15+ paginated requests")
        print("✓ Complete card data in one download (~100MB)")
        print("✓ No rate limiting concerns")
        print("✓ Updated daily by Scryfall")
        print("✓ Includes all card fields without filtering")
        print("="*80)


if __name__ == "__main__":
    fetcher = StandardCardFetcher()
    fetcher.run()
