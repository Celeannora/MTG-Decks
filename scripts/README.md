# MTG Deck Builder Scripts

Utility scripts for maintaining the MTG deck builder system.

## fetch_standard_cards.py

### Purpose
Fetches current Standard-legal cards from Scryfall API and exports them in multiple formats for AI deck building reference.

### Features
- **API Integration**: Queries Scryfall's search API with `legal:standard` filter
- **Pagination Handling**: Automatically fetches all pages of results
- **Data Extraction**: Pulls only AI-relevant card data:
  - Name, mana cost, CMC
  - Type line and oracle text
  - Colors and color identity
  - Power/toughness (creatures)
  - Loyalty (planeswalkers)
  - Keywords and abilities
  - Set information
  - Rarity
- **Multi-Face Cards**: Properly handles split, modal, adventure, and transform cards
- **Deduplication**: Keeps most recent printing when multiple versions exist
- **Rate Limiting**: Respects Scryfall API guidelines

### Usage

```bash
# Run from repository root
python scripts/fetch_standard_cards.py

# Or make executable and run directly
chmod +x scripts/fetch_standard_cards.py
./scripts/fetch_standard_cards.py
```

### Output Files

The script generates three files in the current directory:

#### 1. `standard_cards.json` (AI-Optimized)
```json
{
  "metadata": {
    "format": "Standard",
    "last_updated": "2026-03-05T11:30:00.000000",
    "total_cards": 1500,
    "source": "Scryfall API"
  },
  "cards": [
    {
      "name": "Lightning Bolt",
      "mana_cost": "{R}",
      "cmc": 1,
      "type_line": "Instant",
      "oracle_text": "Lightning Bolt deals 3 damage to any target.",
      "colors": ["R"],
      "color_identity": ["R"],
      "keywords": [],
      "set": "M21",
      "set_name": "Core Set 2021",
      "rarity": "common",
      "collector_number": "153",
      "standard_legal": true
    }
  ]
}
```

**Use Case**: Primary reference for AI deck builder. Load this file to validate card legality and access card data.

#### 2. `standard_cards.txt` (Human-Readable)
Formatted text with full card details, one card per section:
```
Name: Lightning Bolt
Cost: {R} (CMC: 1)
Type: Instant
Text: Lightning Bolt deals 3 damage to any target.
Set: Core Set 2021 (M21) #153
Rarity: Common
Colors: R
```

**Use Case**: Quick reference for developers, browsing available cards.

#### 3. `standard_cards.csv` (Spreadsheet Analysis)
Comma-separated values with columns: name, mana_cost, cmc, type_line, oracle_text, colors, color_identity, rarity, set, set_name, collector_number, power, toughness, loyalty, keywords

**Use Case**: Import into Excel/Google Sheets for statistical analysis, filtering, or mass data operations.

### Integration with AI Deck Builder

1. **Run script before deck building**: `python scripts/fetch_standard_cards.py`
2. **Load JSON in deck builder**: Reference `standard_cards.json` for legality checks
3. **Update repository**: Commit updated card data when Standard rotation occurs

### When to Run

- **Standard Rotation**: Every fall when new sets rotate in/out
- **New Set Release**: When new Standard-legal sets are added
- **Before Deck Builds**: To ensure latest card pool
- **Manual Updates**: When Scryfall data may have changed

### Rate Limiting

Script includes 100ms delay between API requests to respect Scryfall's rate limits (10 requests/second). For ~1500 cards across ~15 pages, total runtime is approximately 2-3 seconds.

### Error Handling

Script gracefully handles:
- API connection failures
- Invalid JSON responses  
- Missing card data fields
- Network timeouts

Errors are printed to console; partial data is saved if fetching fails mid-process.

### Dependencies

```bash
pip install requests
```

No other external dependencies required. Uses Python standard library for JSON, CSV, and datetime operations.

### Future Enhancements

- [ ] Support for other formats (Pioneer, Modern, Commander)
- [ ] Incremental updates (only fetch new/changed cards)
- [ ] Card image URLs for visual reference
- [ ] Price data integration
- [ ] Mana curve analysis/statistics

---

**Maintained by**: Celeannora  
**Last Updated**: March 5, 2026  
**License**: MIT
