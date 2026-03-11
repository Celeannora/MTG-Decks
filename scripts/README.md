# Scripts

This directory contains Python utilities for managing the MTG card database and validating decklists.

## Requirements

```bash
pip install -r requirements.txt
```

`requests` is the only runtime dependency.

## Scripts

### `fetch_and_categorize_cards.py`

Downloads all Standard-legal cards from the Scryfall bulk data API and writes them
into `cards_by_category/` as letter-split CSV files.

```bash
python scripts/fetch_and_categorize_cards.py
```

- Downloads ~100 MB of bulk data from Scryfall (streamed, not buffered)
- Filters to Standard-legal cards only
- Deduplicates by card name (keeps first/newest printing)
- Splits into `{type}/{type}_{letter}.csv` files, each ≤80 KB
- Adds `battle` card type (introduced in March of the Machine)
- Regenerates `cards_by_category/_INDEX.md`

**Run this after every new MTG set release or Standard rotation.**

---

### `validate_decklist.py`

Validates a decklist against `cards_by_category/`. Requires no pre-build step.

```bash
python scripts/validate_decklist.py Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --quiet Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --verbose Decks/my_deck/decklist.txt
```

**What it checks:**
- Every card exists in the database (Standard-legal)
- Mainboard has exactly 60 cards
- Sideboard has exactly 15 cards (or 0)
- No non-basic land appears more than 4 times
- Offers "did you mean?" suggestions for near-miss card names

**Exit codes:** `0` = pass, `1` = illegal cards, `2` = file not found, `3` = count violation

---

### `validate_decklist_local.py`

Fast offline validation using a pre-built local index. Much faster than the full CSV scan.

```bash
# Build the index first (one-time)
python scripts/build_local_database.py

# Then validate
python scripts/validate_decklist_local.py Decks/my_deck/decklist.txt
python scripts/validate_decklist_local.py --sqlite Decks/my_deck/decklist.txt
```

Same exit codes and flags as `validate_decklist.py`.

---

### `build_local_database.py`

Builds the `local_db/` directory used by `validate_decklist_local.py`.

```bash
python scripts/build_local_database.py
```

**Output:**

```
local_db/
├── card_index.json    # Lightweight JSON pointer index (~200-300 KB)
├── card_names.txt     # Plain text card name list (~100 KB)
└── card_details.db    # Full SQLite database (~800 KB)
```

The `local_db/` directory is in `.gitignore` and is not committed to the repo.

---

### `mtg_utils.py`

Shared utilities imported by both validator scripts. Not intended to be run directly.

Provides `parse_decklist(path)` which handles MTGA-format decklists with `//` and `#` comments,
`Deck` / `Sideboard` section headers, and set code stripping.

---

## License

MIT License — see [LICENSE](../LICENSE).
