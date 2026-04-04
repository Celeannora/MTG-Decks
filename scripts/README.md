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

Validates a decklist against the local card database. Works out of the box
after cloning — no pre-build step required.

**Quick start (after cloning):**

```bash
python scripts/validate_decklist.py Decks/my_deck/decklist.txt
```

**All usage:**

```bash
# Default — reads cards_by_category/ CSVs directly (no setup needed)
python scripts/validate_decklist.py Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --verbose Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --quiet Decks/my_deck/decklist.txt

# Faster backends (run build_local_database.py first)
python scripts/validate_decklist.py --db json Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --db sqlite Decks/my_deck/decklist.txt

# Extra analysis
python scripts/validate_decklist.py --strict Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --show-tags Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --strict --show-tags --verbose Decks/my_deck/decklist.txt
```

**What it checks:**

- Every card exists in the database (Standard-legal)
- Mainboard has exactly 60 cards
- Sideboard has exactly 15 cards (or 0)
- No non-basic land appears more than 4 times (respects cards with unlimited copies like Rat Colony)
- Offers "did you mean?" suggestions for near-miss card names
- Empty or missing decklist detection

**With `--strict`:**

- Land count sanity check (warns if outside 20–28 range)

**With `--show-tags`:**

- Prints synergy tag summary for all mainboard non-land cards (lifegain, removal, draw, etc.)

**Flags:**

| Flag | Description |
|------|-------------|
| `--db csv` | Read cards_by_category/ CSVs directly (default, no setup needed) |
| `--db json` | Read local_db/card_index.json (run `build_local_database.py` first) |
| `--db sqlite` | Read local_db/card_details.db (run `build_local_database.py` first) |
| `--quiet` / `-q` | Suppress info-level logging |
| `--verbose` / `-v` | Print source CSV path for each card |
| `--strict` | Enable extra checks (land count warnings) |
| `--show-tags` | Print synergy tag distribution for the deck |

**Exit codes:** `0` = pass, `1` = illegal cards, `2` = file/database not found, `3` = count violation

---

### `build_local_database.py`

Builds the `local_db/` directory for faster offline validation with `--db json` or `--db sqlite`.

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

Searches the `cards_by_category/` CSV files for cards matching a query. Supports filtering by name, type, color identity, keywords, mana value, rarity, and strategic tags.

```bash
python scripts/search_cards.py --colors W --type creature --tags lifegain
python scripts/search_cards.py --colors UB --type instant --cmc-max 3
python scripts/search_cards.py --name "Lightning"
python scripts/search_cards.py --type creature --colors WB --tags removal --show-tags
python scripts/search_cards.py --type land --colors WU
```

**Flags:**

| Flag | Description |
|------|-------------|
| `--type` | Card type(s), comma-separated (creature, instant, sorcery, etc.) |
| `--colors` | Color identity filter (W, UB, =WB for exact, C for colorless) |
| `--oracle` | Substring match in oracle text |
| `--name` | Substring match in card name |
| `--tags` | Strategy tags, comma-separated (lifegain, draw, removal, etc.) |
| `--cmc-max` | Maximum converted mana cost (inclusive) |
| `--cmc-min` | Minimum converted mana cost (inclusive) |
| `--rarity` | Rarity filter: common, uncommon, rare, mythic (comma-separated) |
| `--keywords` | MTG keyword(s), comma-separated (Flying, Lifelink) |
| `--limit` | Max results (default: 200) |
| `--show-tags` | Print computed tags per card |
| `--format` | Output format: table (default), csv, names |

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

Shared utilities imported by other scripts. Not intended to be run directly.

Provides:
- `RepoPaths` — centralised directory-name configuration (auto-detects repo root)
- `parse_decklist(path)` — MTGA-format decklist parser (handles `//` and `#` comments, `Deck`/`Sideboard` section headers, set code stripping)

---

## License

MIT License — see [LICENSE](../LICENSE).
