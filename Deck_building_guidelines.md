# Deck building guidelines

Quick reference for AI assistants. For the full methodology see `Deck_builder_instructions.md`.

---

## Card database lookup

| What you need | Where to look |
|---|---|
| Full file index | `card_data/_INDEX.md` |
| A creature starting with H | `card_data/creature/creature_h.csv` |
| An instant starting with C | `card_data/instant/instant_c.csv` |
| A land starting with B | `card_data/land/land_b.csv` |
| A planeswalker starting with T | `card_data/planeswalker/planeswalker_t.csv` |

**Pattern**: `card_data/{type}/{type}_{first_letter}.csv`

Files are ≤80KB. Open the specific file you need — do not scan all files.

---

## Deck construction checklist

- [ ] Card database loaded for relevant types
- [ ] Format legality verified for every card
- [ ] 60 mainboard cards confirmed
- [ ] 15 sideboard cards confirmed
- [ ] Mana base math validated
- [ ] Curve distribution checked
- [ ] Minimum 3 weaknesses identified
- [ ] Deck saved to `Decks/YYYY-MM-DD_Archetype_Name/`

---

## File naming conventions

| Folder / file | Purpose |
|---|---|
| `Decks/YYYY-MM-DD_Archetype/` | Generated deck output |
| `card_data/` | Card database root |
| `card_data/_INDEX.md` | Master index of all card files |
| `Deck_builder_instructions.md` | Full AI methodology |
| `Deck_building_guidelines.md` | This file |
| `Rules_reference.md` | MTG rules reference |
| `Changelog.md` | Project change history |

---

## Output file structure

```
Decks/
└── 2026-03-08_Orzhov_Lifegain/
    ├── decklist.txt        ← MTGA importable
    ├── analysis.md         ← full reasoning
    └── sideboard_guide.md  ← matchup plans
```

---

## When database is not accessible

1. Tell the user the database is unavailable
2. Ask for: card name, mana cost, type line, oracle text, power/toughness
3. Proceed using user-provided details
4. Note in `analysis.md`: "Card legality user-confirmed"

---

**Last updated**: March 8, 2026 | **Version**: 3.0
