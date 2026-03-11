# MTG Deck Repository

## 🛑 AI ASSISTANTS: STOP AND READ THIS FIRST 🛑

**Before building ANY deck, you MUST:**

1. ⚠️ **STOP** - Do not suggest cards yet
2. 📚 **READ** `AI_INSTRUCTIONS.md` - Your ONLY authoritative instruction source
3. 📋 **LOAD DATABASE** - Open `cards_by_category/` CSV files
4. ✓ **VERIFY EVERY CARD** - Check each card exists in loaded CSVs before adding
5. 🧪 **RUN VALIDATOR** - Execute `python scripts/validate_decklist.py` before finalizing

**Skipping these steps will generate illegal decks.**

📖 **Primary instruction file:** [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) — All other instruction files are deprecated.

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
├── Decks/                           # All generated decks
│   └── YYYY-MM-DD_Archetype_Name/
│       ├── decklist.txt             # MTGA-importable decklist
│       ├── analysis.md              # Card-by-card reasoning and strategy
│       └── sideboard_guide.md       # Matchup-specific boarding plans
├── cards_by_category/               # Standard card database (CSV, auto-generated)
│   ├── _INDEX.md                    # File listing and lookup guide
│   ├── artifact/
│   ├── battle/
│   ├── creature/
│   ├── enchantment/
│   ├── instant/
│   ├── land/
│   ├── other/
│   ├── planeswalker/
│   └── sorcery/
├── scripts/
│   ├── fetch_and_categorize_cards.py  # Regenerates card database from Scryfall
│   ├── validate_decklist.py           # Online validator (uses cards_by_category/)
│   ├── validate_decklist_local.py     # Offline validator (uses local_db/)
│   ├── build_local_database.py        # Builds local_db/ for offline use
│   └── mtg_utils.py                   # Shared utilities (parser, etc.)
├── .github/DECK_TEMPLATE/           # Template for new decks
├── AI_INSTRUCTIONS.md               # 🔴 SINGLE SOURCE OF TRUTH for AI deck building
├── Changelog.md
├── requirements.txt
└── README.md
```

---

## Card database

All Standard-legal cards are stored in `cards_by_category/`, organized by type and split by first letter of card name:

- **Path format**: `cards_by_category/{type}/{type}_{letter}.csv`
- **Example**: Sheoldred, the Apocalypse (creature, S) → `cards_by_category/creature/creature_s1.csv`
- **File size**: Each file targets ≤80 KB for reliable GitHub API access
- **Index**: `cards_by_category/_INDEX.md` lists every file with card counts and sizes
- **Columns**: `name`, `mana_cost`, `cmc`, `type_line`, `oracle_text`, `colors`, `color_identity`, `rarity`, `set`, `set_name`, `collector_number`, `power`, `toughness`, `loyalty`, `produced_mana`, `keywords`

To update the database after a new set releases or Standard rotates:

```bash
python scripts/fetch_and_categorize_cards.py
```

---

## Deck validation

### Online validation (uses cards_by_category/ CSVs)

```bash
python scripts/validate_decklist.py Decks/2026-03-09_Orzhov_Lifegain/decklist.txt
```

### Offline validation (faster, uses pre-built local_db/)

```bash
# One-time setup
python scripts/build_local_database.py

# Then validate quickly
python scripts/validate_decklist_local.py Decks/2026-03-09_Orzhov_Lifegain/decklist.txt
```

### Validation flags

```bash
--quiet    # Summary only (good for CI/CD)
--verbose  # Print source CSV for each card
--sqlite   # (local validator only) Use SQLite DB instead of JSON index
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Illegal/unrecognised cards found |
| 2 | Decklist file not found |
| 3 | Count violation (wrong 60/15/4-copy counts) |

**Sample failure output:**

```
❌ VALIDATION FAILED
Found 2 illegal card(s):
  • 4x Thoughtseize (mainboard)
  • 2x Fatal Push (sideboard)
```

### Validation requirements

Every deck MUST:

1. Pass automated validation before publication
2. Include validation results in `analysis.md`
3. Document which database CSV files were loaded
4. Provide per-card source file citations for key cards

---

## For AI assistants

### 🚨 Critical legality requirements

1. **Load database FIRST** — before selecting any cards
2. **Only use database cards** — never rely on web searches for card selection
3. **Verify every card** — check each card individually against loaded CSVs
4. **Run validation script** — execute before finalizing deck
5. **Document verification** — list which CSV files you loaded in analysis.md
6. **Zero tolerance** — even one illegal card invalidates the entire deck

### Workflow

1. Read [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) for complete methodology
2. Open `cards_by_category/_INDEX.md` to understand database structure
3. Load specific letter files for card types you need
4. Build working list of available legal cards from loaded CSVs
5. Select cards ONLY from your loaded database list
6. Verify each card individually before adding to decklist
7. Run `python scripts/validate_decklist.py Decks/[deck_name]/decklist.txt`
8. Create database verification section in analysis.md
9. Save completed decks to `Decks/` with standard folder structure

**Never trust external sources for card legality** — the database is the only source of truth.

---

## For deck builders (human)

1. Browse `Decks/` organized by date and archetype
2. Import `decklist.txt` directly into MTG Arena
3. Read `analysis.md` for detailed card reasoning and database verification
4. Consult `sideboard_guide.md` for matchup strategies

---

## Formats supported

Only **Standard** has full card database support. All other formats require manual legality verification.

---

## Philosophy

Every card choice is mathematically justified. Every strategic decision is rigorously challenged. No deck is published without surviving brutal self-critique.

**Format legality is non-negotiable.** A brilliant deck with illegal cards is worthless.

---

**Maintained by**: Celeannora  
**Last updated**: March 10, 2026  
**Version**: 7.1
