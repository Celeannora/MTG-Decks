# Changelog

## v3.0 — March 8, 2026

### Breaking changes
- Card database directory renamed from `cards_by_category/` to `card_data/`
- Files reorganized from `creature_part1.csv … creature_part5.csv` (arbitrary row-count chunks, 400KB each) to `creature/creature_a.csv … creature/creature_z.csv` (first-letter splits, ≤80KB each)
- All root markdown files renamed to sentence case

### New
- `card_data/` directory with type subfolders and letter-split CSVs
- Updated `scripts/fetch_and_categorize_cards.py` to output letter-split files under `card_data/`
- `Deck_builder_instructions.md` replaces `AI_DECK_BUILDER_INSTRUCTIONS.md`
- `Deck_building_guidelines.md` replaces `AI_DECK_BUILDING_GUIDELINES.md`
- `Rules_reference.md` replaces `MTG_RULES_REFERENCE.md`
- `Changelog.md` replaces `CHANGELOG.md`

### Removed
- `OPTIMIZATION_COMPLETE.md` (stale)
- `TEST_REPORT.md` (stale)
- `cards_by_category/` old flat-file structure

### Improvements
- Max file size reduced from 400KB to 80KB — no more API truncation
- Direct card lookup: know type + first letter → open one file immediately
- Truncation warnings removed from AI instructions (no longer applicable)
- README fully rewritten to reflect current structure

---

## v2.0 — March 5, 2026

- Initial CSV-only card database (`cards_by_category/`)
- Cards split by type into flat part files (creature_part1–5, land_part1–3, etc.)
- 400KB size limit per file
- Added `AI_DECK_BUILDER_INSTRUCTIONS.md` v4.x series

---

## v1.0 — February 2026

- Initial repository with `standard_cards.json` (monolithic 3MB file)
- Basic deck folder structure
- First decks published
