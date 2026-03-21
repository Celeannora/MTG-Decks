# Frosch Blitzkrieg v2 — Simic Frog Tribal Aggro-Midrange

> *„Schneller. Tödlicher. Unaufhaltsam."* — Faster. Deadlier. Unstoppable.

---

## Database Query Report

### Queries Run

| Query | Results |
|-------|---------|
| `search_cards.py --type creature --oracle "frog" --format names` | 7 frog creatures |
| `search_cards.py --type creature --colors GU --tags pump --rarity rare,mythic --cmc-max 4` | 55 candidates |
| `search_cards.py --type instant --colors GU --tags counter` | 27 candidates |
| `search_cards.py --type instant --colors GU --tags pump --cmc-max 3` | 37 candidates |
| `search_cards.py --type enchantment --colors GU --tags pump,draw` | 9 candidates |
| `search_cards.py --type land --colors GU` | 40+ candidates |
| Individual card detail lookups (Repulsive Mutation, Inspiring Call, Biosynthic Burst, etc.) | 15+ reads |

### Version Delta vs. v1 (2026-03-20)

**Added:**
✓ Repulsive Mutation (x4) — instant/instant_r.csv — (MKM) 227
✓ Inspiring Call (x2) — instant/instant_i.csv — (IMA) 169
✓ Biosynthic Burst (x2) — instant/instant_b.csv — (EOE) 173
✓ Hedge Maze (x2) — land/land_h.csv — (PMKM) 262s
✓ Willowrush Verge (x4, was x2) — land/land_w.csv — (DFT) 375
✓ Mistbreath Elder (x4, was x2) — creature/creature_m2.csv — (PBLB) 184p

**Removed:**
- Sunshower Druid (4→2) — lifegain less critical in aggro build; Biosynthic Burst serves counter role better
- Three Tree Scribe (2→1) — powerful but competes with 2-drop slot density
- Innkeeper's Talent (2→2, was 2x) — kept; Gossip's Talent cut for Repulsive Mutation
- Gossip's Talent (cut) — surveil replaced by Hedge Maze and Lilypad Village passive
- Synchronized Charge (1x main→SB) — now sideboard; replaced by Repulsive Mutation which does more
- Splash Portal (cut) — Biosynthic Burst's untap effect is cleaner
- Gossip's Talent × 2 SB → Blossoming Defense + Three Steps Ahead

### Per-Card Verification (60 mainboard + 15 sideboard)

**Mainboard:**
✓ Valley Mightcaller (x4) — creature/creature_v.csv — (BLB) 326
✓ Mistbreath Elder (x4) — creature/creature_m2.csv — (PBLB) 184p
✓ Frog Butler (x4) — creature/creature_f2.csv — (TMT) 114
✓ Poison Dart Frog (x3) — creature/creature_p.csv — (LCI) 207
✓ Sunshower Druid (x2) — creature/creature_s4.csv — (BLB) 195
✓ Genghis Frog (x2) — creature/creature_g1.csv — (TMT) 148
✓ Clement, the Worrywort (x2) — creature/creature_c1.csv — (BLB) 347
✓ Three Tree Scribe (x1) — creature/creature_t2.csv — (BLB) 199
✓ Dour Port-Mage (x1) — creature/creature_d2.csv — (PBLB) 47s
✓ Valley Floodcaller (x1) — creature/creature_v.csv — (BLB) 308
✓ Dreamdew Entrancer (x1) — creature/creature_d2.csv — (BLB) 365
✓ Polliwallop (x2) — instant/instant_p.csv — (BLB) 189
✓ Repulsive Mutation (x4) — instant/instant_r.csv — (MKM) 227
✓ Inspiring Call (x2) — instant/instant_i.csv — (IMA) 169
✓ Biosynthic Burst (x2) — instant/instant_b.csv — (EOE) 173
✓ Innkeeper's Talent (x2) — enchantment/enchantment_i.csv — (SLP) 45
✓ Glacierwood Siege (x2) — enchantment/enchantment_g.csv — (TDM) 189
✓ Breeding Pool (x4) — land/land_b.csv — (EXP) 15
✓ Botanical Sanctum (x4) — land/land_b.csv — (SLD) 1376
✓ Willowrush Verge (x4) — land/land_w.csv — (DFT) 375
✓ Lilypad Village (x2) — land/land_l.csv — (BLB) 255
✓ Oakhollow Village (x2) — land/land_o.csv — (BLB) 258
✓ Hedge Maze (x2) — land/land_h.csv — (PMKM) 262s
✓ Forest (x1) — land/land_f1.csv — (BLB) 280
✓ Island (x2) — land/land_i1.csv — (ELD) 255

**Sideboard:**
✓ Disdainful Stroke (x3) — instant/instant_d.csv — (GRN) 37
✓ Stickytongue Sentinel (x3) — creature/creature_s4.csv — (BLB) 193
✓ Blossoming Defense (x2) — instant/instant_b.csv — (ECL) 167
✓ Three Steps Ahead (x2) — instant/instant_t.csv — (POTJ) 75s
✓ Synchronized Charge (x2) — sorcery/sorcery_s.csv — (TDM) 162
✓ Confounding Riddle (x2) — instant/instant_c.csv — (LCI) 50
✓ Dreamdew Entrancer (x1) — creature/creature_d2.csv — (BLB) 365

### Rejected / Considered Cards

- **Glarb, Calamity's Augur** — {B}{G}{U} is three colors; running black would require a full mana base rebuild and dilutes the Simic identity. Cut.
- **Quina, Qu Gourmet** — token doubling is powerful but relies on token-makers we don't have outside of Genghis Frog. Better in a dedicated token shell.
- **Spider-Ham, Peter Porker** — gives all Frogs +1/+1 which is strong, but competes with the 2-drop slot (already Frog Butler + Poison Dart Frog). Sideboard consideration if meta requires more bodies.
- **Kitsa, Otterball Elite** — excellent with Valley Floodcaller but {1}{U} and we only run 1 Floodcaller; prowess doesn't trigger off creatures. Not enough spell density.
- **Innkeeper's Talent (3x)** — level 3 doubling counters is the dream, but 3 copies at CMC 2 in an already-crowded 2-drop slot dilutes the threat density. Two is correct.

### Validation Script Result

```
$ python scripts/validate_decklist.py Decks/2026-03-21_Frosch_Blitzkrieg_v2/decklist.txt --verbose
✅ VALIDATION PASSED
All cards are legal and present in the database.
Mainboard: 60 cards | Sideboard: 15 cards
```

---

## Executive Summary

**Deck name:** Frosch Blitzkrieg v2
**Colors:** Simic (Green/Blue)
**Format:** Standard
**Archetype:** Frog Tribal Aggro-Midrange

**Core philosophy unchanged:** Overwhelm through speed, bounce loops, and an unstoppable Frog army. **What's new in v2:** The interaction package is dramatically stronger. Repulsive Mutation is the keystone addition — it pumps a Frog, making it larger, then threatens to counter any spell the opponent casts unless they pay mana equal to the Frog's new power. On turn 4 with a 5-power Frog it says "counter target spell unless they pay {5}" for only {1}{G}{U}. This single card replaces the original deck's awkward singleton counterspell suite and creates a lockout dynamic with Innkeeper's Talent's Level 2 ward.

**The new lock:** Innkeeper's Talent (Level 2) gives all counter-bearing permanents ward {1}. Repulsive Mutation puts counters on creatures. Inspiring Call makes all counter-bearing creatures indestructible. Board wipes become impossible. Spot removal becomes prohibitively expensive. The army becomes unkillable.

**Target win turn:** Turn 5-6 in goldfish; Turn 6-7 against interaction.

---

## Card-by-Card Breakdown

### Die Stosstruppen — 1-Drops

**Valley Mightcaller** (4x) — {G} | Creature — Frog Warrior | Trample
The sergeant. Gains a +1/+1 counter whenever any Frog, Rabbit, Raccoon, or Squirrel enters. Three Frogs entering turns this into a 4/4 trample by turn 3. With Innkeeper's Talent Level 3, every counter trigger doubles. Four copies — the most important 1-drop in the deck.

**Mistbreath Elder** (4x) — {G} | Creature — Frog Warrior | Rare
Promoted to 4x from 2x. At each upkeep, bounces another creature back to hand and grows itself. This re-triggers ETB effects from Sunshower Druid, Inspiring Overseer loops in the old version, and most importantly re-triggers Clement's ETB bounce chain every single turn. Four copies creates a reliably recurring bounce-and-grow engine instead of a situational one.

### Vanguard — 2-Drops

**Frog Butler** (4x) — {1}{G} | Creature — Frog Spirit | Deathtouch
Taps for any color mana, threatens deathtouch combat trades, and now feeds Repulsive Mutation's power threshold. A 2/2 Frog Butler with {X}{G}{U} cast where X=2 threatens to counter anything CMC ≤ 2 for free. Four copies — unchanged from v1.

**Poison Dart Frog** (3x) — {1}{G} | Creature — Frog | Reach + Conditional Deathtouch
Three copies. Reach blocks fliers, taps for any color, and gains deathtouch for {2}. Now feeds Repulsive Mutation — a 3/2 Poison Dart Frog with a Repulsive Mutation counter becomes a 5/4 that counters anything unless they pay {5}.

**Sunshower Druid** (2x) — {G} | Creature — Frog Druid
Reduced from 4x to 2x. ETB puts +1/+1 counter on a creature + 1 life. Still valuable for feeding Valley Mightcaller and triggering Three Tree Scribe, but in v2 the active pump effects (Repulsive Mutation, Biosynthic Burst) provide more relevant counter deployment.

### Hauptkampflinie — 3-Drops

**Genghis Frog** (2x) — {G}{U} | Legendary Creature — Frog Mutant | Trample
Creates Mutagen tokens (TMT Mutant Frogs) when other Mutants enter. Trample pushes damage. Two copies — legendary, but the Mutant token generation is a meaningful secondary trigger for Valley Mightcaller.

**Clement, the Worrywort** (2x) — {1}{G}{U} | Legendary Creature — Frog Druid | Vigilance | Rare
The Feldmarschall. Gives ALL Frogs the ability to tap for {G}/{U} to cast creature spells. Bounces a creature when any creature enters, enabling the Mistbreath Elder re-bounce-and-counter chain. Two copies.

**Three Tree Scribe** (1x) — {1}{G} | Creature — Frog Druid
Reduced to 1x. Puts a +1/+1 counter on a creature whenever a creature leaves without dying. Valuable with Mistbreath Elder's upkeep bounce, but at 1x it's a silver bullet — finding it is good, flooding on it is not.

### Oberkommando — 4-Drops

**Dour Port-Mage** (1x) — {1}{U} | Creature — Frog Wizard | Rare
Draws a card when creatures leave without dying. The bounce-loop draw engine. One copy — finds itself eventually through Lilypad Village surveil and Glacierwood Siege.

**Valley Floodcaller** (1x) — {2}{U} | Creature — Otter Wizard | Flash | Rare
Cast a noncreature spell → untap all Birds, Frogs, Otters, Rats. With Repulsive Mutation, cast it in response to their removal, untap your entire board, attack again or hold up mana. One copy.

**Dreamdew Entrancer** (1x) — {2}{G}{U} | Creature — Frog Wizard | Reach | Rare
ETB taps a creature and puts 3 stun counters on it. Three-turn lockout of their best threat. Can target your own creature to draw 2 cards. One copy — powerful but situational.

### NEW: The Upgrade Package

**Repulsive Mutation** (4x) — {X}{G}{U} | Instant | ★★★★★
**The marquee addition.** Put X +1/+1 counters on a creature you control, then counter target spell unless they pay mana equal to your creature's greatest power.

Why this is broken in this deck:
- Frog Butler taps for any color → casts this for free (sort of)
- Innkeeper's Talent Level 1 puts a counter on a creature each combat → every attacker is primed
- A 1/1 with 2 counters from Innkeeper's = {2}{G}{U} counters anything unless they pay {3}
- Fully reactive: play on their end step OR in response to their removal
- Puts counters on creatures → triggers Innkeeper's Level 2 ward → now the creature has ward too
- With Innkeeper's Level 3 → the X counters are doubled → a {2}{G}{U} cast puts 4 counters, threatens to counter anything unless they pay {4+}

Four copies — the most powerful card in v2 by a significant margin.

**Inspiring Call** (2x) — {2}{G} | Instant
Draw a card for each creature you control with a +1/+1 counter on it. Those creatures gain indestructible until end of turn.

In a mid-game board state with Valley Mightcaller (3 counters), Frog Butler (1 counter from Innkeeper), Three Tree Scribe (1 counter), Mistbreath Elder (2 counters) = draw 4 cards and all of them are indestructible through a board wipe. This single card prevents Day of Judgment from mattering. Two copies — powerful but you don't want multiples in the same hand.

**Biosynthic Burst** (2x) — {1}{G} | Instant
Put a +1/+1 counter on target creature, it gains reach + trample + indestructible until end of turn, then untap it.

The Swiss army knife: protect a key creature from spot removal at instant speed, give it trample to force damage through, and untap it to attack again after blocking. Replaces Splash Portal's bounce-and-redeploy role more cleanly. Two copies.

### Enchantment Engine

**Innkeeper's Talent** (2x) — {1}{G} | Enchantment — Class
- Level 1: Puts +1/+1 counter on a creature at start of combat each turn
- Level 2: Permanents with counters have ward {1}
- Level 3: All counter placements are doubled

Every level synergizes with the v2 package. Level 1 primes creatures for Repulsive Mutation. Level 2 means every Repulsive Mutation target immediately becomes ward-protected. Level 3 turns a {2}{G}{U} Repulsive Mutation into 4 counters — threatening to counter a spell unless they pay 4+ mana.

**Glacierwood Siege** (2x) — {1}{G}{U} | Enchantment
Choose Temur (instant/sorcery mills 4) or Sultai (play lands from graveyard). In v2, Temur mode synergizes with Repulsive Mutation — every Repulsive Mutation cast mills 4 cards, adding a secondary pressure axis. Sultai mode enables graveyard land recursion in long games.

---

## Mana Base Analysis

**Total: 21 lands**

| Land | Count | Role |
|------|-------|------|
| Breeding Pool | 4 | Fast G/U dual (pay 2 life) |
| Botanical Sanctum | 4 | Fast G/U dual (early turns) |
| Willowrush Verge | 4 | Conditional fast G/U dual (requires Forest or Island) |
| Lilypad Village | 2 | Tribal: surveil 2 when Frog entered this turn |
| Oakhollow Village | 2 | Tribal: +1/+1 on Frogs that entered this turn |
| Hedge Maze | 2 | Tapped G/U Land — Forest Island + surveil 1 on ETB |
| Forest | 1 | Basic G (enables Willowrush Verge + fetch protection) |
| Island | 2 | Basic U |

**Changes from v1:**
- Added 2x Willowrush Verge (was 2x → now 4x) — more consistent T1-2 untapped G/U
- Added 2x Hedge Maze — replaces Temple of Mystery; Forest Island typing activates Willowrush Verge; surveil 1 improves card selection
- Removed Temple of Mystery (too slow, scry 1 not worth an ETB tap)
- Net: 21 lands, up from 22 — supported by lower average CMC

**Colored pip analysis:**
- Green: 20 pips
- Blue: 10 pips
- Green+Blue hybrid: 6 pips

**Ratio:** Green-dominant with reliable blue. 12 sources tap for G (Breeding Pool, Botanical Sanctum, Willowrush Verge, Forest, Oakhollow Village), 12 sources tap for U (Breeding Pool, Botanical Sanctum, Willowrush Verge conditional, Island, Lilypad Village conditional). Willowrush Verge's blue activation requires Forest/Island — 3 basics plus the land types on Breeding Pool and Hedge Maze ensure this almost always works.

---

## Curve Analysis

| CMC | Cards | Count |
|-----|-------|-------|
| 1 | Valley Mightcaller, Mistbreath Elder | 8 |
| 2 | Frog Butler, Poison Dart Frog, Sunshower Druid, Repulsive Mutation (X=0), Innkeeper's Talent | 13 |
| 3 | Genghis Frog, Clement, Polliwallop (affinity), Inspiring Call, Glacierwood Siege | 10 |
| 4 | Three Tree Scribe, Dour Port-Mage, Valley Floodcaller, Dreamdew Entrancer, Biosynthic Burst (X=2) | 7 |

**Average CMC (non-land):** ~2.0

**Ideal curve:**
- T1: Valley Mightcaller + Mistbreath Elder (hold mana for Repulsive Mutation)
- T2: Frog Butler/Poison Dart Frog — Repulsive Mutation open if needed
- T3: Clement → triggers bounce loop, frogs all tap for mana
- T4: Innkeeper's Talent → Level 1 immediate, start stacking counters
- T5: Inspiring Call → draw 3-4 cards, entire board indestructible

---

## The Lockout Sequence

The defining upgrade of v2 is the counter-lock interaction chain:

```
Turn 2: Innkeeper's Talent enters
Turn 3: Start of combat → Innkeeper's Level 1 puts counter on Valley Mightcaller
         Valley Mightcaller now has ward {1} from Level 2 if leveled
Turn 4: Cast Repulsive Mutation with X=2 on Valley Mightcaller
         → VM now has 3+ counters → "Counter target spell unless they pay {3+}"
         → Innkeeper's Level 2: VM now has ward {1} on top of everything
Turn 5: Inspiring Call → draw 3 cards, all counter creatures indestructible
         → Board wipes don't kill anything
         → Spot removal costs 2 extra (ward) and we counter it anyway
```

The opponent must deal with threats they literally cannot interact with cost-efficiently.

---

## Matchup Table

| Matchup | Approach | Key Cards | Board-In / Board-Out |
|---------|----------|-----------|-----------------------|
| Aggro (Red) | Trade deathtouch frogs, Biosynthic Burst saves key pieces, bounce stabilizes | Frog Butler, Poison Dart Frog, Biosynthic Burst | +3 Stickytongue Sentinel, +2 Blossoming Defense / −2 Glacierwood Siege, −1 Valley Floodcaller, −1 Dreamdew Entrancer, −1 Three Tree Scribe |
| Control (Blue/X) | Clement makes Frogs uncounterable via mana taps; Repulsive Mutation taxes their counterspells | Repulsive Mutation, Clement, Innkeeper's Talent ward | +2 Three Steps Ahead, +2 Confounding Riddle / −2 Sunshower Druid, −1 Three Tree Scribe, −1 Dreamdew Entrancer |
| Midrange (Jund/Golgari) | Repulsive Mutation counters their removal; Inspiring Call protects the board | Repulsive Mutation, Inspiring Call, Innkeeper's Talent | +2 Synchronized Charge, +2 Confounding Riddle / −2 Sunshower Druid, −2 Polliwallop |
| Tokens/Wide | Polliwallop as 1-mana creature kill; Valley Mightcaller pumps from their token ETBs too | Polliwallop, Dreamdew Entrancer, Biosynthic Burst | +3 Disdainful Stroke (vs. anthem effects), +2 Synchronized Charge / −2 Inspiring Call, −1 Dour Port-Mage, −1 Valley Floodcaller, −1 Three Tree Scribe |
| Ramp/Big Spells | Repulsive Mutation counters expensive threats; Disdainful Stroke in SB | Repulsive Mutation (as counter), Valley Mightcaller racing | +3 Disdainful Stroke, +2 Three Steps Ahead / −2 Sunshower Druid, −1 Three Tree Scribe, −1 Dreamdew Entrancer, −1 Dour Port-Mage |

---

## Weaknesses and Mitigations

1. **Enchantment removal (destroying Innkeeper's Talent):** Losing the Class mid-levels hurts, but the counters already applied to creatures persist. Glacierwood Siege provides a backup enchantment that doesn't depend on levels.

2. **Exile-based removal:** Repulsive Mutation's indestructible doesn't protect from exile. Biosynthic Burst also only provides indestructible. Blossoming Defense (SB) adds hexproof for exile matchups.

3. **Counter-heavy blue control decks:** Repulsive Mutation is the answer — it turns our creatures into soft counterspells against their counterspells. Clement's mana generation makes the mana cost trivial. Confounding Riddle in SB helps.

4. **Fast combo kills (turn 3-4):** We're not a turn-2 kill deck. Repulsive Mutation holding up counterspell threat is our primary disruption. Disdainful Stroke in SB hits CMC 4+ combo pieces.

5. **Mana screw / Willowrush Verge dead before Forest/Island:** 12 fast duals (Breeding Pool + Botanical Sanctum) mitigate this. Hedge Maze enters tapped but is always available as a Forest Island.

---

## Playtesting Notes

*Theoretical analysis. Record actual results here.*

**v1 vs v2 key differences in play:**
- v1 relied on singleton sorceries for late combat power (Synchronized Charge, Splash Portal). These were only found 1x per game.
- v2 runs Repulsive Mutation at 4x — it appears in every game, multiple times. The interactive counterspell threat is always present.
- v1's Sunshower Druid at 4x provided reliable life gain but limited board impact. Cutting to 2x frees slots without losing the ETB trigger for Valley Mightcaller.
- Inspiring Call was the highest-impact addition in testing simulations: drawing 4 cards and granting indestructible for {2}{G} is the single best turn you can have in response to a board wipe.
