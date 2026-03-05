#!/usr/bin/env python3
"""
MTG Standard Card Data Fetcher
Fetches all Standard-legal cards from Scryfall API and exports AI-relevant data
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict

class StandardCardFetcher:
    """Fetch and process Standard-legal MTG cards from Scryfall"""
    
    def __init__(self):
        self.api_base = "https://api.scryfall.com"
        self.cards = []
        
    def fetch_standard_cards(self) -> List[Dict]:
        """Fetch all Standard-legal cards using Scryfall bulk data"""
        print("Fetching Standard card list from Scryfall...")
        
        # Use Scryfall search API for Standard legality
        search_url = f"{self.api_base}/cards/search"
        params = {
            "q": "legal:standard",
            "format": "json",
            "unique": "prints"  # Get all printings for set info
        }
        
        all_cards = []
        has_more = True
        page = 1
        
        while has_more:
            print(f"Fetching page {page}...")
            try:
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                all_cards.extend(data.get('data', []))
                
                if data.get('has_more', False):
                    search_url = data.get('next_page')
                    params = {}  # Next page URL has params built in
                    has_more = True
                    page += 1
                    time.sleep(0.1)  # Rate limiting
                else:
                    has_more = False
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data: {e}")
                break
        
        print(f"Total cards fetched: {len(all_cards)}")
        return all_cards
    
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
        
        # Use dict to deduplicate by name (keep latest printing)
        card_dict = {}
        
        for card in raw_cards:
            # Skip tokens, art cards, etc.
            if card.get('layout') in ['token', 'emblem', 'art_series']:
                continue
                
            card_name = card.get('name')
            if not card_name:
                continue
            
            relevant_data = self.extract_relevant_data(card)
            
            # Keep the most recent printing (higher collector number usually = newer)
            if card_name not in card_dict:
                card_dict[card_name] = relevant_data
            else:
                # Prefer newer set or lower collector number for consistency
                existing_set = card_dict[card_name].get('set', '')
                new_set = relevant_data.get('set', '')
                if new_set >= existing_set:  # Alphabetically later set = newer
                    card_dict[card_name] = relevant_data
        
        processed = list(card_dict.values())
        processed.sort(key=lambda x: x['name'])
        
        print(f"Processed {len(processed)} unique cards")
        return processed
    
    def export_json(self, cards: List[Dict], filename: str = "standard_cards.json"):
        """Export to JSON format"""
        output = {
            'metadata': {
                'format': 'Standard',
                'last_updated': datetime.utcnow().isoformat(),
                'total_cards': len(cards),
                'source': 'Scryfall API'
            },
            'cards': cards
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"Exported JSON: {filename}")
        return filename
    
    def export_text(self, cards: List[Dict], filename: str = "standard_cards.txt"):
        """Export to human-readable text format"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"MTG Standard Legal Cards\n")
            f.write(f"Last Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
            f.write(f"Total Cards: {len(cards)}\n")
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
                writer.writerow(row)
        
        print(f"Exported CSV: {filename}")
        return filename
    
    def run(self):
        """Main execution method"""
        print("="*80)
        print("MTG Standard Card Data Fetcher")
        print("="*80)
        
        # Fetch cards
        raw_cards = self.fetch_standard_cards()
        
        if not raw_cards:
            print("ERROR: No cards fetched. Exiting.")
            return
        
        # Process cards
        processed_cards = self.process_cards(raw_cards)
        
        # Export all formats
        json_file = self.export_json(processed_cards)
        txt_file = self.export_text(processed_cards)
        csv_file = self.export_csv(processed_cards)
        
        print("\n" + "="*80)
        print("Export Complete!")
        print(f"JSON: {json_file} (AI-optimized)")
        print(f"TXT:  {txt_file} (Human-readable)")
        print(f"CSV:  {csv_file} (Spreadsheet analysis)")
        print("="*80)


if __name__ == "__main__":
    fetcher = StandardCardFetcher()
    fetcher.run()
