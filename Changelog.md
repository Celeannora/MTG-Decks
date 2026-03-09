# Changelog

## v5.0 — March 9, 2026

### 🎉 Major improvements

**Automated validation**
- Added `scripts/validate_decklist.py` - automated deck legality validator
- Validates all cards in decklist.txt against cards_by_category directory database
- Provides clear pass/fail output with illegal card identification
- Prevents illegal cards from entering repository
- Exit code integration for CI/CD pipelines

**Consolidated AI instructions**
- Created `AI_INSTRUCTIONS.md` as single source of truth for all AI deck building
- Consolidated content from:
  - `Deck_builder_instructions.md` (13KB)
  - `DECK_BUILDING_PROTOCOL.md` (3.7KB)
  - `Deck_building_guidelines.md` (6.5KB)
- All other instruction files now deprecated
- Reduced instruction overload - AI now has ONE file to follow

**Enhanced README**
- Added prominent "🛑 AI ASSISTANTS: STOP" section at top
- Clear 5-step workflow before deck building begins
- Validation script documentation and examples
- Points to AI_INSTRUCTIONS.md as authoritative source

### Breaking changes
- **Deprecated files** (content merged into AI_INSTRUCTIONS.md):
  - `Deck_builder_instructions.md` → Use `AI_INSTRUCTIONS.md`
  - `DECK_BUILDING_PROTOCOL.md` → Use `AI_INSTRUCTIONS.md`
  - `Deck_building_guidelines.md` → Use `AI_INSTRUCTIONS.md`
  - `AI_DECK_BUILDER_INSTRUCTIONS.md` → Use `AI_INSTRUCTIONS.md`
  - `AI_DECK_BUILDING_GUIDELINES.md` → Use `AI_INSTRUCTIONS.md`

### New files
- `scripts/validate_decklist.py` - 250 lines, full validation with detailed output
- `AI_INSTRUCTIONS.md` - 12.5KB, comprehensive single-file instructions

### Workflow changes

**Old workflow:**
1. AI reads multiple instruction files (often skips some)
2. AI builds deck
3. Manual verification catches illegal cards
4. Back-and-forth to fix issues

**New workflow:**
1. AI reads ONE instruction file (AI_INSTRUCTIONS.md)
2. AI loads database CSVs
3. AI builds deck using verified cards
4. AI runs `validate_decklist.py`
5. Automated validation catches any issues before submission
6. AI includes validation result in analysis.md

### Impact on issues

This release directly addresses:
- **Issue #1**: AI ignoring instructions → Single authoritative file reduces confusion
- **Issue #2**: No database validation → Validation script enforces legality

### Philosophy

> "The best validation is the one that runs automatically."
> "One source of truth beats five sources of confusion."

---

## v4.0 — March 8, 2026 (formerly v3.0)

### Breaking changes
- Card database directory renamed from `cards_by_category/` to `cards_by_category directory/`
- Files reorganized from `creature_part1.csv … creature_part5.csv` (arbitrary row-count chunks, 400KB each) to `creature/creature_a.csv … creature/creature_z.csv` (first-letter splits, ≤80KB each)
- All root markdown files renamed to sentence case

### New
- `cards_by_category directory/` with type subfolders and letter-split CSVs
- Updated `scripts/fetch_and_categorize_cards.py` to output letter-split files
- `Deck_builder_instructions.md` replaces `AI_DECK_BUILDER_INSTRUCTIONS.md`
- `Deck_building_guidelines.md` replaces `AI_DECK_BUILDING_GUIDELINES.md`
- `Rules_reference.md` replaces `MTG_RULES_REFERENCE.md`
- `Changelog.md` replaces `CHANGELOG.md`

### Removed
- `OPTIMIZATION_COMPLETE.md` (stale)
- `TEST_REPORT.md` (stale)
- Old flat-file structure

### Improvements
- Max file size reduced from 400KB to 80KB — no more API truncation
- Direct card lookup: know type + first letter → open one file immediately
- Truncation warnings removed from AI instructions (no longer applicable)
- README fully rewritten to reflect current structure

---

## v3.0 — March 5, 2026

- Initial CSV-only card database (`cards_by_category/`)
- Cards split by type into flat part files (creature_part1–5, land_part1–3, etc.)
- 400KB size limit per file
- Added `AI_DECK_BUILDER_INSTRUCTIONS.md` v4.x series

---

## v2.0 — February 2026

- Initial repository with `standard_cards.json` (monolithic 3MB file)
- Basic deck folder structure
- First decks published
