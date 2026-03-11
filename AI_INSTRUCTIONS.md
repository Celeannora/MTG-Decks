# AI DECK BUILDING INSTRUCTIONS

## ⚠️ STOP - READ THIS FIRST ⚠️

**Before doing ANYTHING, you MUST:**

1. 🚫 **STOP** - Do not suggest any cards yet
2. 📚 **LOAD DATABASE** - Open and load relevant CSV files from `cards_by_category/`
3. ✓ **VERIFY EACH CARD** - Check every single card against the loaded database
4. 📋 **ONLY USE DATABASE CARDS** - Never use web searches or memory for card selection

**If you skip this, you WILL generate illegal decks. This wastes time and violates the entire purpose of this repository.**

---

## CRITICAL LEGALITY ENFORCEMENT

### Zero Tolerance Policy

- **ONE illegal card = ENTIRE DECK REJECTED**
- Web sources contain rotated cards - they are FORBIDDEN for card selection
- The database is the ONLY source of truth for card legality
- Assumptions about card legality are PROHIBITED

### Mandatory Database-First Workflow

```
STEP 1: Load cards_by_category/ files
STEP 2: Build working list of available legal cards
STEP 3: Select cards ONLY from loaded database
STEP 4: Verify each card individually before adding to deck
STEP 5: Run validation script before finalizing
```

### Prohibited Actions

- ❌ Using web search results to find cards
- ❌ Copying decklists from external sources without validation
- ❌ Assuming a card is legal without database verification
- ❌ Building the deck before loading the database
- ❌ Trusting external sources over the database
- ❌ Mixing verified and unverified cards

---

## CARD DATABASE STRUCTURE

### File Organization

```
cards_by_category/
├── _INDEX.md              ← Start here - lists all files with sizes
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

### How to Find a Card

**Pattern:** `cards_by_category/{type}/{type}_{first_letter}.csv`

**Examples:**
- **Sheoldred, the Apocalypse** (creature, S) → `creature/creature_s1.csv` or `creature/creature_s2.csv`
- **Cut Down** (instant, C) → `instant/instant_c.csv`
- **Forest** (land, F) → `land/land_f1.csv` or `land/land_f2.csv`

**Pro tip:** Files are ≤80 KB. Open the specific letter file directly instead of scanning all files.
Always check `_INDEX.md` first to confirm which numbered file(s) exist for a given letter.

### CSV Columns

```
name, mana_cost, cmc, type_line, oracle_text, colors, color_identity,
rarity, set, set_name, collector_number, power, toughness, loyalty,
produced_mana, keywords
```

---

## DECK BUILDING METHODOLOGY

### Phase 0: Database Loading (MANDATORY)

**Execute BEFORE any card selection:**

1. Open `cards_by_category/_INDEX.md` to understand file structure
2. Identify which card types you need (creatures, instants, lands, etc.)
3. Load the specific letter files for cards you’re considering
4. Build a working list of available legal cards
5. **Document which files you loaded** for the analysis

### Phase 1: Card Pool Assessment

For each requested or considered card:

- **Format legality**: Verify in database (MANDATORY - reject if not found)
- **Power level**: Rate objectively (1-10)
- **Mana efficiency**: CMC vs. impact ratio
- **Synergy potential**: Does it enable a strategy or die alone?
- **Meta positioning**: Performance against tier 1 archetypes
- **Win condition role**: Does this card WIN games or just delay losses?

**If a requested card is not in database:** Inform user it’s illegal/rotated and suggest legal alternatives.

### Phase 2: Strategy Definition

- Define ONE primary win condition
- Identify the exact turn this deck aims to win
- Challenge the strategy ruthlessly - what disrupts it?
- **Only consider cards present in loaded database files**

### Phase 3: Card Selection

For every card slot ask:

- Why this card over all alternatives **in the database**?
- What does it do at each stage of the game?
- What happens if it’s removed or countered?

**Verification requirement:** Check each card exists in appropriate CSV before adding.

### Phase 4: Mana Base Construction

- Count colored pips, calculate requirements
- Determine land count using probability formulas
- Evaluate utility lands vs. entering tapped
- Validate curve support (enough early plays)
- **All lands must be in `cards_by_category/land/` files**

### Phase 5: Curve Analysis

- Build turn-by-turn gameplan for ideal draw
- Identify weakest turn and address it
- Confirm curve isn’t top-heavy

### Phase 6: Sideboard Construction

- Address top 5 meta archetypes
- Every sideboard card must answer a specific threat
- No card earns a slot because it “seems useful”
- **All 15 sideboard cards must be in database**

### Phase 7: Matchup Analysis

- Pre-board and post-board win rates vs. meta decks
- Identify hardest matchup and explain if unwinnable

### Phase 8: Self-Critique

Identify minimum 3 structural weaknesses. If none found, you haven’t looked hard enough.

### Phase 9: Final Validation

**FINAL LEGALITY CHECK** (perform individually for each card):

- [ ] All 60 mainboard cards verified in database
- [ ] All 15 sideboard cards verified in database
- [ ] Every card confirmed Standard-legal via database presence
- [ ] Set codes and collector numbers included (from database)
- [ ] Mana base math validated
- [ ] Curve distribution functional
- [ ] No cards from web searches or external decklists
- [ ] Validation script executed: `python scripts/validate_decklist.py Decks/[deck_name]/decklist.txt`

---

## OUTPUT FORMAT

### File Structure

**All decks save to `Decks/` subfolder:**

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

### analysis.md Required Sections

#### 1. Database Verification (MANDATORY)

```markdown
## Database Verification

### Files Loaded
- `cards_by_category/creature/creature_s1.csv`
- `cards_by_category/instant/instant_c.csv`
- `cards_by_category/land/land_f1.csv`
[List ALL CSV files loaded]

### Legality Confirmation
✓ All 60 mainboard cards verified present in database
✓ All 15 sideboard cards verified present in database

### Per-Card Verification (Representative Sample)
✓ Sheoldred, the Apocalypse - cards_by_category/creature/creature_s1.csv
✓ Cut Down - cards_by_category/instant/instant_c.csv
✓ Forest - cards_by_category/land/land_f1.csv
[List 10-15 key cards with source files]

### Rejected Cards
[If user requested illegal cards, list them here]
None - all suggested cards were Standard-legal.

### Validation Script Result
$ python scripts/validate_decklist.py Decks/2026-03-09_Archetype/decklist.txt
✅ VALIDATION PASSED
All cards are legal and present in the database.
```

#### 2. Executive Summary

- Archetype classification
- Primary win condition
- Format legality confirmation
- Expected metagame positioning

#### 3. Card-by-Card Breakdown

- Each card with quantity justification
- Alternatives considered from database
- Role in gameplan

#### 4. Mana Base Analysis

- Color requirements (pip counts)
- Land count mathematics
- Utility land justification

#### 5. Curve Analysis

- CMC distribution
- Turn-by-turn ideal gameplan
- Weakest turn identification

#### 6. Matchup Table

| Matchup | Pre-Board | Post-Board |
|---------|-----------|------------|
| Aggro   | 45%       | 55%        |
| Control | 60%       | 65%        |
| ...     | ...       | ...        |

#### 7. Weaknesses and Mitigations

Minimum 3 structural weaknesses with mitigation strategies.

#### 8. Playtesting Results

Theoretical goldfish analysis, critical turn identification.

### sideboard_guide.md Format

For each major matchup:

```markdown
## vs. [Archetype]

**Boarding:**
- Out: 2x Card A, 1x Card B
- In: 2x Sideboard Card X, 1x Sideboard Card Y

**Gameplan:** [Post-board strategy shift]

**Key Cards:** [Cards that win/lose the matchup]

**Critical Turns:** [When to deploy key threats/answers]
```

---

## VALIDATION SCRIPT USAGE

### Running the Validator

```bash
python scripts/validate_decklist.py Decks/2026-03-09_Orzhov_Lifegain/decklist.txt
```

### Flags

```bash
--quiet    # Print summary only (good for CI)
--verbose  # Print source CSV file for each valid card
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Validation passed |
| 1    | Illegal / unrecognised cards found |
| 2    | Decklist file not found |
| 3    | Deck count violation (wrong 60/15/4-copy counts) |

### Expected Output

**Success:**

```
✅ VALIDATION PASSED
All cards are legal and present in the database.
```

**Failure:**

```
❌ VALIDATION FAILED
Found 3 illegal card(s):
  • 4x Thoughtseize (mainboard)
  • 2x Fatal Push (sideboard)
  • 1x Polluted Delta (mainboard)
```

### Offline Validation (faster)

```bash
# Build local index once
python scripts/build_local_database.py

# Then validate without loading all CSVs
python scripts/validate_decklist_local.py Decks/my_deck/decklist.txt
```

---

## COMMON MISTAKES & CORRECTIONS

| ❌ Wrong | ✓ Correct |
|----------|----------|
| "I'll search for cards online" | "I'll load the database first" |
| "This card is probably legal" | "Let me verify in the CSV" |
| "I'll build then validate" | "I'll validate as I build" |
| "Web sources say it's good" | "Does it exist in database?" |
| "I'm 99% sure it's legal" | "I must verify in database" |
| "I'll add this cool card I remember" | "Is this card in the loaded CSV?" |

---

## RED FLAGS - STOP IMMEDIATELY IF YOU CATCH YOURSELF

1. 🚩 Adding cards without checking database first
2. 🚩 Searching "best Standard cards" online
3. 🚩 Copying decklists from websites
4. 🚩 Assuming cards are legal because "they should be"
5. 🚩 Planning to validate after deck is complete
6. 🚩 Using memory/knowledge instead of database

**If you catch any of these: STOP, load database, start over with database-first approach.**

---

## WHEN DATABASE IS INACCESSIBLE

1. **STOP IMMEDIATELY** - do not proceed with deck building
2. Inform user database is unavailable
3. Request direct confirmation for each card:
   - Card name, mana cost, type line, oracle text, power/toughness
   - Explicit confirmation card is Standard-legal
4. Note in analysis.md: "Card legality user-confirmed due to database access issue"
5. Still verify as many cards as possible once database becomes accessible

---

## IF USER REQUESTS ILLEGAL CARDS

**Response template:**

> "I checked the database and [Card Name] is not present in `cards_by_category/`. This means it’s not currently Standard-legal (likely rotated).
>
> Legal alternatives from the database:
> - [Alternative 1] (similar effect)
> - [Alternative 2] (similar role)
> - [Alternative 3] (synergy match)
>
> Would you like me to use one of these instead?"

**Never include illegal cards even if user insists** - the database is authoritative.

---

## SESSION ACKNOWLEDGMENT

**All AI sessions helping with deck building MUST acknowledge:**

"I acknowledge that I will ONLY suggest cards verified to exist in the Celeannora/MTG-Decks repository. I will search the database BEFORE making ANY card suggestions. I will NOT use general MTG knowledge without database verification. I will run the validation script before finalizing any deck."

---

## PHILOSOPHY

Every card choice is mathematically justified. Every strategic decision is rigorously challenged. No deck is published without surviving brutal self-critique.

**Format legality is non-negotiable.** A brilliant deck with illegal cards is worthless.

**Failure is acceptable. Unjustified mediocrity is not. Illegal cards are unacceptable.**

---

## VERSION HISTORY

| Version | Date | Notes |
|---------|------|-------|
| 7.1 | 2026-03-10 | Fix directory name (removed space); add `battle` type; fix AI engine reference; add validator flags/exit codes; fix example cards to current Standard references |
| 7.0 | 2026-03-09 | Consolidated all instructions into single file; added validation script integration; enhanced enforcement protocols |
| 6.0 | 2026-03-09 | Added mandatory database-first workflow; prohibited web search card selection |
| 5.0 | 2026-03-08 | Rebuilt for letter-split card database structure |

**Maintained by:** Celeannora  
**Last updated:** March 10, 2026
