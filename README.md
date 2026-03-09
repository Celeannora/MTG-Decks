# MTG Deck Repository

## 🛑 AI ASSISTANTS: STOP AND READ THIS FIRST 🛑

**Before building ANY deck, you MUST:**

1. ⚠️ **STOP** - Do not suggest cards yet
2. 📚 **READ** `AI_INSTRUCTIONS.md` - This is your ONLY authoritative instruction source
3. 📋 **LOAD DATABASE** - Open `cards_by_category directory/` CSV files  
4. ✓ **VERIFY EVERY CARD** - Check each card exists in loaded CSVs before adding
5. 🧪 **RUN VALIDATOR** - Execute `python scripts/validate_decklist.py` before finalizing

**Skipping these steps will generate illegal decks that waste everyone's time.**

📖 **Primary instruction file:** [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) - All other instruction files are deprecated.

---

## Overview

This repository contains rigorously analyzed, format-legal Magic: The Gathering decklists built through AI-assisted optimization. Every deck undergoes exhaustive mathematical and strategic analysis before publication.

**Repository status**: ✅ Fully self-sufficient — contains a complete Standard card database and AI deck-building instructions.

**Legality enforcement**: 🚨 STRICT — All cards must be verified against the database. Web sources are prohibited for card selection.

**Validation**: ✅ Automated validation script prevents illegal cards from entering the repository.

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
│   ├── creature/                   # creature_a1.csv, creature_a2.csv, ...
│   ├── instant/
│   ├── sorcery/
│   ├── artifact/
│   ├── enchantment/
│   ├── land/
│   ├── planeswalker/
│   └── other/
├── scripts/
│   ├── fetch_and_categorize_cards.py   # Regenerates card database from Scryfall
│   └── validate_decklist.py            # Validates decks against database (NEW)
├── AI_INSTRUCTIONS.md              # 🔴 SINGLE SOURCE OF TRUTH for AI deck building
├── Changelog.md
└── README.md
```

---

## Card database

All Standard-legal cards are stored in `cards_by_category directory/`, organized by type and split by first letter of card name:

- **Path format**: `cards_by_category directory/{type}/{type}_{letter}.csv`
- **Example**: Llanowar Elves (creature, starts with L) → `cards_by_category directory/creature/creature_l1.csv`
- **File size**: Each file targets ≤80KB for reliable GitHub API access
- **Index**: `cards_by_category directory/_INDEX.md` lists every file with card counts and sizes
- **Columns**: `name`, `mana_cost`, `cmc`, `type_line`, `oracle_text`, `colors`, `color_identity`, `rarity`, `set`, `set_name`, `collector_number`, `power`, `toughness`, `loyalty`, `keywords`

To update after Standard rotation or a new set release:
```bash
python scripts/fetch_and_categorize_cards.py
```

---

## Deck validation

### Automated Validation Script (NEW)

Validate any decklist against the database to ensure all cards are legal:

```bash
python scripts/validate_decklist.py Decks/2026-03-09_Orzhov_Lifegain/decklist.txt
```

**Output example:**

```
✅ VALIDATION PASSED
Mainboard: 60 cards validated  
Sideboard: 15 cards validated
All cards are legal and present in the database.
```

**Or if illegal cards detected:**

```
❌ VALIDATION FAILED
Found 3 illegal card(s):
  • 4x Thoughtseize (mainboard)
  • 2x Fatal Push (sideboard)
```

### Validation Requirements

Every deck MUST:

1. Pass automated validation before publication
2. Include validation results in `analysis.md`
3. Document which database CSV files were loaded
4. Provide per-card source file citations for key cards

---

## For AI assistants

### 🚨 Critical legality requirements

1. **Load database FIRST** - before selecting any cards
2. **Only use database cards** - never rely on web searches for card selection  
3. **Verify every card** - check each card individually against loaded CSVs
4. **Run validation script** - execute before finalizing deck
5. **Document verification** - list which CSV files you loaded in analysis.md
6. **Zero tolerance** - even one illegal card invalidates the entire deck

### Workflow

1. Read [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) for complete methodology
2. Open `cards_by_category directory/_INDEX.md` to understand database structure
3. Load specific letter files for card types you need (e.g., `creature/creature_l1.csv`)  
4. Build working list of available legal cards from loaded CSVs
5. Select cards ONLY from your loaded database list
6. Verify each card individually before adding to decklist
7. Run `python scripts/validate_decklist.py Decks/[deck_name]/decklist.txt`
8. Create database verification section in analysis.md
9. Save completed decks to `Decks/` with standard folder structure

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
4. **Automated validation**: `validate_decklist.py` script prevents illegal cards
5. **Documentation required**: Analysis must include database verification section
6. **Rejection policy**: Decks with illegal cards are invalid and rejected

### Example verification section

Every `analysis.md` must include:

```markdown
## Database Verification

### Files Loaded
- `cards_by_category directory/creature/creature_l1.csv`
- `cards_by_category directory/instant/instant_c.csv`  
- `cards_by_category directory/land/land_f2.csv`

### Legality Confirmation
✓ All 60 mainboard cards verified present in database
✓ All 15 sideboard cards verified present in database

### Representative Card Verification  
✓ Llanowar Elves - cards_by_category directory/creature/creature_l1.csv
✓ Counterspell - cards_by_category directory/instant/instant_c.csv
✓ Forest - cards_by_category directory/land/land_f2.csv

### Validation Script Result
```bash
$ python scripts/validate_decklist.py Decks/2026-03-09_Deck/decklist.txt
✅ VALIDATION PASSED
```
```

---

## Philosophy

Every card choice is mathematically justified. Every strategic decision is rigorously challenged. No deck is published without surviving brutal self-critique.

**Format legality is non-negotiable**. A brilliant deck with illegal cards is worthless.

**Failure is acceptable. Unjustified mediocrity is not. Illegal cards are unacceptable.**

---

**Maintained by**: Celeannora  
**Last updated**: March 9, 2026  
**Version**: 5.0 (Automated validation + consolidated instructions)  
**Powered by**: [Perplexity AI](https://www.perplexity.ai)
