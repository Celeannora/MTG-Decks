# MANDATORY DECK BUILDING PROTOCOL

## CRITICAL REQUIREMENT
This repository contains the ONLY valid card pool. All deck building and card recommendations MUST be validated against this database.

## PROTOCOL FOR ALL AI SESSIONS

### BEFORE SUGGESTING ANY CARDS:

1. **SEARCH THE DATABASE FIRST**
   - Never suggest cards from general knowledge
   - Every card MUST be verified to exist in this repository
   - If a card is not in the database, it is ILLEGAL

2. **REQUIRED WORKFLOW**
   ```
   Step 1: User requests deck building
   Step 2: Search cards_by_category directory for relevant cards
   Step 3: Verify each suggested card exists in database
   Step 4: Only present verified cards
   ```

3. **FORBIDDEN ACTIONS**
   - ❌ Suggesting cards without database verification
   - ❌ Using internal MTG knowledge as primary source
   - ❌ Assuming cards exist in the collection
   - ❌ Mixing verified and unverified cards
   - ❌ Skipping database searches for "efficiency"

## DATABASE STRUCTURE

```
cards_by_category directory/
├── creature/
├── instant/
├── sorcery/
├── enchantment/
├── artifact/
├── land/
└── planeswalker/
```

Each directory contains CSV files organized alphabetically (e.g., `creature_a1.csv`, `creature_h2.csv`)

## SEARCH METHODOLOGY

### For Deck Building Requests:

1. **Identify card requirements** (colors, keywords, effects)
2. **Search by category**:
   - Creatures with lifelink: Search `creature/` directory, filter by keywords
   - Mill effects: Search for "mill" in oracle_text/keywords
   - Removal spells: Search `instant/` and `sorcery/` directories
   - Lands: Search `land/` directory for color requirements

3. **Verify each card** in CSV files before suggesting
4. **Compile only verified cards** into deck list

### CSV File Fields:
- `name`: Card name
- `mana_cost`: Mana cost (e.g., {2}{W}{U})
- `type_line`: Card type
- `oracle_text`: Card abilities and text
- `colors`: Card colors
- `keywords`: Keywords (lifelink, mill, etc.)
- `power`/`toughness`: Creature stats
- `rarity`: Rarity level
- `set`: Set code

## VALIDATION CHECKLIST

Before presenting ANY deck list or card recommendations:

- [ ] Did I search the database for each suggested card?
- [ ] Can I cite the specific CSV file and line for each card?
- [ ] Are all cards confirmed to exist in this repository?
- [ ] Did I avoid using general MTG knowledge without verification?

**IF ANY ANSWER IS "NO" → DO NOT PROCEED. SEARCH DATABASE FIRST.**

## FAILURE CONSEQUENCES

Suggesting cards not in this database:
- Wastes user time
- Wastes computational resources
- Violates mandatory instructions
- Is completely unacceptable

## EXAMPLE CORRECT WORKFLOW

User: "Build a lifegain mill deck with Hope Estheim"

AI MUST:
1. ✅ Search `creature/creature_h2.csv` for Hope Estheim
2. ✅ Search creature files for cards with "lifelink" keyword
3. ✅ Search for cards with "mill" in oracle_text
4. ✅ Search `land/` directory for appropriate mana base
5. ✅ Compile list ONLY from verified cards
6. ✅ Present deck with citations to database files

AI MUST NOT:
1. ❌ Suggest "Hedron Crab" without verifying it exists
2. ❌ Suggest "Path to Exile" from general knowledge
3. ❌ Assume any card exists without database confirmation

## SESSION START INSTRUCTION

**ALL AI sessions helping with deck building MUST acknowledge this protocol:**

"I acknowledge that I will ONLY suggest cards verified to exist in the Celeannora/MTG-Decks repository. I will search the database BEFORE making ANY card suggestions. I will NOT use general MTG knowledge without database verification."

---

**This protocol is mandatory and non-negotiable for all deck building assistance.**
