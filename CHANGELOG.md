# MTG-Decks Repository Changelog

## March 7, 2026 - CSV-Only Migration

### Summary
Migrated repository to CSV-only format for optimal AI parsing and GitHub API compatibility.

### Changes Made

#### 1. Updated Fetcher Script
- **File**: `scripts/fetch_and_categorize_cards.py`
- **Change**: Removed JSON output, keeping only CSV generation
- **Benefit**: Simpler codebase, faster execution, smaller files
- **File sizes**: Target 400KB per file (vs. previous 800KB JSON target)

#### 2. Created Cleanup Script
- **File**: `scripts/cleanup_json_files.py`
- **Purpose**: Local utility to remove JSON files from `cards_by_category/`
- **Usage**: Run locally with `python scripts/cleanup_json_files.py`
- **Action**: Safely removes all .json files while preserving .csv files

#### 3. Created Decks Subfolder
- **Folder**: `Decks/`
- **Purpose**: Centralized location for all generated deck lists
- **Structure**: Each deck in dated subfolder (e.g., `2026-03-07_Archetype_Name/`)
- **Contents**: decklist.txt, analysis.md, sideboard_guide.md

#### 4. Updated AI Instructions
- **File**: `AI_DECK_BUILDER_INSTRUCTIONS.md`
- **Changes**:
  - Updated database references to point to `cards_by_category/` CSV files
  - Specified `Decks/` as mandatory save location for all generated decks
  - Removed JSON file references
  - Updated file size expectations (400KB per CSV)
  - Added category-based file structure explanation

### File Size Comparison

| Category | JSON Size | CSV Size | Savings |
|----------|-----------|----------|----------|
| creature_part1 | 1,085 KB | 433 KB | 60% |
| all_part1 | 1,088 KB | 438 KB | 60% |
| land_part1 | 1,176 KB | 279 KB | 76% |
| instant | 764 KB | 274 KB | 64% |
| sorcery | 688 KB | 285 KB | 59% |

**Average savings: 63%**

### Benefits

1. **Smaller Files**: CSV files are ~60% smaller than JSON
2. **GitHub API Compatible**: All files now under 500KB limit
3. **Easier Parsing**: Simple CSV format vs. nested JSON
4. **Faster Loading**: Less data to transfer and parse
5. **Better Organization**: Decks in dedicated subfolder

### Migration Notes

#### For Users with Local Clones
If you have JSON files locally:

```bash
# Navigate to repository
cd MTG-Decks

# Run cleanup script (interactive)
python scripts/cleanup_json_files.py

# Or manually remove JSON files
cd cards_by_category
rm *.json
```

#### For AI Assistants
- Load CSV files from `cards_by_category/` instead of JSON
- CSV files use standard format with header row
- Columns: name, mana_cost, cmc, type_line, oracle_text, colors, color_identity, rarity, set, set_name, collector_number, power, toughness, loyalty, keywords
- **Save all generated decks to `Decks/` subfolder**

### Remaining JSON Files (To Be Removed)

The following JSON files in `cards_by_category/` still need to be deleted:
- all_part1.json (DONE)
- all_part2.json through all_part10.json
- artifact.json
- creature_part1.json through creature_part5.json
- enchantment.json
- instant.json
- land_part1.json through land_part3.json
- other.json
- planeswalker.json
- sorcery.json

**Action Required**: Run cleanup script locally or manually delete via GitHub web interface.

### Next Steps

1. Complete JSON file cleanup
2. Test card search functionality with CSV files
3. Generate sample deck using new structure
4. Verify all decks save to `Decks/` folder correctly

---

## Previous Updates

### March 5, 2026 - Initial Repository Setup
- Created card database fetch scripts
- Added AI deck builder instructions
- Populated initial Standard card database
