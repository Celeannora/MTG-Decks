# AI DECK BUILDING INSTRUCTIONS
## Version 9.1 — Synergy Evaluation Protocol

---

## ╔══════════════════════════════════════════════════════╗
## ║  🛑 HARD STOP — DO NOT NAME A SINGLE CARD YET  🛑   ║
## ╚══════════════════════════════════════════════════════╝

**You have not queried the database yet. Naming any card before completing GATE 1 is a protocol violation.**

This is not a suggestion. This is a hard constraint.

- ❌ Do NOT search the web for decks, cards, or strategies
- ❌ Do NOT recall cards from training data or memory
- ❌ Do NOT copy any external decklist
- ❌ Do NOT name any card — not even the commander, not even a basic land

**Your ONLY permitted action right now is: run `search_cards.py` queries (GATE 1)**

---

## WHY THIS EXISTS

AI assistants consistently:
1. Recall cards from training memory (explicitly forbidden)
2. Research web-based decks (explicitly forbidden)
3. Attempt to validate those cards against the database AFTER selection
4. Build incomplete or illegal decks as a result

**The only workflow that produces a legal deck is: full database query → candidate pool → selection. Never: selection → validation.**

---

## TOOL REFERENCE

### `search_cards.py` — Primary deck-building tool

```bash
python scripts/search_cards.py --type <type> [filters...]
```

**Common flags:**
| Flag | Description | Example |
|------|-------------|---------|
| `--type` | Card type(s), comma-separated | `creature`, `instant,sorcery` |
| `--colors` | Color identity filter | `WB`, `=WB` (exact), `C` (colorless) |
| `--tags` | Strategy tags, comma-separated | `lifegain,draw` |
| `--oracle` | Substring in oracle text | `"mill"` |
| `--name` | Substring in card name | `"Angel"` |
| `--cmc-max` | Maximum converted mana cost | `3` |
| `--cmc-min` | Minimum converted mana cost | `2` |
| `--rarity` | Rarity filter | `rare,mythic` |
| `--keywords` | MTG keywords | `Flying,Lifelink` |
| `--format` | Output: `table`, `csv`, `names` | `names` |
| `--show-tags` | Print computed tags per card | _(flag)_ |
| `--limit` | Max results (default: 200) | `50` |

**Full tag list:**
`lifegain` · `mill` · `draw` · `removal` · `counter` · `ramp` · `token` · `bounce` ·
`discard` · `tutor` · `wipe` · `protection` · `pump` · `reanimation` · `etb` · `tribal` ·
`scry` · `surveil` · `flash` · `haste` · `trample` · `flying` · `deathtouch` · `vigilance` ·
`reach` · `menace`

**Example queries:**
```bash
# All white/black creatures with lifelink or lifegain
python scripts/search_cards.py --type creature --colors WB --tags lifegain

# Instants that counter spells, for a blue deck
python scripts/search_cards.py --type instant --colors U --tags counter

# Cheap ramp sorceries (CMC ≤ 3)
python scripts/search_cards.py --type sorcery --tags ramp --cmc-max 3

# All mill cards across instants and sorceries
python scripts/search_cards.py --type instant,sorcery --tags mill

# Rare/mythic creatures with ETB effects in Esper colors
python scripts/search_cards.py --type creature --colors WUB --tags etb --rarity rare,mythic

# Land search for a specific color pair
python scripts/search_cards.py --type land --colors WB

# Find a specific card by name
python scripts/search_cards.py --name "Sheoldred"
```

### `validate_decklist.py` — Legality checker

```bash
# Default — reads cards_by_category/ CSVs directly (no setup needed)
python scripts/validate_decklist.py Decks/my_deck/decklist.txt

# Faster offline backends (run build_local_database.py first)
python scripts/validate_decklist.py --db json Decks/my_deck/decklist.txt
python scripts/validate_decklist.py --db sqlite Decks/my_deck/decklist.txt

# Flags: --quiet (summary only) · --verbose (source CSV per card) · --strict (land warnings) · --show-tags
```

| Exit Code | Meaning |
|-----------|---------|
| 0 | Validation passed |
| 1 | Illegal / unrecognised cards found |
| 2 | Decklist file not found |
| 3 | Deck count violation (wrong 60/15/4-copy counts) |

### `index_decks.py` — Deck registry

```bash
python scripts/index_decks.py
```

Regenerates `Decks/_INDEX.md` with a searchable table of all published decks.

---

## MANDATORY GATE SYSTEM

Complete each gate **in order** and **in full**.

---

### ✅ GATE 1: DATABASE QUERY (Required before any card is named)

Use `search_cards.py` to build a complete candidate pool. Run **multiple queries**
to cover all card types you need. Do not skip any type you plan to use.

**Step 1: Identify needed card types from your archetype**

| If building... | You need to query... |
|----------------|----------------------|
| Aggro creature deck | `creature`, `instant` (removal), `land` |
| Control | `instant` (counter/removal), `creature`, `sorcery` (wipes), `land` |
| Mill | `instant,sorcery` (mill), `creature`, `enchantment`, `land` |
| Lifegain | `creature` (lifegain), `instant,sorcery` (lifegain), `enchantment`, `land` |
| Tribal | `creature` (tribe), `instant,sorcery,enchantment` (support), `land` |

**Step 2: Run `search_cards.py` for each needed type**

Run one or more queries per card type. Combine filters for precision.
Record every candidate card returned: name, mana cost, set, collector number, source file.

**Step 3: Ask clarifying questions if archetype is ambiguous**

If the requested archetype could go in multiple directions, ask before building:
- What is the primary win condition? (combat damage, mill, lifegain drain, combo?)
- What color(s) are preferred?
- Budget constraint? (any rarity / rare+mythic only / budget commons+uncommons)
- Target speed? (aggressive turn 4-5 wins / midrange turn 6-7 / control turn 8+)
- Any must-include cards?

**Step 4: Document your candidate pool**

List each query run and the number of candidates found, e.g.:
```
Queries run:
  search_cards.py --type creature --colors WB --tags lifegain,etb   → 47 candidates
  search_cards.py --type instant --colors WB --tags removal          → 28 candidates
  search_cards.py --type enchantment --colors WB --tags lifegain      → 19 candidates
  search_cards.py --type land --colors WB                             → 89 candidates
```

**Gate 1 is complete ONLY when:**
- Every needed card type has been queried
- A complete candidate pool exists from those queries
- Zero cards have been named from memory or web sources

---

### ✅ GATE 2: STRATEGY DEFINITION (Required before any card slot is filled)

Using only cards from your Gate 1 candidate pool:

1. Define ONE primary win condition
2. Identify the target win turn
3. Map card types needed to execute that win condition
4. Confirm all needed roles (win con, support, interaction, ramp, lands) have candidates
5. Identify cards that create **meaningful interactions** (not just individually good cards)

**Interaction checklist:**
- Does the win condition card synergize with 3+ other cards in the pool?
- Do support cards enable multiple win conditions or have standalone value?
- Is there a coherent backup plan if the primary win con is disrupted?

**Gate 2 is complete when:** Strategy is fully defined using database-confirmed cards only.

---

### ✅ GATE 2.5: SYNERGY EVALUATION (Required before card slots are filled)

Using the candidate pool from Gate 1 and the strategy from Gate 2, evaluate pairwise card synergies for every candidate under serious consideration. This gate replaces vague claims of "good synergy" with a structured, auditable assessment.

**This gate applies identically to every archetype. The synergy types and thresholds below are mechanical — they describe how cards interact, not what strategy they serve.**

#### Step 1: Classify Pairwise Interactions

For each pair of candidates being considered for inclusion, determine whether a directional interaction exists. An interaction is exactly one of:

| Type | Definition | How to Identify |
|------|-----------|----------------|
| `ENABLES` | A makes B functional, cheaper, or castable | A produces mana B needs; A meets a condition B checks; A reduces B's cost |
| `TRIGGERS` | A causes B's triggered/activated ability to fire | A's action (casting, entering, attacking, gaining life, etc.) matches B's trigger condition |
| `AMPLIFIES` | A multiplies or scales B's output | A doubles counters B places; A adds to a quantity B already produces; A copies B |
| `PROTECTS` | A defends B from removal or disruption | A counters spells targeting B; A grants hexproof/indestructible/ward to B |
| `FEEDS` | A's output becomes B's input | A produces resource X (life, tokens, counters, cards in graveyard); B consumes or cares about resource X |
| `REDUNDANT` | A and B fill the same role with diminishing returns when drawn together | Two cards that both serve as finisher, board wipe, or narrow answer — drawing both is worse than drawing one plus a different role |

**Rules for classification:**
- A card can interact with the same partner through multiple types (e.g., A both TRIGGERS and FEEDS B). Count each type once.
- Generic "both are good cards" is not a synergy. The interaction must be mechanical — traceable to specific oracle text, keywords, or type lines.
- Use the oracle text and tags from your Gate 1 query results. Do not reason about cards from memory.

#### Step 2: Score Each Candidate

For every candidate card being considered for a mainboard slot, record three scores:

| Metric | Definition | How to Calculate |
|--------|-----------|------------------|
| **Synergy Count** | Number of other candidates this card has at least one non-REDUNDANT interaction with | Count distinct partner cards |
| **Role Breadth** | Number of distinct interaction types this card participates in | Count how many of ENABLES / TRIGGERS / AMPLIFIES / PROTECTS / FEEDS apply across all partners |
| **Dependency** | Number of other specific cards that must be on the battlefield for this card to function at all | 0 = standalone value; 1 = needs one enabler; 2+ = highly conditional |

Output a summary table sorted by Synergy Count descending:

```markdown
### Synergy Scores

| Card | Synergy Count | Role Breadth | Dependency | Notes |
|------|--------------|-------------|------------|-------|
| [Highest-synergy card] | N | N | N | [1-line: which types, which key partners] |
| ... | ... | ... | ... | ... |
| [Lowest-synergy card] | N | N | N | ... |
```

#### Step 3: Apply Thresholds

Before proceeding to Gate 3, the candidate list must satisfy all of the following. These apply regardless of archetype:

1. **Average Synergy Count across all non-land candidates ≥ 3.0** — Every card interacts mechanically with at least 3 others on average. A deck of individually powerful but disconnected cards fails this.

2. **No more than 4 non-land cards with Synergy Count 0–1** — These are "good stuff" inclusions with no mechanical ties to the rest of the deck. A small number is acceptable (e.g., a universally strong removal spell). More than 4 means the deck lacks cohesion.

3. **At least 2 cards with Synergy Count ≥ 8** — These are the "hub" cards that tie the deck together. Every archetype needs at least two high-connectivity cards. If the deck has only one, losing it collapses the entire strategy.

4. **No card with Dependency ≥ 3 makes the final cut** — A card that needs 3+ other specific cards on board to function is too fragile for competitive play. Either find a less conditional alternative from the candidate pool, or rethink the strategy.

5. **Every REDUNDANT pair is acknowledged** — If two cards are flagged REDUNDANT, justify why both deserve slots (e.g., "4 copies of the effect is needed for consistency" or "one is better in early game, the other in late game"). If no justification exists, cut one.

**If any threshold is not met:**
- Revisit the candidate pool from Gate 1
- Run additional `search_cards.py` queries if the pool lacks high-synergy options
- Adjust the strategy (Gate 2) if the archetype fundamentally lacks internal synergy in the available card pool
- Document which threshold failed and how you resolved it

#### Step 4: Map Synergy Chains

Identify the 2–3 most important multi-card sequences that execute the deck's game plan. A chain is an ordered sequence of cards where each card's output feeds the next card's input.

```markdown
### Synergy Chains

**Chain 1 — [Name describing function, e.g., "Primary Win Condition"]:**
[Card A] → [what A produces] → [Card B] → [what B produces] → [Card C] → [outcome]
Redundancy: [which pieces have substitutes in the candidate pool]
Minimum pieces to function: [N of M]

**Chain 2 — [Name, e.g., "Defensive Engine" or "Card Advantage Loop"]:**
[Card X] → ... → [outcome]
Redundancy: ...
Minimum pieces to function: ...
```

Each chain must meet two requirements:
- **Redundancy**: At least one piece in the chain has a substitute in the deck (e.g., if Card B is removed, Card B2 can fill the same role). Chains with zero redundancy are single points of failure.
- **Graceful degradation**: The chain still produces value (at reduced output) with one piece missing. If removing any single card makes the chain do nothing, the chain is too fragile.

#### Gate 2.5 Completion Criteria

- [ ] All candidates scored (Synergy Count, Role Breadth, Dependency)
- [ ] Average Synergy Count ≥ 3.0
- [ ] ≤ 4 cards with Synergy Count 0–1
- [ ] ≥ 2 hub cards with Synergy Count ≥ 8
- [ ] No card with Dependency ≥ 3
- [ ] All REDUNDANT pairs justified
- [ ] 2–3 synergy chains mapped with redundancy and degradation noted
- [ ] All analysis based on Gate 1 query results (oracle text, tags, keywords) — not memory

**If any item is unchecked, do not proceed to Gate 3.**

---

### ✅ GATE 3: CARD SELECTION (From candidate pool only)

For each card slot:

1. **Name the card** — from your Gate 1 candidate pool only
2. **State the source file** (e.g., `cards_by_category/creature/creature_s1.csv`)
3. **Record mana cost, type line, set code, collector number** from the query output
4. **Justify inclusion** — what interaction or role does this card fill?

**If you cannot cite a source file and query for a card, do not include it. Full stop.**

Cards that fail Gate 3:
- Cards recalled from memory without a query citation → **REJECTED**
- Cards found via web search → **REJECTED**
- Cards "assumed" to be legal → **REJECTED**

---

### ✅ GATE 4: MANA BASE

1. Count colored pips across your mainboard
2. Run: `python scripts/search_cards.py --type land --colors <your_colors>`
3. Select dual lands, triomes, utility lands with citations
4. Validate that the curve is supported (enough early sources for 1-2 drop plays)

---

### ✅ GATE 5: SIDEBOARD

Run targeted queries for sideboard roles:
```bash
# Graveyard hate
python scripts/search_cards.py --type instant,enchantment --tags graveyard --oracle "exile"

# Additional removal
python scripts/search_cards.py --type instant --colors <yours> --tags removal --cmc-max 3

# Counter magic
python scripts/search_cards.py --type instant --colors <yours> --tags counter
```

All 15 sideboard cards must have query citations.

---

### ✅ GATE 6: FINAL VALIDATION CHECKLIST

Before writing any output files:

- [ ] All needed card types were queried (Gate 1 queries documented)
- [ ] All 60 mainboard cards have a cited source file
- [ ] All 15 sideboard cards have a cited source file
- [ ] Zero cards sourced from web searches or memory
- [ ] Set codes and collector numbers recorded
- [ ] Mana base math validated
- [ ] Synergy evaluation completed (Gate 2.5 thresholds met, chains documented)
- [ ] Meaningful card interactions documented
- [ ] Validation script run: `python scripts/validate_decklist.py Decks/[deck_name]/decklist.txt`
- [ ] Validation script returned exit code 0

**If any item is unchecked, do not output the deck.**

---

## LEGAL VALIDATION — THE CORE RULE

> **A card is legal if and only if it appears in `cards_by_category/`.**
>
> - Found in database ✅ → Legal
> - Not found in database ❌ → Illegal (rotated, banned, or nonexistent)
> - "Probably legal" → Does not exist. Verify or reject.
> - Web source says it's legal → Irrelevant. Verify in database or reject.
> - You remember it being legal → Irrelevant. Verify in database or reject.

---

## PROHIBITED ACTIONS (Zero Tolerance)

| Action | Consequence |
|--------|-------------|
| Naming any card before completing Gate 1 | Restart from Gate 1 |
| Using web search results to select cards | Restart from Gate 1 |
| Copying any external decklist | Restart from Gate 1 |
| Adding a card without a query citation | Remove card, find database alternative |
| Assuming card legality without verification | Restart from Gate 1 |
| Building deck then validating after | Restart from Gate 1 |
| Skipping Gate 2.5 synergy evaluation | Return to Gate 2.5 before proceeding |

ONE illegal card = ENTIRE DECK REJECTED.

---

## CARD DATABASE STRUCTURE

Total card pool (from `cards_by_category/_INDEX.md`):
- **Artifact**: ~1,012 cards (artifact_a – artifact_w)
- **Creature**: ~6,345 cards (creature_a1 – creature_z)
- **Enchantment**: ~1,048 cards (enchantment_a – enchantment_z)
- **Instant**: ~1,359 cards (instant_a – instant_z)
- **Land**: ~6,082 cards (land_a – land_w)
- **Planeswalker**: ~103 cards
- **Sorcery**: ~1,101 cards (sorcery_a – sorcery_z)

**`search_cards.py` reads all files automatically.** You do not need to open individual CSVs.

### CSV Columns

```
name, mana_cost, cmc, type_line, oracle_text, colors, color_identity,
rarity, set, set_name, collector_number, power, toughness, loyalty,
produced_mana, keywords, tags
```

The `tags` column contains pre-computed strategic tags (semicolon-separated),
e.g. `draw;etb;lifegain`. These are the same tags used by `search_cards.py --tags`.

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

#### 1. Database Query Report (MANDATORY — must appear first)

```markdown
## Database Query Report

### Queries Run

| Query | Results |
|-------|---------|
| `search_cards.py --type creature --colors WB --tags lifegain` | 47 candidates |
| `search_cards.py --type instant --colors WB --tags removal` | 28 candidates |
| `search_cards.py --type land --colors WB` | 89 candidates |
[... all queries listed]

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
#### 3. Card-by-Card Breakdown (with interaction justifications)
#### 4. Mana Base Analysis
#### 5. Curve Analysis
#### 6. Matchup Table
#### 7. Weaknesses and Mitigations
#### 8. Playtesting Notes

---

## WHEN A REQUESTED CARD IS NOT IN THE DATABASE

> "I queried `cards_by_category/` and [Card Name] was not returned by any search.
> It is not Standard-legal.
>
> Legal alternatives found during my database queries:
> - [Alternative 1] — `cards_by_category/[file]`
> - [Alternative 2] — `cards_by_category/[file]`
>
> Would you like to use one of these instead?"

**Never include the illegal card even if the user insists.** The database is authoritative.

---

## SESSION ACKNOWLEDGMENT

Every AI session must begin with this acknowledgment **before any other action:**

> "I acknowledge this repository's database-first protocol. I will:
> 1. Use `search_cards.py` to query the database before naming any card
> 2. Build my candidate pool exclusively from query results
> 3. Cite the source file for every card I suggest
> 4. Reject any card not returned during my database queries
> 5. Run the validation script before finalizing any deck
> 6. Ask clarifying questions if the archetype or strategy is ambiguous
>
> I will not name a single card until Gate 1 (database queries) is complete."

---

## PHILOSOPHY

Every card choice is mathematically justified. Every strategic decision is rigorously
challenged. Cards must form **meaningful interactions** — a deck of individually strong
cards is weaker than a deck with deliberate synergy chains.

**Format legality is non-negotiable.** A brilliant deck with illegal cards is worthless.

**Failure is acceptable. Unjustified mediocrity is not. Illegal cards are unacceptable.**

The database is the only source of truth.
Workflow runs one direction only: database query → candidate pool → card selection.

---

## VERSION HISTORY

| Version | Date | Notes |
|---------|------|-------|
| 9.1 | 2026-04-03 | Added Gate 2.5 (Synergy Evaluation): mandatory pairwise synergy classification, scoring (Synergy Count, Role Breadth, Dependency), universal thresholds, and synergy chain mapping before card selection; added synergy evaluation section to analysis.md template; added Gate 2.5 skip to prohibited actions table |
| 9.0 | 2026-03-21 | Search-first protocol: replaced manual file-sweep with `search_cards.py`; added strategic tags column to CSV schema; unified validators into single script with `--local` flag; added `index_decks.py` for deck registry; removed deprecated stub files; CI now re-validates all decks on database changes; added clarifying questions to Gate 1; added interaction justification requirement to Gate 3 |
| 8.2 | 2026-03-15 | Mandate exhaustive full-database sweep: ALL files for each needed card type must be opened before any selection; added partial-loading prohibition to zero-tolerance table; added file-opened checklist to Gate 1 |
| 8.1 | 2026-03-15 | Fix critical file-naming misconception: letters are alphabetical, NOT thematic categories |
| 8.0 | 2026-03-15 | Absolute adherence rewrite: hard-gated protocol, explicit card-naming prohibition, zero-tolerance table, mandatory CSV citation per card |
| 7.1 | 2026-03-10 | Fix directory name; add `battle` type; add validator flags/exit codes |
| 7.0 | 2026-03-09 | Consolidated all instructions into single file |

**Maintained by:** Celeannora
**Last updated:** April 3, 2026
