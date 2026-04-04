# MTG Deck Repository

## 🛑 AI ASSISTANTS: STOP AND READ THIS FIRST 🛑

**Before building ANY deck, you MUST:**

1. ⚠️ **STOP** - Do not name any card yet
2. 📚 **READ** `AI_INSTRUCTIONS.md` - Your ONLY authoritative instruction source
3. 🔍 **QUERY DATABASE** - Use `python scripts/search_cards.py` to build your candidate pool
4. ✓ **VERIFY EVERY CARD** - Every card must come from a `search_cards.py` query result
5. 🧪 **RUN VALIDATOR** - Execute `python scripts/validate_decklist.py` before finalizing
6. ❓ **ASK QUESTIONS** - If the archetype or win condition is unclear, ask before building

**Skipping these steps will generate illegal decks.**

📖 **Primary instruction file:** [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md)

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
│       ├── session.md               # Consolidated build session (local workflow)
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
│   ├── search_cards.py                # 🔍 AI card search with strategy tag filtering
│   ├── validate_decklist.py           # Validator (online CSV or offline --local mode)
│   ├── build_local_database.py        # Builds local_db/ for fast offline validation
│   ├── generate_deck_scaffold.py      # 📝 Local workflow: single-file session generator
│   ├── index_decks.py                 # Regenerates Decks/_INDEX.md registry
│   └── mtg_utils.py                   # Shared utilities (parser, etc.)
├── .github/DECK_TEMPLATE/           # Template for new decks
├── AI_INSTRUCTIONS.md               # 🔴 SINGLE SOURCE OF TRUTH for AI deck building
├── LOCAL_WORKFLOW.md                 # 💻 Guide for running the process on your own machine
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

### Online validation (reads cards_by_category/ CSVs directly)

```bash
python scripts/validate_decklist.py Decks/my_deck/decklist.txt
```

### Offline validation (faster, uses pre-built local_db/)

```bash
# One-time setup
python scripts/build_local_database.py

# Then validate quickly
python scripts/validate_decklist.py --local Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --local --sqlite Decks/my_deck/decklist.txt
```

### Validation flags

```bash
--quiet    # Summary only (good for CI/CD)
--verbose  # Print source CSV for each card
--local    # Use pre-built local_db/ instead of scanning CSVs
--sqlite   # (with --local) Use SQLite DB instead of JSON index
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

1. **Query database FIRST** — before naming any card
2. **Only use database cards** — never rely on web searches or training memory
3. **Cite every card** — each card must trace back to a `search_cards.py` result
4. **Run validation script** — execute before finalizing deck
5. **Document queries** — list all `search_cards.py` commands run in analysis.md
6. **Ask if unclear** — ask clarifying questions about archetype/win condition before building
7. **Zero tolerance** — even one illegal card invalidates the entire deck

### Workflow

1. Read [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md) for complete methodology
2. Use `search_cards.py` to query the database for each needed card type
3. Build candidate pool exclusively from query results
4. Select cards only from the candidate pool, citing source file for each
5. Run `python scripts/validate_decklist.py Decks/[deck_name]/decklist.txt`
6. Create database query report section in analysis.md
7. Save completed deck to `Decks/YYYY-MM-DD_Archetype_Name/`

### Card search examples

```bash
# Lifegain creatures in white/black
python scripts/search_cards.py --type creature --colors WB --tags lifegain

# Cheap removal instants
python scripts/search_cards.py --type instant --tags removal --cmc-max 3

# Mill cards across all spell types
python scripts/search_cards.py --type instant,sorcery --tags mill

# Dual lands for a color pair
python scripts/search_cards.py --type land --colors WU
```

**Never trust external sources for card legality** — the database is the only source of truth.

---

## Local workflow (no tool access required)

If your AI tool has limited tool access or rate limits, you can run the entire deck-building process on your own machine. The scaffold generator creates a **single `session.md` file** with all query results embedded, so the AI only needs to read one file and fill in the gates.

```bash
# Generate a session scaffold (runs all queries, embeds results)
python scripts/generate_deck_scaffold.py --name "Orzhov Lifegain" --colors WB --archetype lifegain

# Output: Decks/2026-04-03_Orzhov_Lifegain/session.md (single file with everything)
```

Supported archetypes: `aggro`, `midrange`, `control`, `combo`, `mill`, `lifegain`, `tribal`, `ramp`, `tempo`, `burn`

See **[`LOCAL_WORKFLOW.md`](LOCAL_WORKFLOW.md)** for the full guide.

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
**Last updated**: April 3, 2026  
**Version**: 9.1
