# AI DECK BUILDING INSTRUCTIONS
## Version 8.1 — Absolute Adherence Protocol

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

## ⚠️ CRITICAL: HOW THE FILE NAMING SYSTEM WORKS ⚠️

This is the most commonly misunderstood part of this repository.

### The letters in filenames are ALPHABETICAL — NOT thematic

The `_{letter}` suffix in every CSV filename refers to the **first letter of the card name**. Nothing else.

| Filename | Contains |
|----------|----------|
| `creature/creature_h1.csv` | Creatures whose names start with the letter **H** |
| `creature/creature_l1.csv` | Creatures whose names start with the letter **L** |
| `creature/creature_m1.csv` | Creatures whose names start with the letter **M** |
| `instant/instant_c.csv` | Instants whose names start with the letter **C** |
| `land/land_s1.csv` | Lands whose names start with the letter **S** |

### ❌ WRONG — Do not do this

```
# INCORRECT interpretation — letters do NOT mean themes:
Creatures: H (lifegain), L (lifegain), M (mill), D (drain)
Instants: C, D, H, L, M, S, T (counterspells, removal, lifegain, mill)
Lands: D, H, I, S, T (dual/triome lands for Esper)
```

This is completely wrong. H does not mean lifegain. M does not mean mill. D does not mean drain.
Loading files by theme instead of by card name wastes time and misses cards entirely.

### ✅ CORRECT — How to actually find a card

You must know (or hypothesize) the **name** of a card first, then look it up by its first letter:

```
To find "Sheoldred, the Apocalypse" (Creature starting with S):
→ Check _INDEX.md to see if creature_s1.csv, creature_s2.csv, creature_s3.csv, creature_s4.csv exist
→ Open those files and search for "Sheoldred"

To find "Sunfall" (Sorcery starting with S):
→ Open sorcery/sorcery_s.csv
→ Search for "Sunfall"

To find "Adarkar Wastes" (Land starting with A):
→ Open land/land_a.csv
→ Search for "Adarkar Wastes"
```

### ✅ CORRECT — How to browse a card type for options

If you want to browse all legal creatures for a strategy, you must open files **by first letter of name** and read their contents:

```
To find all legal lifegain creatures:
→ Open creature_a1.csv, creature_a2.csv — read for lifegain keywords/oracle text
→ Open creature_b1.csv, creature_b2.csv — read for lifegain
→ Continue through all letter files as needed
Do NOT assume a particular letter file = a particular theme.
```

### Why this matters

If you plan an Esper mill deck and write:
> "I'll load `creature_m.csv` for mill creatures and `instant_c.csv` for counterspells"

You will get:
- `creature_m1.csv` / `creature_m2.csv` = creatures whose names begin with M (Merfolk, Mulldrifter, etc.) — many will NOT be mill-related
- `instant_c.csv` = instants whose names begin with C — some will be counterspells, many will not

You will miss mill creatures whose names start with A, B, D, G, etc., and you will include non-counterspell instants starting with C.

**The letter is always and only the first letter of the card name.**

---

## MANDATORY GATE SYSTEM

You must complete each gate **in order**. You cannot proceed to the next gate until the current one is fully complete. There are no exceptions.

---

### ✅ GATE 1: DATABASE LOAD (Required before any card selection)

**Actions:**

1. Open `cards_by_category/_INDEX.md` — confirm you can read it
2. Identify all card types needed for the requested archetype
3. Open and load the specific letter CSV files for cards you are considering by **card name first letter**
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
2. Load the appropriate land letter files (by first letter of land name)
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
| Treating letter suffixes as thematic categories | Restart from Gate 1 |

ONE illegal card = ENTIRE DECK REJECTED.

---

## CARD DATABASE STRUCTURE

```
cards_by_category/
├── _INDEX.md              ← Open this first, always
├── artifact/
│   ├── artifact_a.csv     ← Artifacts starting with A
│   ├── artifact_b.csv     ← Artifacts starting with B
│   └── ...
├── battle/
│   └── battle_a.csv
├── creature/
│   ├── creature_a1.csv    ← Creatures starting with A (file 1 of 2)
│   ├── creature_a2.csv    ← Creatures starting with A (file 2 of 2)
│   ├── creature_b1.csv    ← Creatures starting with B (file 1 of 2)
│   └── ...
├── enchantment/
├── instant/
├── land/
├── other/
├── planeswalker/
└── sorcery/
```

**Pattern:** `cards_by_category/{type}/{type}_{first_letter_of_card_name}.csv`

Large letters (A, B, C, S, T, etc.) are split into numbered files (e.g., `creature_s1.csv` through `creature_s4.csv`). Always check `_INDEX.md` first to confirm which numbered files exist.

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
- `cards_by_category/creature/creature_s1.csv`  ← creatures starting with S
- `cards_by_category/instant/instant_c.csv`     ← instants starting with C
- `cards_by_category/land/land_f1.csv`          ← lands starting with F
[List ALL CSV files loaded, with first-letter note]

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
> 2. Load specific CSV files by the **first letter of the card name**, not by theme
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
| 8.1 | 2026-03-15 | Fix critical file-naming misconception: added explicit section clarifying letter suffixes are alphabetical (first letter of card name), NOT thematic categories; added wrong/correct examples; added "treating letters as themes" to zero-tolerance table |
| 8.0 | 2026-03-15 | Absolute adherence rewrite: hard-gated protocol, explicit card-naming prohibition, zero-tolerance table, mandatory CSV citation per card |
| 7.1 | 2026-03-10 | Fix directory name; add `battle` type; add validator flags/exit codes |
| 7.0 | 2026-03-09 | Consolidated all instructions into single file; added validation script integration |
| 6.0 | 2026-03-09 | Added mandatory database-first workflow; prohibited web search card selection |
| 5.0 | 2026-03-08 | Rebuilt for letter-split card database structure |

**Maintained by:** Celeannora
**Last updated:** March 15, 2026
