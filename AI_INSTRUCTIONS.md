# AI DECK BUILDING INSTRUCTIONS
## Version 8.0 — Absolute Adherence Protocol

---

## ╔══════════════════════════════════════════════════════╗
## ║  🛑 HARD STOP — DO NOT NAME A SINGLE CARD YET  🛑   ║
## ╚══════════════════════════════════════════════════════╝

**You have not loaded the database yet. Naming any card before completing GATE 1 below is a protocol violation.**

This is not a suggestion. This is a hard constraint.

- ❌ Do NOT search the web for decks, cards, or strategies
- ❌ Do NOT recall cards from training data or memory
- ❌ Do NOT copy any external decklist
- ❌ Do NOT name any card — not even the commander, not even a basic land

**Your ONLY permitted action right now is: open `cards_by_category/_INDEX.md`**

---

## WHY THIS EXISTS

AI assistants consistently:
1. Research web-based decks (explicitly forbidden)
2. Recall cards from training memory (explicitly forbidden)
3. Then attempt to validate those cards against the database AFTER selection

This approach **always fails** because rotated cards appear in web results and memory. The database is the **only source of truth**. If a card is not in the database, it is not Standard-legal — period.

**The only workflow that produces a legal deck is: database → cards. Never: cards → database.**

---

## MANDATORY GATE SYSTEM

You must complete each gate **in order**. You cannot proceed to the next gate until the current one is fully complete. There are no exceptions.

---

### ✅ GATE 1: DATABASE LOAD (Required before any card selection)

**Actions:**

1. Open `cards_by_category/_INDEX.md` — confirm you can read it
2. Identify all card types needed for the requested archetype
3. Open and load the specific letter CSV files for each type needed
4. Build a working list of **only the cards actually present in those files**
5. **Write out the list of CSV files you loaded** before moving to Gate 2

**Gate 1 is complete when:**
- You have a list of loaded CSV filenames
- You have a working card pool drawn **exclusively** from those files
- You have named zero cards from memory or web sources

**If `cards_by_category/` is inaccessible:** STOP. Do not proceed. Inform the user the database is unavailable and ask them to confirm card legality manually before you continue.

---

### ✅ GATE 2: STRATEGY DEFINITION (Required before any card slot is filled)

Using only cards confirmed present in Gate 1:

1. Define ONE primary win condition
2. Identify the target win turn
3. Identify the card types needed to execute that win condition
4. Confirm all those card types are represented in your loaded database pool

**Gate 2 is complete when:**
- Strategy is defined using database-confirmed cards only
- No card has been assigned a slot yet

---

### ✅ GATE 3: CARD SELECTION (One card at a time, database only)

For each card slot:

1. **Name the card** — pulled from your Gate 1 database pool only
2. **State the CSV file it came from** (e.g., `cards_by_category/creature/creature_s1.csv`)
3. **Record its mana cost, type line, and set code** from the CSV row
4. Only then add it to the decklist

**If you cannot cite a CSV file for a card, do not include it. Full stop.**

Cards that fail Gate 3:
- Cards recalled from memory without CSV citation → **REJECTED**
- Cards found via web search → **REJECTED**
- Cards "assumed" to be legal → **REJECTED**
- Cards present in web decklists but not confirmed in CSV → **REJECTED**

---

### ✅ GATE 4: MANA BASE (Database-verified lands only)

All lands must come from `cards_by_category/land/` files.

1. Count colored pips across your mainboard
2. Load the appropriate land letter files
3. Select lands with CSV citations
4. Validate curve support

---

### ✅ GATE 5: SIDEBOARD (Database-verified only)

All 15 sideboard cards must have CSV citations. Same rules as Gate 3.

---

### ✅ GATE 6: FINAL VALIDATION CHECKLIST

Before writing any output files, confirm every item:

- [ ] All 60 mainboard cards have a cited CSV source
- [ ] All 15 sideboard cards have a cited CSV source
- [ ] Zero cards sourced from web searches
- [ ] Zero cards sourced from memory or training data
- [ ] Set codes and collector numbers recorded from CSV
- [ ] Mana base math validated
- [ ] Validation script run: `python scripts/validate_decklist.py Decks/[deck_name]/decklist.txt`
- [ ] Validation script returned exit code 0

**If any item is unchecked, do not output the deck.**

---

## LEGAL VALIDATION — THE CORE RULE

> **A card is legal if and only if it exists in `cards_by_category/`.**
>
> - Present in database ✅ → Legal
> - Not present in database ❌ → Illegal (rotated, banned, or nonexistent)
> - "Probably legal" → Does not exist. Verify or reject.
> - Web source says it's legal → Irrelevant. Verify in database or reject.
> - You remember it being legal → Irrelevant. Verify in database or reject.

There is no appeal. There is no override. The database is authoritative.

---

## PROHIBITED ACTIONS (Zero Tolerance)

The following actions result in an immediately invalid deck that must be restarted from Gate 1:

| Action | Consequence |
|--------|-------------|
| Naming any card before loading database | Restart from Gate 1 |
| Using web search results to select cards | Restart from Gate 1 |
| Copying any external decklist | Restart from Gate 1 |
| Adding a card without a CSV citation | Remove card, find database alternative |
| Assuming card legality without verification | Restart from Gate 1 |
| Building deck then validating after | Restart from Gate 1 |
| Mixing database-verified and unverified cards | Restart from Gate 1 |

ONE illegal card = ENTIRE DECK REJECTED.

---

## CARD DATABASE STRUCTURE

```
cards_by_category/
├── _INDEX.md              ← Open this first, always
├── artifact/
│   ├── artifact_a.csv
│   └── ...
├── battle/
│   └── battle_a.csv
├── creature/
│   ├── creature_a1.csv    ← Large letters split into numbered files
│   ├── creature_a2.csv
│   ├── creature_b.csv
│   └── ...
├── enchantment/
├── instant/
├── land/
├── other/
├── planeswalker/
└── sorcery/
```

**Pattern:** `cards_by_category/{type}/{type}_{first_letter}.csv`

Always check `_INDEX.md` first to confirm which numbered file(s) exist for a given letter.

### CSV Columns

```
name, mana_cost, cmc, type_line, oracle_text, colors, color_identity,
rarity, set, set_name, collector_number, power, toughness, loyalty,
produced_mana, keywords
```

---

## OUTPUT FORMAT

### File Structure

```
Decks/
└── YYYY-MM-DD_Archetype_Name/
    ├── decklist.txt        # MTGA-importable
    ├── analysis.md         # Full reasoning + database verification
    └── sideboard_guide.md  # Matchup boarding plans
```

### decklist.txt Format

```
Deck
4 Card Name (SET) Collector_Number
4 Another Card (SET) Collector_Number
...
[Sort: Creatures > Planeswalkers > Instants > Sorceries > Artifacts > Enchantments > Lands]

Sideboard
3 Sideboard Card (SET) Collector_Number
...
```

### Required Sections in analysis.md

#### 1. Database Verification (MANDATORY — must appear first)

```markdown
## Database Verification

### Files Loaded
- `cards_by_category/creature/creature_s1.csv`
- `cards_by_category/instant/instant_c.csv`
- `cards_by_category/land/land_f1.csv`
[List ALL CSV files loaded]

### Per-Card Verification (ALL 60+15 cards)
✓ [Card Name] - [cards_by_category/type/file.csv]
[Every single card listed with its source file]

### Rejected Cards
[Cards considered but not found in database — list with reason]

### Validation Script Result
$ python scripts/validate_decklist.py Decks/YYYY-MM-DD_Archetype/decklist.txt
✅ VALIDATION PASSED
All cards are legal and present in the database.
```

#### 2. Executive Summary
#### 3. Card-by-Card Breakdown
#### 4. Mana Base Analysis
#### 5. Curve Analysis
#### 6. Matchup Table
#### 7. Weaknesses and Mitigations
#### 8. Playtesting Results

---

## VALIDATION SCRIPT USAGE

```bash
python scripts/validate_decklist.py Decks/YYYY-MM-DD_Archetype/decklist.txt

# Flags
--quiet    # Summary only
--verbose  # Print source CSV for each valid card
```

| Exit Code | Meaning |
|-----------|---------|
| 0 | Validation passed |
| 1 | Illegal / unrecognised cards found |
| 2 | Decklist file not found |
| 3 | Deck count violation (wrong 60/15/4-copy counts) |

---

## WHEN A REQUESTED CARD IS NOT IN THE DATABASE

> "I checked `cards_by_category/` and [Card Name] is not present. It is not Standard-legal.
>
> Legal alternatives from the database:
> - [Alternative 1] — `cards_by_category/[file]`
> - [Alternative 2] — `cards_by_category/[file]`
> - [Alternative 3] — `cards_by_category/[file]`
>
> Would you like to use one of these instead?"

**Never include the illegal card even if the user insists.** The database is authoritative.

---

## SESSION ACKNOWLEDGMENT

Every AI session must begin with this acknowledgment **before any other action:**

> "I acknowledge this repository's absolute database-first protocol. I will:
> 1. Open `cards_by_category/_INDEX.md` before naming any card
> 2. Load specific CSV files before making any card selection
> 3. Cite the source CSV for every card I suggest
> 4. Reject any card not found in the database, regardless of web sources or memory
> 5. Run the validation script before finalizing any deck
>
> I will not name a single card until Gate 1 is complete."

---

## PHILOSOPHY

Every card choice is mathematically justified. Every strategic decision is rigorously challenged. No deck is published without surviving brutal self-critique.

**Format legality is non-negotiable.** A brilliant deck with illegal cards is worthless.

**Failure is acceptable. Unjustified mediocrity is not. Illegal cards are unacceptable.**

The database is the only source of truth. The workflow runs one direction only: database → cards.

---

## VERSION HISTORY

| Version | Date | Notes |
|---------|------|-------|
| 8.0 | 2026-03-15 | Absolute adherence rewrite: hard-gated protocol, explicit card-naming prohibition before database load, zero-tolerance table, mandatory CSV citation per card, clarified direction of workflow (database→cards never cards→database) |
| 7.1 | 2026-03-10 | Fix directory name; add `battle` type; add validator flags/exit codes |
| 7.0 | 2026-03-09 | Consolidated all instructions into single file; added validation script integration |
| 6.0 | 2026-03-09 | Added mandatory database-first workflow; prohibited web search card selection |
| 5.0 | 2026-03-08 | Rebuilt for letter-split card database structure |

**Maintained by:** Celeannora
**Last updated:** March 15, 2026
