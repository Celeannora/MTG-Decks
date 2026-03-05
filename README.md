# MTG Deck Repository

## Overview
This repository contains rigorously analyzed, format-legal Magic: The Gathering decklists built through AI-assisted optimization. Every deck undergoes exhaustive mathematical and strategic analysis before publication.

**Repository Status**: ✅ **Fully Self-Sufficient** - Contains complete Standard card database and instructions for AI deck building.

## Repository Structure
Each deck is organized in its own folder with:
- **decklist.txt**: MTGA-importable decklist
- **analysis.md**: Comprehensive card-by-card reasoning and strategic breakdown
- **sideboard_guide.md**: Matchup-specific boarding plans and strategies

## Core Components

### 1. Standard Card Database
**File**: `standard_cards.json` (3MB, ~1500 cards)
- Complete Standard-legal card pool from Scryfall
- Includes: name, mana cost, CMC, type, oracle text, colors, keywords, power/toughness, loyalty, set info, rarity
- Updated when Standard rotation occurs or new sets release
- **Last Updated**: March 5, 2026

### 2. AI Deck Builder Instructions
**File**: `AI_DECK_BUILDER_INSTRUCTIONS.md`
- Comprehensive 9-phase deck construction framework
- Mathematical mana base optimization
- Turn-by-turn simulation analysis
- Rigorous format legality verification (cross-references `standard_cards.json`)
- Meta-aware matchup analysis
- Self-critical evaluation protocols

### 3. Data Fetcher Script
**File**: `scripts/fetch_standard_cards.py`
- Downloads latest Standard card data from Scryfall Bulk Data API
- Exports to JSON, TXT, and CSV formats
- Run when Standard rotation occurs: `python scripts/fetch_standard_cards.py`

## How to Use This Repository

### For Deck Builders (Human)
1. **Browse Decks**: Navigate to folders organized by color/archetype
2. **Import to MTGA**: Copy contents of `decklist.txt` directly into MTG Arena
3. **Understand Strategy**: Read `analysis.md` for detailed reasoning
4. **Master Matchups**: Consult `sideboard_guide.md` for specific opponent strategies

### For AI Assistants
**This repository is designed for external AI integration.** To use:

1. **Load Instructions**: Read `AI_DECK_BUILDER_INSTRUCTIONS.md` for complete methodology
2. **Load Card Database**: Parse `standard_cards.json` for Standard-legal card pool
3. **Verify User Cards**: Cross-reference user-provided cards against database
4. **Build Deck**: Follow 9-phase analysis framework with mathematical rigor
5. **Publish Results**: Create folder with `decklist.txt`, `analysis.md`, `sideboard_guide.md`

**Key Requirement**: ALL card suggestions must exist in `standard_cards.json`. If a card is not in the database, it is NOT Standard-legal.

## Request a Deck
To request a new deck analysis:
1. Provide your card pool or cards to build around
2. Specify format (default: Standard)
3. Indicate strategic preferences (aggro/midrange/control/combo)
4. The AI will:
   - Verify cards against `standard_cards.json`
   - Generate full analysis with mathematical optimization
   - Publish properly structured folder to repository

## Formats Supported
- **Standard** (default, full database support)
- Pioneer
- Modern
- Legacy
- Vintage
- Commander
- Pauper
- Historic
- Explorer
- Alchemy

**Note**: Only Standard format has comprehensive card database support (`standard_cards.json`). Other formats require manual legality verification or external data sources.

## Philosophy
Every card choice is mathematically justified. Every strategic decision is rigorously challenged. No deck is published without surviving brutal self-critique.

**Database-First Approach**: All card suggestions are verified against `standard_cards.json` to ensure format legality. No exceptions.

**Failure is acceptable. Unjustified mediocrity is not.**

## Updating Card Data
When Standard rotation occurs or new sets release:
```bash
python scripts/fetch_standard_cards.py
```
This updates `standard_cards.json` with the latest Standard-legal card pool from Scryfall.

## Repository Self-Sufficiency
This repository is **completely self-contained**:
- ✅ Complete Standard card database (`standard_cards.json`)
- ✅ Comprehensive AI instructions (`AI_DECK_BUILDER_INSTRUCTIONS.md`)
- ✅ Data update automation (`scripts/fetch_standard_cards.py`)
- ✅ Standardized output templates (`.github/DECK_TEMPLATE/`)
- ✅ Documentation for all components

**External AIs can link to this repository and immediately begin building decks without additional resources.**

---

**Maintained by**: Celeannora  
**Last Updated**: March 5, 2026  
**Version**: 2.0 (Database-Integrated)  
**Powered by**: [Perplexity AI](https://www.perplexity.ai) using [AI Deck Builder Instructions](AI_DECK_BUILDER_INSTRUCTIONS.md)
