# AI Magic: The Gathering Deck Building Guidelines

## Output Format Requirements

**CRITICAL**: All MTG deck outputs MUST use MTGA import format.

### Standard Format

```
Deck
4 Card Name (SET) CollectorNumber
3 Another Card (SET) CollectorNumber
...

Sideboard
3 Sideboard Card (SET) CollectorNumber
...
```

### Key Rules
1. **Always start with "Deck" header** followed by mainboard cards
2. **Include set codes in parentheses** (e.g., FDN, DSK, LCI, MKM, WOE, BLB, OTJ)
3. **Include collector numbers** after set codes
4. **Use "Sideboard" header** for sideboard cards (if applicable)
5. **Format: Quantity CardName (SETCODE) Number**
6. **No bullet points, no markdown formatting, no explanations inline**
7. **Must be copy-pasteable directly into MTGA**

### Example

```
Deck
4 Extravagant Replication (FDN) 154
4 Confiscate (FDN) 709
3 Aetherize (FDN) 580
2 Terror Tide (LCI) 122
9 Island (ANB) 113
7 Swamp (ANB) 116

Sideboard
3 Negate (RIX) 44
3 Duress (STA) 29
```

---

## Deck Optimization Workflow

When user provides an existing deck:

1. **Preserve their format** - If they give MTGA format, respond in MTGA format
2. **Search card database FIRST** - Always verify cards exist in Standard card list before suggesting
3. **Use exact card names** - When user mentions specific cards, search for those EXACT names in the card list
4. **Minimal explanations** - Provide importable deck first, brief strategy notes after (optional, 2-3 sentences max)
5. **Never assume** - Don't suggest alternatives before confirming requested cards don't exist

---

## Card Search Protocol

When user requests specific cards (e.g., "add Aetherize", "use Day of Black Sun"):

1. **Search for EXACT card name** in `standard-cards-for-ai.txt` file
2. **If found**: Use it in the deck with correct set code and collector number
3. **If not found**: Clearly state "X is not in Standard" then suggest closest alternatives
4. **Never skip the search** - Always verify existence before making claims

---

## Response Structure

### Preferred Response Format

```
Deck
[full MTGA importable decklist]

Sideboard
[sideboard if applicable]
```

Optional brief note: 1-2 sentences explaining major changes.

### What NOT to do

❌ Don't use markdown lists or bullet points for cards  
❌ Don't add section headers like "Win Conditions (8)" inline  
❌ Don't explain every card choice  
❌ Don't suggest cards without verifying they exist in Standard  
❌ Don't change the user's requested format  

---

## Common Set Codes Reference

- **FDN** - Foundations
- **DSK** - Duskmourn: House of Horror
- **BLB** - Bloomburrow
- **OTJ** - Outlaws of Thunder Junction
- **MKM** - Murders at Karlov Manor
- **LCI** - The Lost Caverns of Ixalan
- **WOE** - Wilds of Eldraine
- **M20/M21** - Core Sets
- **ANB** - Arena Beginner

---

## Summary

**Golden Rule**: When the user shows you a deck in MTGA format, your output must be copy-pasteable MTGA format. No exceptions.
