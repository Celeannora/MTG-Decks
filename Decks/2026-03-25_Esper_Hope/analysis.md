# Esper Hope — WUB Lifegain/Mill/Angel Control

> *"Where there is life, there is hope — and where there is hope, memories fade."*

---

## Database Query Report

### Queries Run

| Query | Results |
|-------|---------|
| `search_cards.py --name "Hope Estheim"` | 1 candidate |
| `search_cards.py --type creature --colors WUB --tags lifegain` | 94 candidates |
| `search_cards.py --type creature --colors WUB --keywords Flying --tags lifegain` | 18 candidates |
| `search_cards.py --type creature --colors WUB --oracle "angel"` | 14 candidates |
| `search_cards.py --type creature --colors WUB --tags mill` | 12 candidates |
| `search_cards.py --type instant --colors WUB --tags removal` | 42 candidates |
| `search_cards.py --type instant --colors WUB --tags counter` | 31 candidates |
| `search_cards.py --type instant --colors WUB --tags draw` | 28 candidates |
| `search_cards.py --type enchantment --colors WUB --tags lifegain` | 15 candidates |
| `search_cards.py --type enchantment --colors WUB --tags mill` | 8 candidates |
| `search_cards.py --type sorcery --colors WUB --tags removal` | 19 candidates |
| `search_cards.py --type land --colors WUB` | 89 candidates |
| Individual detail lookups (Exemplar of Light, Overlord of the Balemurk, etc.) | 30+ detail reads |

### Per-Card Verification (60 mainboard + 15 sideboard)

**Mainboard:**
✓ Hope Estheim (x4) — creature/creature_h2.csv — (FIN) 541
✓ Deep-Cavern Bat (x3) — creature/creature_d1.csv — (SCH) 33
✓ Ajani's Pridemate (x2) — creature/creature_a1.csv — (CLU) 52
✓ Overlord of the Balemurk (x2) — creature/creature_o.csv — (DSK) 391
✓ The Mindskinner (x2) — creature/creature_t1.csv — (DSK) 357
✓ Resplendent Angel (x2) — creature/creature_r2.csv — (PLCI) 32p
✓ Exemplar of Light (x2) — creature/creature_e.csv — (FDN) 297
✓ Lyra Dawnbringer (x2) — creature/creature_l2.csv — (DMR) 413
✓ Heartless Act (x2) — instant/instant_h.csv — (IKO) 366
✓ Get Lost (x2) — instant/instant_g.csv — (PLCI) 14p
✓ No More Lies (x2) — instant/instant_n.csv — (MKM) 221
✓ Three Steps Ahead (x2) — instant/instant_t.csv — (POTJ) 75s
✓ Spell Pierce (x1) — instant/instant_s.csv — (2X2) 63
✓ Opt (x2) — instant/instant_o.csv — (WOC) 101
✓ Think Twice (x2) — instant/instant_t.csv — (TSP) 86
✓ Deduce (x2) — instant/instant_d.csv — (MKM) 293
✓ Authority of the Consuls (x1) — enchantment/enchantment_a.csv — (PKLD) 5s
✓ Sheltered by Ghosts (x2) — enchantment/enchantment_s.csv — (PJSC) 2026-1
✓ Stillness in Motion (x1) — enchantment/enchantment_s.csv — (PTDM) 59p
✓ Hallowed Fountain (x2) — land/land_h.csv — (UNF) 277
✓ Watery Grave (x2) — land/land_w.csv — (CLU) 283
✓ Godless Shrine (x2) — land/land_g.csv — (UNF) 533
✓ Meticulous Archive (x1) — land/land_m1.csv — (PMKM) 264p
✓ Undercity Sewers (x1) — land/land_u.csv — (PZA) 20
✓ Shadowy Backstreet (x1) — land/land_s1.csv — (MKM) 330
✓ Restless Fortress (x1) — land/land_r.csv — (PWOE) 259s
✓ Restless Anchorage (x1) — land/land_r.csv — (LCI) 347
✓ Concealed Courtyard (x2) — land/land_c.csv — (POTJ) 268p
✓ Floodfarm Verge (x1) — land/land_f1.csv — (DSK) 330
✓ Gloomlake Verge (x1) — land/land_g.csv — (PDSK) 260s
✓ Plains (x3) — land/land_p1.csv — (CMA) 292
✓ Island (x2) — land/land_i1.csv — (ELD) 255
✓ Swamp (x2) — land/land_s1.csv — (JMP) 59

**Sideboard:**
✓ Moment of Craving (x2) — instant/instant_m.csv — (PLST) RIX-79
✓ Enduring Innocence (x2) — creature/creature_e.csv — (DSK) 6
✓ Bitter Triumph (x1) — instant/instant_b.csv — (LCI) 91
✓ Negate (x2) — instant/instant_n.csv — (OGW) 59
✓ Enduring Curiosity (x2) — creature/creature_e.csv — (PDSK) 51s
✓ Spellgyre (x1) — instant/instant_s.csv — (BLB) 72
✓ Angel of Finality (x2) — creature/creature_a1.csv — (C20) 75
✓ Malicious Eclipse (x2) — sorcery/sorcery_m.csv — (LCI) 111
✓ Consuming Ashes (x1) — instant/instant_c.csv — (OTJ) 83

### Rejected Cards

- **Marauding Blight-Priest** — {2}{B} drains 1 per lifegain, but 3 CMC without evasion competes with better 3-drops. Cut.
- **Angel of Vitality** — Lifegain amplifier, but with only 2 colors of the Azorius version's WU engine, less impactful in 3-color. Replaced by Exemplar of Light which offers removal.
- **Giada, Font of Hope** — Angel tribal lord, but Esper Hope is not pure Angel tribal. Only 8 Angels in the 60; counters too inconsistent. Cut.
- **Inspiring Overseer** — ETB draw + life, but {2}{W} for a 2/1 is too fragile; Deduce/Opt do the draw job better.
- **Vampire Nighthawk** — {1}{B}{B} is color-intensive; excellent keywords but doesn't synergize with mill axis. Cut.
- **Day of Judgment** — 4-mana wipe, but Malicious Eclipse in sideboard is better since it exiles and costs 3. Cut from main.
- **Linden, the Steadfast Queen** — {W}{W}{W} impossible in 3-color mana base.
- **Space-Time Anomaly** — From previous Azorius version; not found in database under Esper-legal cards. Replaced by dedicated mill creatures.

### Validation Script Result

```
$ python scripts/validate_decklist.py Decks/2026-03-25_Esper_Hope/decklist.txt
✅ VALIDATION PASSED
All cards are legal and present in the database.
Mainboard: 60 cards | Sideboard: 15 cards
```

---

## Executive Summary

**Deck name:** Esper Hope
**Colors:** Esper (White/Blue/Black)
**Format:** Standard
**Archetype:** Lifegain/Mill/Angel Control

**The Core Loop:**
1. Deploy Hope Estheim and lifegain enablers (Deep-Cavern Bat, Authority of the Consuls, Sheltered by Ghosts)
2. Every point of life gained triggers Hope Estheim's end-step mill on the opponent
3. Dedicated mill engines (The Mindskinner, Overlord of the Balemurk, Stillness in Motion) attack the library directly
4. Angel finishers (Resplendent Angel, Exemplar of Light, Lyra Dawnbringer) provide an aerial beatdown backup

**Why Esper over Azorius?** Adding black gives access to premium removal (Heartless Act, Get Lost), hand disruption (Deep-Cavern Bat), dedicated mill creatures (Overlord of the Balemurk, The Mindskinner), and powerful sideboard tools (Malicious Eclipse, Consuming Ashes). The three-color mana base is supported by 6 shocklands, 3 surveil duals, 2 fast lands, and 2 verge lands.

**Target win condition:** Mill-out by turn 8-10 via Hope Estheim accumulation plus dedicated mill engines, or aerial beatdown via Resplendent Angel tokens and Lyra-buffed Angels.

---

## Card-by-Card Breakdown

### The Engine Core

**Hope Estheim** (4x) — {W}{U} | Legendary Creature — Human Wizard | Lifelink
*Source: `cards_by_category/creature/creature_h2.csv`*
The deck's namesake and central synergy piece. Lifelink means he contributes to his own trigger. Every end step, opponents mill X where X = life gained that turn. Four copies ensures a consistent turn-2 play. Multiple copies stack their triggers independently, creating exponential mill pressure.

**Deep-Cavern Bat** (3x) — {1}{B} | Creature — Bat | Flying, Lifelink
*Source: `cards_by_category/creature/creature_d1.csv`*
Flying lifelink body that disrupts the opponent's hand on ETB. Every point of combat damage gains life for Hope Estheim's mill trigger. The hand disruption protects your engine from removal. Three copies — the deck's best black 2-drop and critical for tempo.

**Ajani's Pridemate** (2x) — {1}{W} | Creature — Cat Soldier
*Source: `cards_by_category/creature/creature_a1.csv`*
Grows by +1/+1 every time you gain life. In this deck, Pridemate becomes a 6/6+ by turn 5 regularly. Demands an immediate answer or wins by combat alone. Two copies — powerful but not part of the mill or Angel synergy; a supplemental threat.

**Authority of the Consuls** (1x) — {W} | Enchantment
*Source: `cards_by_category/enchantment/enchantment_a.csv`*
Opponents' creatures enter tapped AND you gain 1 life per creature they play. Both effects feed the deck: lifegain triggers Hope Estheim and grows Ajani's Pridemate; entering tapped stops aggressive starts. One copy — powerful but legendary-adjacent; drawing multiples is poor.

### Mill Package

**Overlord of the Balemurk** (2x) — {3}{B}{B} | Enchantment Creature — Avatar Horror
*Source: `cards_by_category/creature/creature_o.csv`*
Impending for {1}{B} as a 2-mana enchantment that mills 4 on entry and recurs a creature card from the graveyard. The impending mode dodges creature removal while milling aggressively. When it becomes a creature, it's a 6/5 that continues the mill pressure. Two copies — the deck's primary black-aligned mill threat.

**The Mindskinner** (2x) — {U}{U}{U} | Legendary Enchantment Creature — Nightmare
*Source: `cards_by_category/creature/creature_t1.csv`*
Unblockable creature that converts all combat damage dealt to opponents into mill. A 2/2 unblockable that mills 2 per turn is already strong; with any pump or Lyra's +1/+1 buff, the mill rate scales. Two copies — triple-blue is demanding but achievable by turn 4-5 in this mana base.

**Stillness in Motion** (1x) — {1}{U} | Enchantment
*Source: `cards_by_category/enchantment/enchantment_s.csv`*
Two-mana enchantment that mills 3 per upkeep passively. Reliable, hard to remove, and compounds with Hope Estheim's end-step trigger. One copy — low-impact individually but provides consistent background mill pressure.

### Angel Finishers

**Resplendent Angel** (2x) — {1}{W}{W} | Creature — Angel | Flying
*Source: `cards_by_category/creature/creature_r2.csv`*
Creates a 4/4 flying vigilance Angel token at end step if you gained 5+ life that turn. With Hope Estheim's lifelink, Deep-Cavern Bat, and Sheltered by Ghosts, reaching 5 life in a turn is trivial by turn 4. Each token provides additional aerial pressure. Two copies — strong but {W}{W} can be demanding.

**Exemplar of Light** (2x) — {2}{W}{W} | Creature — Angel
*Source: `cards_by_category/creature/creature_e.csv`*
Grows from lifegain triggers with +1/+1 counters, then removes counters to exile target permanents. Bridges the lifegain engine directly into removal. Two copies — the most synergistic Angel in the deck, converting life gain into board control.

**Lyra Dawnbringer** (2x) — {3}{W}{W} | Legendary Creature — Angel | Flying, First Strike, Lifelink
*Source: `cards_by_category/creature/creature_l2.csv`*
The general. 5/5 flying first strike lifelink that gives all other Angels +1/+1 and lifelink. With Lyra in play, every Angel attacking gains life, every life gained triggers Hope Estheim's mill. Two copies due to legendary status.

### Interaction Suite

**Heartless Act** (2x) — {1}{B} | Instant
*Source: `cards_by_category/instant/instant_h.csv`*
Two-mana instant-speed destroy creature (with no counters) or remove 3 counters. Efficient, flexible, on-curve. Black's premium removal spell in the format.

**Get Lost** (2x) — {1}{W} | Instant
*Source: `cards_by_category/instant/instant_g.csv`*
Two-mana instant that destroys a creature, enchantment, or planeswalker. The most versatile removal in the deck, handling any problematic permanent type. The Map tokens given to the opponent are negligible.

**Sheltered by Ghosts** (2x) — {1}{W} | Enchantment — Aura
*Source: `cards_by_category/enchantment/enchantment_s.csv`*
ETB exiles a target nonland permanent. Grants enchanted creature lifelink and ward {2}. Dual role: removal AND lifegain enabler. Attaching to Hope Estheim creates a protected lifelink mill engine.

**No More Lies** (2x) — {W}{U} | Instant
*Source: `cards_by_category/instant/instant_n.csv`*
Counter target spell unless opponent pays {3}; exiles on counter. Efficient Esper-colored counterspell that protects the engine and exiles combo pieces.

**Three Steps Ahead** (2x) — {U} (Spree) | Instant
*Source: `cards_by_category/instant/instant_t.csv`*
Flexible Spree spell: hard counter mode or copy mode. The modality makes it never dead in hand — counter when you need protection, copy when you want value.

**Spell Pierce** (1x) — {U} | Instant
*Source: `cards_by_category/instant/instant_s.csv`*
One-mana noncreature counter. Excellent early game protection for Hope Estheim against removal and board wipes.

### Card Draw

**Opt** (2x) — {U} | Instant
*Source: `cards_by_category/instant/instant_o.csv`*
One-mana instant cantrip with scry 1. Smooths early draws and finds key pieces at minimal cost.

**Think Twice** (2x) — {1}{U} | Instant
*Source: `cards_by_category/instant/instant_t.csv`*
Two-mana draw with flashback from the graveyard. Provides sustained card advantage in longer games, and the graveyard synergizes with Overlord of the Balemurk's creature recursion.

**Deduce** (2x) — {1}{U} | Instant
*Source: `cards_by_category/instant/instant_d.csv`*
Two-mana draw plus investigate (Clue token). The Clue provides additional draw later, making this effectively draw-two spread across turns.

### Mana Base

**Hallowed Fountain** (2x) — Land — Plains Island
*Source: `cards_by_category/land/land_h.csv`*
W/U shockland. Untapped for 2 life — a small cost in a lifegain deck.

**Watery Grave** (2x) — Land — Island Swamp
*Source: `cards_by_category/land/land_w.csv`*
U/B shockland. Critical for casting The Mindskinner and Overlord of the Balemurk.

**Godless Shrine** (2x) — Land — Plains Swamp
*Source: `cards_by_category/land/land_g.csv`*
W/B shockland. Enables turn-2 Deep-Cavern Bat off a Plains.

**Meticulous Archive** (1x) — Land — Plains Island
*Source: `cards_by_category/land/land_m1.csv`*
W/U surveil dual. Enters tapped but filters draws.

**Undercity Sewers** (1x) — Land — Island Swamp
*Source: `cards_by_category/land/land_u.csv`*
U/B surveil dual. Enters tapped with surveil 1.

**Shadowy Backstreet** (1x) — Land — Plains Swamp
*Source: `cards_by_category/land/land_s1.csv`*
W/B surveil dual. Enters tapped with surveil 1.

**Restless Fortress** (1x) — Land
*Source: `cards_by_category/land/land_r.csv`*
W/B creature land with lifelink on attack. Fits the lifegain theme as a land that also generates mill triggers.

**Restless Anchorage** (1x) — Land
*Source: `cards_by_category/land/land_r.csv`*
W/U creature land that creates 1/1 tokens on attack. Extra bodies for late-game pressure.

**Concealed Courtyard** (2x) — Land
*Source: `cards_by_category/land/land_c.csv`*
W/B fast land. Untapped turns 1-3 for early curve plays.

**Floodfarm Verge** (1x) — Land
*Source: `cards_by_category/land/land_f1.csv`*
W/U verge land. Conditional untapped dual.

**Gloomlake Verge** (1x) — Land
*Source: `cards_by_category/land/land_g.csv`*
U/B verge land. Conditional untapped dual.

**Plains** (3x) / **Island** (2x) / **Swamp** (2x) — Basics
Needed to activate verge lands, protect against nonbasic land punishment, and ensure early color access.

---

## Mana Base Analysis

**Total: 22 lands**

| Land | Count | Colors | Entry |
|------|-------|--------|-------|
| Hallowed Fountain | 2 | W/U | Untapped (2 life) |
| Watery Grave | 2 | U/B | Untapped (2 life) |
| Godless Shrine | 2 | W/B | Untapped (2 life) |
| Meticulous Archive | 1 | W/U | Tapped (surveil 1) |
| Undercity Sewers | 1 | U/B | Tapped (surveil 1) |
| Shadowy Backstreet | 1 | W/B | Tapped (surveil 1) |
| Restless Fortress | 1 | W/B | Tapped |
| Restless Anchorage | 1 | W/U | Tapped |
| Concealed Courtyard | 2 | W/B | Untapped (T1-3) |
| Floodfarm Verge | 1 | W/U | Conditional untapped |
| Gloomlake Verge | 1 | U/B | Conditional untapped |
| Plains | 3 | W | Untapped |
| Island | 2 | U | Untapped |
| Swamp | 2 | B | Untapped |
| **Total** | **22** | | |

**Color source count:**
- White sources: 16 (Hallowed Fountain, Godless Shrine, Meticulous Archive, Shadowy Backstreet, Restless Fortress, Restless Anchorage, Concealed Courtyard, Floodfarm Verge, Plains)
- Blue sources: 13 (Hallowed Fountain, Watery Grave, Meticulous Archive, Undercity Sewers, Restless Anchorage, Floodfarm Verge, Gloomlake Verge, Island)
- Black sources: 13 (Watery Grave, Godless Shrine, Undercity Sewers, Shadowy Backstreet, Restless Fortress, Concealed Courtyard, Gloomlake Verge, Swamp)

**Colored pip analysis (mainboard non-land):**
- {W}: 25 pips
- {U}: 22 pips
- {B}: 9 pips

**Ratio:** Heavily white with significant blue and splash black. The mana base supports this with white having the most sources, blue close behind (needed for The Mindskinner's {U}{U}{U}), and black at a comfortable 13 sources for a splash.

**Tapped land count:** 5 (3 surveil duals + 2 creature lands). Acceptable at 22.7% — most opening hands will have at most 1 tapped land.

---

## Curve Analysis

| CMC | Cards | Count |
|-----|-------|-------|
| 1 | Authority of the Consuls, Spell Pierce, Opt (×2) | 4 |
| 2 | Hope Estheim (×4), Deep-Cavern Bat (×3), Ajani's Pridemate (×2), Heartless Act (×2), Get Lost (×2), No More Lies (×2), Sheltered by Ghosts (×2), Stillness in Motion, Think Twice (×2), Deduce (×2) | 22 |
| 3 | The Mindskinner (×2), Resplendent Angel (×2), Three Steps Ahead (×2) | 6 |
| 4 | Exemplar of Light (×2) | 2 |
| 5 | Overlord of the Balemurk (×2), Lyra Dawnbringer (×2) | 4 |

**Average CMC (non-land):** 2.42

**Ideal turn sequence:**
- T1: Authority of the Consuls or Opt/Spell Pierce with mana up
- T2: Hope Estheim or Deep-Cavern Bat (lifegain + disruption begins)
- T3: The Mindskinner or Resplendent Angel (mill engine or token generator)
- T4: Exemplar of Light (lifegain → counters → exile removal)
- T5: Lyra Dawnbringer (all Angels gain lifelink, massive mill spike) or Overlord of the Balemurk (impending for {1}{B} on T2, becoming creature on T7)

**Life total projection at T5:** 24-32 life (Hope lifelink + Deep-Cavern Bat + Authority triggers)
**Mill projection at T5:** 12-20 cards milled cumulatively (Estheim triggers + Mindskinner + Stillness in Motion)

---

## Interaction Map: Why Every Card Is Here

```
Hope Estheim (engine)
  → lifelink: contributes to own mill trigger
  → end step mill = total life gained this turn
  → Sheltered by Ghosts on Estheim = lifelink + ward + exile removal

Deep-Cavern Bat (tempo + lifegain)
  → flying lifelink: mills via Hope Estheim trigger
  → ETB hand disruption: removes opponent's answer to Hope
  → pairs with Lyra (+1/+1 and lifelink redundancy)

Overlord of the Balemurk (mill + recursion)
  → impending for 1B: dodges creature removal as enchantment
  → ETB mills 4 cards
  → recurs Hope Estheim or Deep-Cavern Bat from graveyard

The Mindskinner (dedicated mill)
  → unblockable: guaranteed combat damage → mill
  → Lyra gives +1/+1: 3 damage = 3 cards milled per turn
  → stacks with Hope Estheim's end-step mill

Resplendent Angel (token factory)
  → 5+ life gained in a turn → 4/4 Angel token
  → Lyra gives all Angels lifelink → more life → more mill
  → tokens fuel Exemplar of Light's counter growth

Exemplar of Light (lifegain → removal)
  → grows from lifegain triggers
  → removes counters to exile permanents
  → bridges lifegain engine directly into board control

Lyra Dawnbringer (force multiplier)
  → all Angels gain lifelink: Resplendent Angel, Exemplar
  → massive life spike → massive Hope Estheim mill trigger
  → first strike means she survives most combat
```

---

## Matchup Table

| Matchup | Game Plan | Key Cards | Board-In / Board-Out |
|---------|-----------|-----------|----------------------|
| Aggro (Red/Gruul) | Gain life to stabilize, removal slows them, Resplendent Angel tokens wall them | Authority of the Consuls, Heartless Act, Moment of Craving | +2 Moment of Craving, +2 Enduring Innocence, +1 Bitter Triumph / −2 The Mindskinner, −1 Stillness in Motion, −2 Think Twice |
| Control (Azorius/Dimir) | Protect threats with counters, mill as primary win con, grind with card draw | No More Lies, Three Steps Ahead, The Mindskinner | +2 Negate, +2 Enduring Curiosity, +1 Spellgyre / −2 Heartless Act, −2 Get Lost, −1 Authority of the Consuls |
| Midrange (Golgari/Rakdos) | Out-value on life gain, aerial pressure, Exemplar exiles threats | Hope Estheim, Exemplar of Light, Lyra Dawnbringer | +2 Enduring Innocence, +1 Bitter Triumph / −1 Stillness in Motion, −1 Spell Pierce, −1 Think Twice |
| Graveyard/Reanimator | Counter key spells (exile clause), Angel of Finality exiles graveyard | No More Lies, Angel of Finality, Consuming Ashes | +2 Angel of Finality, +1 Consuming Ashes, +2 Malicious Eclipse / −2 Ajani's Pridemate, −1 Authority of the Consuls, −2 Think Twice |
| Tokens/Go-Wide | Malicious Eclipse sweeps and exiles, Lyra's lifelink overwhelms | Malicious Eclipse, Lyra Dawnbringer, Heartless Act | +2 Malicious Eclipse, +2 Moment of Craving / −2 The Mindskinner, −1 Stillness in Motion, −1 Spell Pierce |

---

## Structural Weaknesses

1. **Three-color mana base inconsistency** — Mitigation: 6 shocklands provide reliable fixing; 22 lands with low average CMC (2.42) reduce mana screw. The Mindskinner's {U}{U}{U} is the hardest cast, achievable turn 4+ with 13 blue sources.

2. **No mainboard board wipe** — Mitigation: The deck wins through targeted removal and evasion. Malicious Eclipse in the sideboard provides a -2/-2 sweep with exile for creature-heavy matchups.

3. **Vulnerable to enchantment removal targeting Sheltered by Ghosts / Stillness in Motion** — Mitigation: Counterspell suite (5 counters mainboard) protects key enchantments. Authority of the Consuls and Stillness in Motion are low-cost enough to re-deploy.

4. **The Mindskinner requires {U}{U}{U}** — Mitigation: 13 blue sources in the mana base. Can be sided out when the mana demands don't align. Hope Estheim + Overlord provide mill backup.

5. **Legendary creature density** — Hope Estheim (4x), The Mindskinner (2x), Lyra Dawnbringer (2x) are all legendary. Mitigation: Varied copies (4-2-2) reduce redundancy. Extra Hope Estheim copies still trigger individually.

---

## Playtesting Notes

*Theoretical analysis. Record actual results here.*

**Key decision points:**
- **Keep or mulligan a no-Hope hand?** Generally keep if you have Deep-Cavern Bat + removal + card draw. The mill plan has backup engines (Mindskinner, Overlord, Stillness in Motion). A hand with just Angels and no engine is a keep only with Resplendent Angel + lifegain.
- **When to deploy Overlord of the Balemurk:** Impending for {1}{B} on turn 2 is excellent — mills 4, recurs a creature, and dodges creature removal for 5 turns. Play it early as an enchantment, not late as a 5-mana creature.
- **Sheltered by Ghosts targeting:** Always prioritize putting it on Hope Estheim if no other copy is on board. The exile effect removes their best threat AND ward {2} + lifelink makes him extremely hard to answer.
- **Three Steps Ahead mode selection:** Default to counter mode when protecting Hope Estheim or The Mindskinner. Use copy mode only when you have the engine established and want to duplicate an ETB creature.
- **Sideboarding The Mindskinner:** Board out against aggressive decks where {U}{U}{U} on turn 3 is too slow. Keep in against control where the unblockable mill is the primary win condition.
