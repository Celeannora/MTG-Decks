# Scripts

This directory contains Python utilities for managing the MTG card database, validating decklists, and generating deck-building scaffolds.

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

### `search_cards.py`

Searches the `cards_by_category/` CSV files for cards matching a query. Supports filtering by name, type, color, keywords, mana value, and more.

```bash
python scripts/search_cards.py --color W --type creature --keyword lifelink
python scripts/search_cards.py --color UB --type instant --max-mv 3
python scripts/search_cards.py --name "Lightning"
```

Used standalone or called internally by `generate_deck_scaffold.py` to build candidate pools.

---

### `generate_deck_scaffold.py`

Generates a complete single-file session scaffold for building a new deck through the full gate system (Gates 1–6) locally. Designed for users running the deck-building process with any AI tool that has limited tool access.

```bash
# Basic usage
python scripts/generate_deck_scaffold.py --name "Orzhov Lifegain" --colors WB --archetype lifegain

# Tribal build
python scripts/generate_deck_scaffold.py --name "Simic Frog Tribal" --colors GU --archetype tribal --tribe Frog

# Skip queries (offline template only)
python scripts/generate_deck_scaffold.py --name "Dimir Control" --colors UB --archetype control --skip-queries

# Custom output directory
python scripts/generate_deck_scaffold.py --name "Boros Aggro" --colors WR --archetype aggro --output-dir my_decks/
```

**Flags:**

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | Yes | Deck name (used for folder naming) |
| `--colors` | Yes | Color identity: W, U, B, R, G, WB, WUB, etc. |
| `--archetype` | Yes | One of: `aggro`, `midrange`, `control`, `combo`, `mill`, `lifegain`, `tribal`, `ramp`, `tempo`, `burn` |
| `--tribe` | No | Creature subtype for tribal builds (e.g. Frog, Angel) |
| `--date` | No | Date override in YYYY-MM-DD format (default: today) |
| `--output-dir` | No | Output directory override (default: `Decks/`) |
| `--extra-tags` | No | Additional search tags, comma-separated |
| `--skip-queries` | No | Generate scaffold without running `search_cards.py` queries |

**What it does:**
1. Runs archetype-specific `search_cards.py` queries to find candidate cards
2. Embeds all candidate pool results directly into the session file
3. Stubs out every required gate section (strategy, synergy, selection, mana base, sideboard, final checks)
4. Pre-populates the deck folder structure
5. Consolidates ALL output into a single `session.md` file

**Output:**

```
Decks/YYYY-MM-DD_Deck_Name/
├── session.md          ← The single consolidated file (all work goes here)
├── decklist.txt        ← Empty template (filled during Gate 3)
├── analysis.md         ← Empty template (filled after all gates)
└── sideboard_guide.md  ← Empty template (filled after Gate 5)
```

**Exit codes:** `0` = success, `1` = invalid arguments, `2` = `cards_by_category/` not found

See [LOCAL_WORKFLOW.md](../LOCAL_WORKFLOW.md) for the full local deck-building guide.

---

### `hypergeometric_analysis.py`

Runs hypergeometric probability calculations for draw consistency analysis. Computes the probability of drawing specific cards or card types by a given turn.

```bash
python scripts/hypergeometric_analysis.py Decks/my_deck/decklist.txt
```

---

### `mana_base_comparison.py`

Compares a deck's mana base against recommended distributions. Useful for validating land counts and color ratios during Gate 4.

```bash
python scripts/mana_base_comparison.py Decks/my_deck/decklist.txt
```

---

### `index_decks.py`

Scans the `Decks/` directory and regenerates the deck index. Run after adding or removing decks.

```bash
python scripts/index_decks.py
```

---

### `mtg_utils.py`

Shared utilities imported by both validator scripts. Not intended to be run directly.

Provides `parse_decklist(path)` which handles MTGA-format decklists with `//` and `#` comments,
`Deck` / `Sideboard` section headers, and set code stripping.

---

## License

MIT License — see [LICENSE](../LICENSE).
