# MTG Deck Repository

## Overview

This repository contains rigorously analyzed, format-legal Magic: The Gathering decklists built through AI-assisted optimization. Every deck undergoes exhaustive mathematical and strategic analysis before publication.

**Repository status**: ✅ Fully self-sufficient — contains a complete Standard card database and AI deck-building instructions.

**Legality enforcement**: 🚨 STRICT — All cards must be verified against the database. Web sources are prohibited for card selection.

---

## Repository structure

```
MTG-Decks/
├── Decks/                          # All generated decks (never modify manually)
│   └── YYYY-MM-DD_Archetype_Name/
│       ├── decklist.txt            # MTGA-importable decklist
│       ├── analysis.md             # Card-by-card reasoning and strategy
│       └── sideboard_guide.md      # Matchup-specific boarding plans
├── cards_by_category directory/    # Standard card database (CSV, auto-generated)
│   ├── _INDEX.md                   # File listing and lookup guide
│   ├── creature/                   # creature_a.csv … creature_z.csv
│   ├── instant/
│   ├── sorcery/
│   ├── artifact/
│   ├── enchantment/
│   ├── land/
│   ├── planeswalker/
│   └── other/
├── scripts/
│   └── fetch_and_categorize_cards.py   # Regenerates card database from Scryfall
├── Deck_builder_instructions.md    # AI methodology and workflow
├── Deck_building_guidelines.md     # Quick reference for AI assistants
├── Rules_reference.md              # MTG rules reference
├── Changelog.md
└── README.md
```

---

## Card database

All Standard-legal cards are stored in `cards_by_category directory/`, organized by type and split by first letter of card name:

- **Path format**: `cards_by_category directory/{type}/{type}_{letter}.csv`
- **Example**: Llanowar Elves (creature, starts with L) → `cards_by_category directory/creature/creature_l.csv`
- **File size**: Each file targets ≤80KB for reliable GitHub API access
- **Index**: `cards_by_category directory/_INDEX.md` lists every file with card counts and sizes
- **Columns**: `name`, `mana_cost`, `cmc`, `type_line`, `oracle_text`, `colors`, `color_identity`, `rarity`, `set`, `set_name`, `collector_number`, `power`, `toughness`, `loyalty`, `keywords`

To update after Standard rotation or a new set release:
```bash
python scripts/fetch_and_categorize_cards.py
```

---

## For AI assistants

### 🚨 Critical legality requirements

1. **Load database FIRST** - before selecting any cards
2. **Only use database cards** - never rely on web searches for card selection
3. **Verify every card** - check each card individually against loaded CSVs
4. **Document verification** - list which CSV files you loaded in analysis.md
5. **Zero tolerance** - even one illegal card invalidates the entire deck

### Workflow

1. Read `Deck_builder_instructions.md` for the full methodology
2. Open `cards_by_category directory/_INDEX.md` to understand database structure
3. Load specific letter files for card types you need (e.g., `creature/creature_l.csv`)
4. Build working list of available legal cards from loaded CSVs
5. Select cards ONLY from your loaded database list
6. Verify each card individually before adding to decklist
7. Create database verification section in analysis.md
8. Save completed decks to `Decks/` with standard folder structure

**Never trust external sources for card legality** - the database is the only source of truth.

---

## For deck builders (human)

1. Browse `Decks/` organized by date and archetype
2. Import `decklist.txt` directly into MTG Arena
3. Read `analysis.md` for detailed card reasoning and database verification
4. Consult `sideboard_guide.md` for matchup strategies

---

## Formats supported

- **Standard** (default — full database support)
- Pioneer, Modern, Legacy, Vintage, Commander, Pauper, Historic, Explorer, Alchemy

Only Standard has full card database support. Other formats require manual legality verification.

---

## Legality enforcement

### Why strict enforcement matters

Web sources (articles, deck guides, forum posts) frequently contain rotated cards that are no longer Standard-legal. AIs can inadvertently include these cards if they rely on web searches instead of the database.

### How enforcement works

1. **Database-first methodology**: All cards must be selected from loaded CSV files
2. **No web search card selection**: External sources used for meta analysis only, not card selection
3. **Individual verification**: Every card checked against database before inclusion
4. **Documentation required**: Analysis must include database verification section
5. **Rejection policy**: Decks with illegal cards are invalid and rejected

### Example verification section

Every `analysis.md` must include:

```markdown
## Database Verification

### Files Loaded
- `cards_by_category directory/creature/creature_l.csv`
- `cards_by_category directory/instant/instant_c.csv`
- `cards_by_category directory/land/land_f.csv`

### Legality Confirmation
✓ All 60 mainboard cards verified present in database
✓ All 15 sideboard cards verified present in database

### Representative Card Verification
✓ Llanowar Elves - cards_by_category directory/creature/creature_l.csv
✓ Counterspell - cards_by_category directory/instant/instant_c.csv
✓ Forest - cards_by_category directory/land/land_f.csv
```

---

## Philosophy

Every card choice is mathematically justified. Every strategic decision is rigorously challenged. No deck is published without surviving brutal self-critique.

**Format legality is non-negotiable**. A brilliant deck with illegal cards is worthless.

**Failure is acceptable. Unjustified mediocrity is not. Illegal cards are unacceptable.**

---

**Maintained by**: Celeannora  
**Last updated**: March 9, 2026  
**Version**: 4.0 (Database-first legality enforcement)  
**Powered by**: [Perplexity AI](https://www.perplexity.ai)
