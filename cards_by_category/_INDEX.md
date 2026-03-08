# MTG Standard Cards - Universal Category Index

Last Updated: 2026-03-08 06:13 UTC

This directory contains Standard-legal MTG cards organized by universal card types.
All files are under 1MB for easy GitHub API access and AI parsing.

## File Size Guarantee

- **Maximum file size**: <800KB (well under 1MB GitHub limit)
- **Automatic splitting**: Large categories split into numbered parts
- **Original database**: ~3MB (inaccessible via API)
- **Category files**: All <800KB (directly accessible)

## Available Categories

| Category | Files | Total Cards | Size Range |
|----------|-------|-------------|------------|
| all | 10 parts | 17070 | 831-1113 KB |
| creature | 5 parts | 6345 | 435-1065 KB |
| land | 3 parts | 6082 | 655-1155 KB |
| instant | 1 file | 1359 | 746 KB |
| sorcery | 1 file | 1101 | 672 KB |
| enchantment | 1 file | 1048 | 718 KB |
| artifact | 1 file | 1012 | 699 KB |
| planeswalker | 1 file | 103 | 89 KB |
| other | 1 file | 20 | 22 KB |

## Detailed File Listing

### All

*Split into 10 parts due to size*

- **all_part1**: 1561 cards (JSON: 1063.3 KB, CSV: 427.8 KB)
- **all_part2**: 1544 cards (JSON: 1057.7 KB, CSV: 413.6 KB)
- **all_part3**: 1961 cards (JSON: 1097.6 KB, CSV: 356.7 KB)
- **all_part4**: 1886 cards (JSON: 1100.9 KB, CSV: 355.9 KB)
- **all_part5**: 1556 cards (JSON: 1064.7 KB, CSV: 407.4 KB)
- **all_part6**: 2019 cards (JSON: 1113.1 KB, CSV: 338.2 KB)
- **all_part7**: 1856 cards (JSON: 1096.9 KB, CSV: 372.4 KB)
- **all_part8**: 1737 cards (JSON: 1078.0 KB, CSV: 399.1 KB)
- **all_part9**: 1775 cards (JSON: 1083.1 KB, CSV: 380.0 KB)
- **all_part10**: 1175 cards (JSON: 830.8 KB, CSV: 324.5 KB)

### Creature

*Split into 5 parts due to size*

- **creature_part1**: 1439 cards (JSON: 1060.1 KB, CSV: 423.0 KB)
- **creature_part2**: 1425 cards (JSON: 1061.9 KB, CSV: 410.6 KB)
- **creature_part3**: 1452 cards (JSON: 1064.6 KB, CSV: 427.4 KB)
- **creature_part4**: 1452 cards (JSON: 1059.9 KB, CSV: 423.9 KB)
- **creature_part5**: 577 cards (JSON: 435.3 KB, CSV: 178.1 KB)

### Land

*Split into 3 parts due to size*

- **land_part1**: 2395 cards (JSON: 1148.7 KB, CSV: 273.3 KB)
- **land_part2**: 2402 cards (JSON: 1154.6 KB, CSV: 268.9 KB)
- **land_part3**: 1285 cards (JSON: 655.1 KB, CSV: 175.6 KB)

### Instant

- **instant**: 1359 cards (JSON: 746.2 KB, CSV: 267.8 KB)

### Sorcery

- **sorcery**: 1101 cards (JSON: 672.1 KB, CSV: 278.1 KB)

### Enchantment

- **enchantment**: 1048 cards (JSON: 718.5 KB, CSV: 296.4 KB)

### Artifact

- **artifact**: 1012 cards (JSON: 698.9 KB, CSV: 303.2 KB)

### Planeswalker

- **planeswalker**: 103 cards (JSON: 89.1 KB, CSV: 47.9 KB)

### Other

- **other**: 20 cards (JSON: 22.1 KB, CSV: 1.8 KB)

## Universal Categories

Cards are organized by their primary card type:

- **creature**: All creature cards
- **instant**: All instant spells
- **sorcery**: All sorcery spells
- **artifact**: All artifacts (including artifact creatures)
- **enchantment**: All enchantments (including enchantment creatures)
- **planeswalker**: All planeswalker cards
- **land**: All land cards
- **battle**: All battle cards
- **all**: Complete Standard card pool (may be split into parts)

## Usage with AI

### Loading a Single Category
```python
import json

# Load all creatures
with open('cards_by_category/creature.json') as f:
    data = json.load(f)
    creatures = data['cards']
```

### Loading Multi-Part Categories
```python
import json
import glob

# Load all parts of a category
all_cards = []
for filename in sorted(glob.glob('cards_by_category/all_part*.json')):
    with open(filename) as f:
        data = json.load(f)
        all_cards.extend(data['cards'])
```

### Searching for Specific Cards
```python
# Search for 'Lyra' in creatures
with open('cards_by_category/creature.json') as f:
    creatures = json.load(f)['cards']
    lyra_cards = [c for c in creatures if 'lyra' in c['name'].lower()]
```
