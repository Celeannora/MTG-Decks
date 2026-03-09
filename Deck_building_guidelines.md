# Deck building guidelines

Quick reference for AI assistants. For the full methodology see `Deck_builder_instructions.md`.

---

## 🚨 LEGALITY ENFORCEMENT 🚨

**ZERO TOLERANCE POLICY**: Any deck with illegal cards is automatically rejected.

### Database-first workflow (MANDATORY)

```
1. Load database → 2. Verify cards → 3. Build deck → 4. Final verification
```

### Prohibited practices

- ❌ Using web search results to find cards
- ❌ Copying decklists from external sources without validation
- ❌ Assuming a card is legal without database check
- ❌ Building first, validating later
- ❌ Trusting external sources over database

### Correct approach

1. Load relevant CSV files from `cards_by_category directory/`
2. Build list of available legal cards
3. Select cards ONLY from loaded database
4. Verify each card individually before adding to decklist
5. Document which CSV file each card was found in

---

## Card database lookup

| What you need | Where to look |
|---|---|
| Full file index | `cards_by_category directory/_INDEX.md` |
| A creature starting with H | `cards_by_category directory/creature/creature_h.csv` |
| An instant starting with C | `cards_by_category directory/instant/instant_c.csv` |
| A land starting with B | `cards_by_category directory/land/land_b.csv` |
| A planeswalker starting with T | `cards_by_category directory/planeswalker/planeswalker_t.csv` |

**Pattern**: `cards_by_category directory/{type}/{type}_{first_letter}.csv`

Files are ≤80KB. Open the specific file you need — do not scan all files.

---

## Deck construction checklist

- [ ] Card database loaded for relevant types BEFORE card selection
- [ ] Working list of legal cards created from loaded CSVs
- [ ] Format legality verified for every card (individually)
- [ ] 60 mainboard cards confirmed present in database
- [ ] 15 sideboard cards confirmed present in database
- [ ] Card names match database spelling exactly
- [ ] NO cards sourced from web searches or external decklists
- [ ] Mana base math validated
- [ ] Curve distribution checked
- [ ] Minimum 3 weaknesses identified
- [ ] Database verification section added to analysis.md
- [ ] Deck saved to `Decks/YYYY-MM-DD_Archetype_Name/`

---

## Database verification template

Add this section to every `analysis.md`:

```markdown
## Database Verification

### Files Loaded
- `cards_by_category directory/creature/creature_l.csv`
- `cards_by_category directory/instant/instant_c.csv`
- `cards_by_category directory/land/land_f.csv`
[List all CSV files you loaded]

### Legality Confirmation
✓ All 60 mainboard cards verified present in database
✓ All 15 sideboard cards verified present in database

### Per-Card Verification
✓ Card Name 1 - cards_by_category directory/creature/creature_c.csv
✓ Card Name 2 - cards_by_category directory/instant/instant_l.csv
[List representative cards with their source files]

### Rejected Cards
[List any cards user requested that were not in database]
None - all suggested cards were Standard-legal.
```

---

## File naming conventions

| Folder / file | Purpose |
|---|---|
| `Decks/YYYY-MM-DD_Archetype/` | Generated deck output |
| `cards_by_category directory/` | Card database root |
| `cards_by_category directory/_INDEX.md` | Master index of all card files |
| `Deck_builder_instructions.md` | Full AI methodology |
| `Deck_building_guidelines.md` | This file |
| `Rules_reference.md` | MTG rules reference |
| `Changelog.md` | Project change history |

---

## Output file structure

```
Decks/
└── 2026-03-09_Orzhov_Lifegain/
    ├── decklist.txt        ← MTGA importable
    ├── analysis.md         ← full reasoning + database verification
    └── sideboard_guide.md  ← matchup plans
```

---

## When database is not accessible

1. **STOP IMMEDIATELY** - do not proceed with deck building
2. Inform the user the database is unavailable
3. Request direct confirmation:
   - Card name, mana cost, type line, oracle text, power/toughness
   - Explicit confirmation that card is Standard-legal
4. Note in `analysis.md`: "Card legality user-confirmed due to database access issue"
5. Still verify as many cards as possible once database is accessible

**Do not build decks without database access unless user explicitly provides legality confirmation.**

---

## If user requests illegal cards

**Response template**:

> "I checked the database and [Card Name] is not present in `cards_by_category directory/`. This means it's not currently Standard-legal (likely rotated). 
>
> Legal alternatives from the database:
> - [Alternative 1] (similar effect)
> - [Alternative 2] (similar role)
> - [Alternative 3] (synergy match)
>
> Would you like me to use one of these instead?"

**Never include illegal cards even if user insists** - explain database is authoritative.

---

## Common mistakes and corrections

| ❌ Wrong | ✓ Correct |
|---|---|
| "I'll search for cards online" | "I'll load the database first" |
| "This card is probably legal" | "Let me verify in the CSV" |
| "I'll build then validate" | "I'll validate as I build" |
| "Web sources say it's good" | "Does it exist in database?" |
| "I'm 99% sure it's legal" | "I must verify in database" |

---

## Workflow summary

### Phase 0: Database Loading (NEW - MANDATORY)
1. Open `cards_by_category directory/_INDEX.md`
2. Identify needed card types
3. Load specific letter files
4. Create working list of legal cards
5. Document loaded files

### Phase 1-8: Deck Building
Follow standard 9-phase analysis from `Deck_builder_instructions.md`

**CRITICAL**: Only use cards from Phase 0 loaded database

### Phase 9: Final Validation
1. Verify each mainboard card against database (individually)
2. Verify each sideboard card against database (individually)
3. Create database verification section in analysis.md
4. Confirm NO cards came from web searches
5. Save to Decks/ folder

---

## Red flags (stop immediately if you catch yourself doing these)

1. 🚩 Adding cards without checking database first
2. 🚩 Searching "best Standard cards" online
3. 🚩 Copying deck lists from websites
4. 🚩 Assuming cards are legal because "they should be"
5. 🚩 Planning to validate after deck is complete
6. 🚩 Using memory/knowledge instead of database

**If you catch any of these: STOP, load database, start over with database-first approach.**

---

**Last updated**: March 9, 2026 | **Version**: 4.0 (Database-first enforcement)
