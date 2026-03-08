# MTG Deck Repository

## Overview

This repository contains rigorously analyzed, format-legal Magic: The Gathering decklists built through AI-assisted optimization. Every deck undergoes exhaustive mathematical and strategic analysis before publication.

**Repository status**: ✅ Fully self-sufficient — contains a complete Standard card database and AI deck-building instructions.

---

## Repository structure

```
MTG-Decks/
├── Decks/                          # All generated decks (never modify manually)
│   └── YYYY-MM-DD_Archetype_Name/
│       ├── decklist.txt            # MTGA-importable decklist
│       ├── analysis.md             # Card-by-card reasoning and strategy
│       └── sideboard_guide.md      # Matchup-specific boarding plans
├── card_data/                      # Standard card database (CSV, auto-generated)
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
│   └── fetch_and_categorize_cards.py   # Regenerates card_data/ from Scryfall
├── Deck_builder_instructions.md    # AI methodology and workflow
├── Deck_building_guidelines.md     # Quick reference for AI assistants
├── Rules_reference.md              # MTG rules reference
├── Changelog.md
└── README.md
```

---

## Card database

All Standard-legal cards are stored in `card_data/`, organized by type and split by first letter of card name:

- **Path format**: `card_data/{type}/{type}_{letter}.csv`
- **Example**: Hope Estheim (creature, starts with H) → `card_data/creature/creature_h.csv`
- **File size**: Each file targets ≤80KB for reliable GitHub API access
- **Index**: `card_data/_INDEX.md` lists every file with card counts and sizes
- **Columns**: `name`, `mana_cost`, `cmc`, `type_line`, `oracle_text`, `colors`, `color_identity`, `rarity`, `set`, `set_name`, `collector_number`, `power`, `toughness`, `loyalty`, `keywords`

To update after Standard rotation or a new set release:
```bash
python scripts/fetch_and_categorize_cards.py
```

---

## For AI assistants

1. Read `Deck_builder_instructions.md` for the full methodology
2. To look up a card: identify its type and first letter, load the matching file from `card_data/`
3. Use the `card_data/_INDEX.md` if you are unsure which file to open
4. Save all completed decks to `Decks/` with the standard folder structure

---

## For deck builders (human)

1. Browse `Decks/` organized by date and archetype
2. Import `decklist.txt` directly into MTG Arena
3. Read `analysis.md` for detailed card reasoning
4. Consult `sideboard_guide.md` for matchup strategies

---

## Formats supported

- **Standard** (default — full database support)
- Pioneer, Modern, Legacy, Vintage, Commander, Pauper, Historic, Explorer, Alchemy

Only Standard has full card database support. Other formats require manual legality verification.

---

## Philosophy

Every card choice is mathematically justified. Every strategic decision is rigorously challenged. No deck is published without surviving brutal self-critique.

**Failure is acceptable. Unjustified mediocrity is not.**

---

**Maintained by**: Celeannora  
**Last updated**: March 8, 2026  
**Version**: 3.0 (Letter-split card database)  
**Powered by**: [Perplexity AI](https://www.perplexity.ai)
