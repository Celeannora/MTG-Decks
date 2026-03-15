# AI DECK BUILDING INSTRUCTIONS
## Version 8.2 — Absolute Adherence Protocol

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
4. Open only one or two CSV files and treat that as a complete database review

All of these approaches produce incomplete or illegal decks. The database is the **only source of truth**. Every file for every needed card type must be opened and read before any card is selected.

**The only workflow that produces a legal deck is: full database sweep → card pool → selection. Never: selection → validation.**

---

## ⚠️ CRITICAL: HOW THE FILE NAMING SYSTEM WORKS ⚠️

### The letters in filenames are ALPHABETICAL — NOT thematic

The `_{letter}` suffix refers to the **first letter of the card name**. Nothing else.

| Filename | Contains |
|----------|----------|
| `creature/creature_h1.csv` | Creatures whose names start with the letter **H** |
| `creature/creature_l1.csv` | Creatures whose names start with the letter **L** |
| `creature/creature_m1.csv` | Creatures whose names start with the letter **M** |
| `instant/instant_c.csv` | Instants whose names start with the letter **C** |
| `land/land_s1.csv` | Lands whose names start with the letter **S** |

### ❌ WRONG — Do not do this

```
# INCORRECT - letters do NOT mean themes:
Creatures: H (lifegain), L (lifegain), M (mill), D (drain)
Instants: C, D, H, L, M, S, T (counterspells, removal, lifegain, mill)
Lands: D, H, I, S, T (dual/triome lands for Esper)
```

H does not mean lifegain. M does not mean mill. D does not mean drain.

### ❌ ALSO WRONG — Partial loading

```
# INCORRECT - opening only a few files is not a database review:
"I'll open creature_s1.csv and creature_b1.csv to find my creatures."
```

This misses every relevant creature starting with A, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, T, U, V, W, X, Y, Z. You cannot build a best-possible deck from a fraction of the available card pool.

### ✅ CORRECT — Exhaustive sweep by card type

For each card type you need, open **every file** for that type listed in `_INDEX.md`, read its contents, and extract relevant cards before moving on.

---

## MANDATORY GATE SYSTEM

You must complete each gate **in order** and **in full**. Partial completion is not completion.

---

### ✅ GATE 1: EXHAUSTIVE DATABASE SWEEP (Required before any card selection)

This gate requires opening **every CSV file** for each card type you need. Not some files. Not the likely files. **Every file.**

**Step 1: Identify needed card types**

Based on the requested archetype, list which card types you will need:
- Creatures? → Must open ALL creature files (creature_a1 through creature_z)
- Instants? → Must open ALL instant files (instant_a through instant_z)
- Sorceries? → Must open ALL sorcery files
- Enchantments? → Must open ALL enchantment files
- Artifacts? → Must open ALL artifact files
- Planeswalkers? → Must open ALL planeswalker files
- Lands? → Must open ALL land files
- Other? → Must open ALL other files

**Step 2: Open every file for each needed type**

For each card type identified above:
1. Check `_INDEX.md` for the complete file list for that type
2. Open **every file** in that type's folder
3. Read each file and extract cards relevant to your strategy (filter by `oracle_text`, `keywords`, `colors`, `color_identity`)
4. Record each candidate card with: name, mana cost, set, collector number, and source CSV filename

**Step 3: Build the complete candidate pool**

After opening all files for all needed types, you have a complete candidate pool. Only then may you proceed to Gate 2.

**Step 4: Document completion**

Write a checklist confirming every file was opened, e.g.:
```
Creature files opened: creature_a1 ✓, creature_a2 ✓, creature_b1 ✓, creature_b2 ✓,
creature_c1 ✓, creature_c2 ✓, creature_d1 ✓, creature_d2 ✓, creature_e ✓,
creature_f1 ✓, creature_f2 ✓, creature_g1 ✓, creature_g2 ✓, creature_h1 ✓,
creature_h2 ✓, creature_i ✓, creature_j ✓, creature_k ✓, creature_l1 ✓,
creature_l2 ✓, creature_m1 ✓, creature_m2 ✓, creature_n ✓, creature_o ✓,
creature_p ✓, creature_q ✓, creature_r1 ✓, creature_r2 ✓, creature_s1 ✓,
creature_s2 ✓, creature_s3 ✓, creature_s4 ✓, creature_t1 ✓, creature_t2 ✓,
creature_u ✓, creature_v ✓, creature_w ✓, creature_x ✓, creature_y ✓,
creature_z ✓

Instant files opened: instant_a ✓, instant_b ✓, instant_c ✓, instant_d ✓ ...
[etc. for every type used]
```

**Gate 1 is complete ONLY when:**
- Every file for every needed card type has been opened and read
- A complete candidate pool exists drawn exclusively from those files
- The file-opened checklist above is written out
- Zero cards have been named from memory or web sources

**If `cards_by_category/` is inaccessible:** STOP. Inform the user. Do not proceed.

---

### ✅ GATE 2: STRATEGY DEFINITION (Required before any card slot is filled)

Using only cards confirmed present in the Gate 1 candidate pool:

1. Define ONE primary win condition
2. Identify the target win turn
3. Identify the card types needed to execute that win condition
4. Confirm all needed cards exist in your candidate pool

**Gate 2 is complete when:**
- Strategy is fully defined using database-confirmed cards only
- No card slot has been assigned yet

---

### ✅ GATE 3: CARD SELECTION (One card at a time, from candidate pool only)

For each card slot:

1. **Name the card** — pulled from your Gate 1 candidate pool only
2. **State the CSV file it came from** (e.g., `cards_by_category/creature/creature_s1.csv`)
3. **Record its mana cost, type line, and set code** from the CSV row
4. Only then add it to the decklist

**If you cannot cite a CSV file and row for a card, do not include it. Full stop.**

Cards that fail Gate 3:
- Cards recalled from memory without CSV citation → **REJECTED**
- Cards found via web search → **REJECTED**
- Cards "assumed" to be legal → **REJECTED**
- Cards not in the Gate 1 candidate pool → **REJECTED**

---

### ✅ GATE 4: MANA BASE (Exhaustive land sweep)

1. Count colored pips across your mainboard
2. Open **every land file** in `cards_by_category/land/` (land_a through land_w — check `_INDEX.md` for full list)
3. Extract all dual lands, triomes, utility lands relevant to your color identity
4. Select lands with CSV citations
5. Validate curve support

Do not open only a few land files. All land files must be checked.

---

### ✅ GATE 5: SIDEBOARD (Exhaustive sweep for sideboard options)

Repeat the relevant type sweeps from Gate 1 if not already complete. All 15 sideboard cards must have CSV citations.

---

### ✅ GATE 6: FINAL VALIDATION CHECKLIST

Before writing any output files, confirm every item:

- [ ] All files for all needed card types were opened (Gate 1 checklist complete)
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

| Action | Consequence |
|--------|-------------|
| Naming any card before completing Gate 1 | Restart from Gate 1 |
| Opening only some files for a card type | Restart Gate 1 for that type |
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

Total card pool (from `_INDEX.md`):
- **Artifact**: 1,012 cards across 23 files (artifact_a – artifact_w)
- **Battle**: files exist for some letters
- **Creature**: 6,345 cards across 40 files (creature_a1 through creature_z)
- **Enchantment**: 1,048 cards across 22 files (enchantment_a – enchantment_z)
- **Instant**: 1,359 cards across 25 files (instant_a – instant_z)
- **Land**: 6,082 cards across 33 files (land_a – land_w, some letters split into 4 files)
- **Other**: 20 cards across 14 files
- **Planeswalker**: 103 cards across 12 files
- **Sorcery**: 1,101 cards across 24 files (sorcery_a – sorcery_z)

```
cards_by_category/
├── _INDEX.md              ← Open this first. Lists EVERY file with card counts.
├── artifact/              ← 23 files, all must be opened if using artifacts
├── battle/
├── creature/              ← 40 files, all must be opened if using creatures
├── enchantment/           ← 22 files, all must be opened if using enchantments
├── instant/               ← 25 files, all must be opened if using instants
├── land/                  ← 33 files, ALL must be opened for mana base
├── other/
├── planeswalker/          ← 12 files, all must be opened if using planeswalkers
└── sorcery/               ← 24 files, all must be opened if using sorceries
```

**Pattern:** `cards_by_category/{type}/{type}_{first_letter_of_card_name}.csv`

Large letters are split into numbered files (e.g., `creature_s1.csv` through `creature_s4.csv`). Always check `_INDEX.md` to confirm all split files for a letter.

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

#### 1. Database Sweep Report (MANDATORY — must appear first)

```markdown
## Database Sweep Report

### Files Opened

Creature files (40 total):
creature_a1 ✓, creature_a2 ✓, creature_b1 ✓, creature_b2 ✓, creature_c1 ✓,
creature_c2 ✓, creature_d1 ✓, creature_d2 ✓, creature_e ✓, creature_f1 ✓,
creature_f2 ✓, creature_g1 ✓, creature_g2 ✓, creature_h1 ✓, creature_h2 ✓,
creature_i ✓, creature_j ✓, creature_k ✓, creature_l1 ✓, creature_l2 ✓,
creature_m1 ✓, creature_m2 ✓, creature_n ✓, creature_o ✓, creature_p ✓,
creature_q ✓, creature_r1 ✓, creature_r2 ✓, creature_s1 ✓, creature_s2 ✓,
creature_s3 ✓, creature_s4 ✓, creature_t1 ✓, creature_t2 ✓, creature_u ✓,
creature_v ✓, creature_w ✓, creature_x ✓, creature_y ✓, creature_z ✓

Instant files (25 total):
instant_a ✓, instant_b ✓, instant_c ✓, ... [all files listed]

[Repeat for every card type used]

### Per-Card Verification (ALL 60+15 cards)
✓ [Card Name] — [cards_by_category/type/file.csv] — (SET) Collector#
[Every single card listed with source file and set info]

### Rejected Cards
[Cards considered but not found in database — name and reason]

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

> "I checked all files in `cards_by_category/` and [Card Name] is not present. It is not Standard-legal.
>
> Legal alternatives found during my full database sweep:
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
> 2. Open **every CSV file** for each card type I need — not just some files
> 3. Build my candidate pool exclusively from those files before selecting any card
> 4. Cite the source CSV for every card I suggest
> 5. Reject any card not found during my full database sweep
> 6. Run the validation script before finalizing any deck
>
> I will not name a single card until Gate 1 (full sweep) is complete."

---

## PHILOSOPHY

Every card choice is mathematically justified. Every strategic decision is rigorously challenged. No deck is published without surviving brutal self-critique.

**Format legality is non-negotiable.** A brilliant deck with illegal cards is worthless.

**Failure is acceptable. Unjustified mediocrity is not. Illegal cards are unacceptable.**

The database is the only source of truth. The workflow runs one direction only: full database sweep → candidate pool → card selection.

---

## VERSION HISTORY

| Version | Date | Notes |
|---------|------|-------|
| 8.2 | 2026-03-15 | Mandate exhaustive full-database sweep: ALL files for each needed card type must be opened before any selection; added partial-loading prohibition to zero-tolerance table; added file-opened checklist to Gate 1 and analysis.md output; updated card type file counts from _INDEX.md |
| 8.1 | 2026-03-15 | Fix critical file-naming misconception: letters are alphabetical (first letter of card name), NOT thematic categories |
| 8.0 | 2026-03-15 | Absolute adherence rewrite: hard-gated protocol, explicit card-naming prohibition, zero-tolerance table, mandatory CSV citation per card |
| 7.1 | 2026-03-10 | Fix directory name; add `battle` type; add validator flags/exit codes |
| 7.0 | 2026-03-09 | Consolidated all instructions into single file; added validation script integration |
| 6.0 | 2026-03-09 | Added mandatory database-first workflow; prohibited web search card selection |
| 5.0 | 2026-03-08 | Rebuilt for letter-split card database structure |

**Maintained by:** Celeannora
**Last updated:** March 15, 2026
