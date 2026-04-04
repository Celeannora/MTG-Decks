# Local Deck-Building Workflow

This guide is for users who want to run the full AI-assisted deck-building process **on their own machine** — useful when your AI tool has limited tool access, rate limits, or no ability to run scripts directly.

The key idea: **everything goes into a single `session.md` file.** No scattered outputs, no lost context between tool calls. One file in, one file out.

---

## Prerequisites

```bash
# Clone the repo
git clone https://github.com/Celeannora/MTG-Decks.git
cd MTG-Decks

# Install dependencies (just `requests`)
pip install -r requirements.txt

# Verify the card database exists
ls cards_by_category/
# Should show: artifact/ creature/ enchantment/ instant/ land/ planeswalker/ sorcery/ etc.

# If the database is missing or outdated, regenerate it:
python scripts/fetch_and_categorize_cards.py
```

---

## Quick Start

### Step 1: Generate a session scaffold

```bash
python scripts/generate_deck_scaffold.py \
  --name "Orzhov Lifegain" \
  --colors WB \
  --archetype lifegain
```

This does three things:
1. Runs all relevant `search_cards.py` queries for your archetype
2. Embeds the complete candidate pool (every card result) into a single `session.md`
3. Creates the deck folder with empty templates for `decklist.txt`, `analysis.md`, and `sideboard_guide.md`

Output:
```
Decks/2026-04-03_Orzhov_Lifegain/
├── session.md            ← All your work goes here
├── decklist.txt          ← Empty (fill during Gate 3)
├── analysis.md           ← Template (compile after all gates)
└── sideboard_guide.md    ← Template (fill after Gate 5)
```

### Step 2: Feed session.md to your AI tool

Open `session.md` and paste it into your AI tool as context. The file contains:
- All candidate pool data (pre-queried, embedded)
- Every gate section with checklists
- Structured tables to fill in
- The validation command to run at the end

Tell the AI:
> "This is a deck-building session file. Work through each gate in order, filling in the sections. Only use cards from the candidate pool in Gate 1. Cite the source file for every card."

### Step 3: Fill in gates inside session.md

Work through the gates in order. All work stays in `session.md`:

| Gate | What happens |
|------|-------------|
| Gate 1 | Already done — candidate pool is embedded. Run extra queries if needed. |
| Gate 2 | Define strategy, win condition, target turn. |
| Gate 2.5 | Score synergies, map chains, check thresholds. |
| Gate 3 | Select all 60 mainboard cards with source citations. |
| Gate 4 | Build mana base with pip counts and Karsten validation. |
| Gate 5 | Select 15 sideboard cards with source citations. |
| Gate 6 | Run validation script and record the result. |

### Step 4: Run validation

```bash
# Default — reads cards_by_category/ CSVs directly (no extra setup)
python scripts/validate_decklist.py Decks/2026-04-03_Orzhov_Lifegain/decklist.txt --verbose

# With synergy tag summary and land-count sanity check
python scripts/validate_decklist.py Decks/2026-04-03_Orzhov_Lifegain/decklist.txt --strict --show-tags

# Faster offline backends (run build_local_database.py first)
python scripts/validate_decklist.py --db json Decks/2026-04-03_Orzhov_Lifegain/decklist.txt
python scripts/validate_decklist.py --db sqlite Decks/2026-04-03_Orzhov_Lifegain/decklist.txt
```

Paste the output into the "Validation Output" section of `session.md`.

### Step 5: Finalize output files

Copy the completed work from `session.md` into:
- `decklist.txt` — MTGA-importable list
- `analysis.md` — Full analysis following the template
- `sideboard_guide.md` — Matchup boarding plans

---

## Scaffold Options

### All archetypes

```bash
# Aggro
python scripts/generate_deck_scaffold.py --name "Boros Aggro" --colors WR --archetype aggro

# Midrange
python scripts/generate_deck_scaffold.py --name "Golgari Midrange" --colors BG --archetype midrange

# Control
python scripts/generate_deck_scaffold.py --name "Azorius Control" --colors WU --archetype control

# Combo
python scripts/generate_deck_scaffold.py --name "Jeskai Combo" --colors WUR --archetype combo

# Mill
python scripts/generate_deck_scaffold.py --name "Dimir Mill" --colors UB --archetype mill

# Lifegain
python scripts/generate_deck_scaffold.py --name "Orzhov Lifegain" --colors WB --archetype lifegain

# Tribal (with --tribe flag)
python scripts/generate_deck_scaffold.py --name "Simic Frogs" --colors GU --archetype tribal --tribe Frog

# Ramp
python scripts/generate_deck_scaffold.py --name "Gruul Ramp" --colors RG --archetype ramp

# Tempo
python scripts/generate_deck_scaffold.py --name "Izzet Tempo" --colors UR --archetype tempo

# Burn
python scripts/generate_deck_scaffold.py --name "Mono Red Burn" --colors R --archetype burn
```

### Offline mode (no queries)

If you don't have the card database yet or want a blank template:

```bash
python scripts/generate_deck_scaffold.py \
  --name "My Deck" --colors WB --archetype lifegain --skip-queries
```

This generates the full scaffold structure with placeholder query sections. You run the queries manually and paste the results in.

### Additional flags

```bash
--date 2026-04-01        # Override date (default: today)
--output-dir ./my_decks  # Custom output directory
--extra-tags draw,etb    # Add extra search tags to all queries
--tribe Angel            # Creature subtype filter (for tribal)
```

---

## Running Additional Queries

If the initial queries don't cover what you need, run more manually:

```bash
# Example: find creatures with ETB effects
python scripts/search_cards.py --type creature --colors WB --tags etb --show-tags

# Example: find cheap counterspells
python scripts/search_cards.py --type instant --colors WB --tags counter --cmc-max 2 --show-tags

# Example: find a specific card
python scripts/search_cards.py --name "Sheoldred"
```

Paste the full output into the "Additional Queries" section of `session.md`.

---

## Why a Single File?

AI tools with limited context or tool access work best when everything is in one place:

1. **No lost context** — The candidate pool, strategy decisions, and card selections all live together. The AI doesn't need to "remember" what happened in a previous tool call.

2. **Auditable** — Every decision traces back to a query result visible in the same file. You can review the entire chain from "candidate found" to "card selected" in one scroll.

3. **Portable** — `session.md` works with any AI tool: ChatGPT, Claude, local LLMs, Copilot. Paste it in and start working. No plugin or API access required.

4. **Recoverable** — If your session is interrupted, everything is saved. Resume exactly where you left off.

5. **Consolidated output** — Instead of the AI generating files across multiple tool calls (which can fail, conflict, or get lost), everything lands in one file that you then split into the final outputs yourself.

---

## Troubleshooting

**"cards_by_category/ not found"**
```bash
python scripts/fetch_and_categorize_cards.py
```
This downloads ~100 MB from Scryfall and rebuilds the database. Requires internet access.

**"No cards matched the given filters"**
Try broadening your query. Remove `--tags` or `--cmc-max` constraints. Check that `--colors` uses the right letters (W/U/B/R/G).

**Validation fails with illegal cards**
The card is not in the database (rotated, banned, or misspelled). Check the "Did you mean?" suggestions. Only cards in `cards_by_category/` are legal.

**Session file is too large for my AI tool**
Use `--skip-queries` to generate a blank scaffold, then run queries individually and paste only the relevant results. Or use `--format names` with `search_cards.py` for compact output.
