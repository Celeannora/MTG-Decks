# Ouroboroid Ascension — Simic Counter Doubling

> *"It grows. It doubles. It cannot be stopped."*

---

## Database Query Report

### Queries Run

| Query | Results |
|-------|---------|
| `search_cards.py --name "Ouroboroid"` | 1 candidate |
| `search_cards.py --type creature --colors GU --tags pump --oracle "+1/+1 counter"` | 40+ candidates |
| `search_cards.py --type creature --colors GU --oracle "put a +1/+1 counter"` | 30+ candidates |
| `search_cards.py --type enchantment --colors GU --oracle "counter"` | 20+ candidates |
| `search_cards.py --type instant --colors GU --tags pump --cmc-max 3` | 37 candidates |
| `search_cards.py --type land --colors GU` | 40+ candidates |
| Individual detail lookups (Doubling Season, Bristly Bill, Mossborn Hydra, etc.) | 20+ reads |

### Per-Card Verification (60 mainboard + 15 sideboard)

**Mainboard:**
✓ District Mascot (x4) — creature/creature_d1.csv — (DFT) 344
✓ Bristly Bill, Spine Sower (x4) — creature/creature_b2.csv — (POTJ) 157p
✓ Jadelight Spelunker (x4) — creature/creature_j.csv — (LCI) 382
✓ Mossborn Hydra (x4) — creature/creature_m2.csv — (FDN) 337
✓ Ouroboroid (x3) — creature/creature_o.csv — (EOE) 201
✓ Tyvar, the Pummeler (x2) — creature/creature_t2.csv — (DSK) 353
✓ Deepfathom Echo (x2) — creature/creature_d1.csv — (PLCI) 228s
✓ Goldvein Hydra (x1) — creature/creature_g2.csv — (POTJ) 167p
✓ Repulsive Mutation (x4) — instant/instant_r.csv — (MKM) 227
✓ Inspiring Call (x3) — instant/instant_i.csv — (IMA) 169
✓ Biosynthic Burst (x2) — instant/instant_b.csv — (EOE) 173
✓ Doubling Season (x2) — enchantment/enchantment_d.csv — (FDN) 438
✓ Bioengineered Future (x2) — enchantment/enchantment_b.csv — (EOE) 172
✓ Case of the Trampled Garden (x1) — enchantment/enchantment_c.csv — (MKM) 156
✓ Innkeeper's Talent (x2) — enchantment/enchantment_i.csv — (SLP) 45
✓ Breeding Pool (x4) — land/land_b.csv — (EXP) 15
✓ Botanical Sanctum (x4) — land/land_b.csv — (SLD) 1376
✓ Willowrush Verge (x4) — land/land_w.csv — (DFT) 375
✓ Fabled Passage (x2) — land/land_f1.csv — (SLD) 727
✓ Hedge Maze (x2) — land/land_h.csv — (PMKM) 262s
✓ Escape Tunnel (x1) — land/land_e.csv — (TMT) 184
✓ Forest (x2) — land/land_f1.csv — (BLB) 280
✓ Island (x1) — land/land_i1.csv — (ELD) 255

**Sideboard:**
✓ Disdainful Stroke (x3) — instant/instant_d.csv — (GRN) 37
✓ Blossoming Defense (x3) — instant/instant_b.csv — (ECL) 167
✓ Confounding Riddle (x2) — instant/instant_c.csv — (LCI) 50
✓ Synchronized Charge (x2) — sorcery/sorcery_s.csv — (TDM) 162
✓ Snakeskin Veil (x2) — instant/instant_s.csv — (OTJ) 181
✓ Case of the Trampled Garden (x2) — enchantment/enchantment_c.csv — (MKM) 156
✓ Tyvar, the Pummeler (x1) — creature/creature_t2.csv — (DSK) 353

### Validation Script Result

```
$ python scripts/validate_decklist.py Decks/2026-03-21_Ouroboroid_Ascension/decklist.txt
✅ VALIDATION PASSED
All cards are legal and present in the database.
Mainboard: 60 cards | Sideboard: 15 cards
```

---

## Executive Summary

**Deck name:** Ouroboroid Ascension
**Colors:** Simic (Green/Blue) — heavily green
**Format:** Standard
**Archetype:** Counter Doubling / Stompy Combo

**The plan:** Flood the board with landfall-enabled creatures that enter with +1/+1 counters, then drop Ouroboroid on turn 4 and watch every creature on the board become a titan. Doubling Season doubles every counter placed — Ouroboroid's combat trigger that would put 4 counters on each creature instead puts 8. Bristly Bill doubles all counters with a single activation. Tyvar, the Pummeler turns the largest creature's power into a universal +X/+X buff. You win through an unstoppable creature combat on turn 5-6.

**Kill sequence target (turns 4-6):**
- T4: Ouroboroid enters (4/4). Board has Bristly Bill + Mossborn Hydra (doubled landfall counters) + District Mascot
- T5 combat: Ouroboroid puts 4 counters on every creature → 8 with Doubling Season → Mossborn is now 11/11+, Ouroboroid is 8/8+
- T5 Bristly Bill activation: doubles all counters → Ouroboroid 16/16, Mossborn 22/22+
- T5 Tyvar ability: all creatures get +16/+16 until EOT → attack for lethal

---

## The Counter Math

This deck wins by making the numbers absurd through stacking doublers.

### The Core Doubling Stack

| Effect | Source | Trigger |
|--------|--------|---------|
| +1 counter per land drop | Bristly Bill (Landfall) | Each land entering |
| ×2 all counter placements | Doubling Season | Passive always-on |
| ×2 all counters per combat | Ouroboroid (X = its power) | Beginning of combat |
| ×2 all counters activated | Bristly Bill ({3}{G}{G}) | Once per turn activated |
| Enters with extra counters | Bioengineered Future | Per land dropped this turn |
| +X/+X to all | Tyvar, the Pummeler ({3}{G}{G}) | Once per turn |

### Turn-by-Turn Power Projection

**Without Doubling Season:**
| Turn | Ouroboroid Power | Counters Added Each | Board Total Counters |
|------|-----------------|---------------------|---------------------|
| T4 (enters) | 4 | — | — |
| T5 | 8 | 4 per creature | All +4 |
| T6 | 16 | 8 per creature | All +12 |
| T7 | 32 | 16 per creature | All +28 |

**With Doubling Season (×2 every counter):**
| Turn | Ouroboroid Power | Counters Added Each | Board Total |
|------|-----------------|---------------------|------------|
| T4 (enters) | 4 | — | — |
| T5 | 12 | 8 per creature | All +8 |
| T6 | 28 | 24 per creature | All +32 |

**With Doubling Season + Bristly Bill activation after Ouroboroid trigger:**
- T5: Ouroboroid adds 8 (doubled from 4) → becomes 12/12. Bristly Bill activation doubles all → Ouroboroid 24/24, other creatures 3× their base.

This is a literal one-turn-kill from turn 5 onward.

---

## Card-by-Card Breakdown

### Foundation — 1-Drops

**District Mascot** (4x) — {G} | Creature — Dog Mount
Enters with a +1/+1 counter already on it. With Doubling Season: enters with 2 counters. With Bioengineered Future and a land dropped this turn: enters with 2+2=4 counters on turn 4. Triggers Bristly Bill's Landfall if a land entered the same turn. Saddle 1 activation gets a counter when attacking while saddled. Four copies — it's a 1-drop with a free counter that feeds everything.

**Bristly Bill, Spine Sower** (4x) — {1}{G} | Legendary Creature — Plant Druid | Mythic
**The backbone of the ramp engine.** Every land that enters puts a +1/+1 counter on a target creature. With Doubling Season this becomes 2 counters per land. The {3}{G}{G} activated ability then doubles all +1/+1 counters on every creature you control — once per turn, available at instant speed if you have the mana open. Note: Bristly Bill's doubling is a separate effect from Doubling Season; they stack multiplicatively. If you activate Bristly Bill with Doubling Season in play, the "double" becomes 4× the original count. Four copies — the most important creature in the deck.

**Jadelight Spelunker** (4x) — {X}{G} | Creature — Merfolk Scout | Rare
Cast for X = available extra mana. Explores X times — each non-land card it hits puts a +1/+1 counter on it. With Doubling Season, each explore counter becomes 2. Cast on T2 for X=1 → likely 2/2 or 3/3. Cast on T4 for X=3 → likely 5/5 to 7/7 depending on land/non-land ratio. Fixes mana if it hits lands, bulks up if it hits spells. Four copies.

### Engine — 3-Drops

**Mossborn Hydra** (4x) — {2}{G} | Creature — Elemental Hydra | Rare | Trample
Enters with 1 counter (2 with Doubling Season). Landfall: doubles counters on it. So: T3 play, T3 land drop → 4 counters (8 with DS). T4 land drop → 8 counters (16 with DS). A Mossborn Hydra on turn 3 with a turn-4 land and Doubling Season is a 16/16 trample before Ouroboroid even hits. Four copies.

**Innkeeper's Talent** (2x) — {1}{G} | Enchantment — Class
Level 1: counter on a creature each combat. Level 2: all counter-bearing creatures get ward {1}. Level 3: all counter placements are doubled (stacks with Doubling Season for ×4 total). Two copies — powerful but slow to level; the deck wins before Level 3 often. Primarily run for Level 1 and Level 2 protection.

**Bioengineered Future** (2x) — {1}{G}{G} | Enchantment | Rare
Creates a Lander token (tap/sacrifice to fetch a basic land). Each creature you control enters with an additional +1/+1 counter for each land that entered this turn. Combined with Fabled Passage or Escape Tunnel (which put lands into play): cast a creature on the same turn as a fetch → it enters with 2+ extra counters. With Doubling Season those extra counters are doubled. Two copies.

### Win Conditions

**Ouroboroid** (3x) — {2}{G}{G} | Creature — Plant Wurm | Mythic
**The namesake card.** At the beginning of combat, puts X +1/+1 counters on EVERY creature you control, where X is Ouroboroid's own power. It starts as 4/4. With Doubling Season, each trigger puts 2X instead of X. The growth is exponential not linear — every combat trigger makes the next trigger larger:

```
T4 (enters): Ouroboroid = 4/4
T5 combat trigger: +4 to all (×2 with DS = +8). Ouroboroid = 8/8 (or 12/12 with DS)
T5 Bristly Bill activation: double all → Ouroboroid 24/24
T6 combat trigger: +24 to all. Ouroboroid = 48/48
```

Three copies — mythic and legendary; three is enough to see it reliably without flooding on a legendary you can't have two of in play.

**Tyvar, the Pummeler** (2x) — {1}{G}{G} | Legendary Creature — Elf Warrior | Mythic
{3}{G}{G}: All creatures you control get +X/+X until end of turn where X is the greatest power among your creatures. After Ouroboroid's combat trigger fires, the greatest power might be 12+. Activate Tyvar: every creature swings as a 20+/20+. Two copies — legendary and expensive to activate, but closes the game immediately.

**Goldvein Hydra** (1x) — {X}{G} | Creature — Hydra | Mythic
Vigilance, trample, haste. Enters with X counters. With Doubling Season, enters with 2X counters. On the turn you cast it for X=5 with DS in play: 10/10 vigilance trample haste that attacks immediately. Dies: creates X Treasure tokens (doubles to 2X with DS). One copy — a late-game mana sink and surprise hasty finisher.

### Interaction

**Repulsive Mutation** (4x) — {X}{G}{U} | Instant
Put X counters on a creature. Then counter target spell unless they pay equal to that creature's power. In this deck, the power threshold is astronomical by turn 4-5 — casting Repulsive Mutation for X=1 on a 16/16 Mossborn Hydra means "counter target spell unless they pay 17" for {1}{G}{U}. The primary interactive piece and also a pump tool for more counters.

**Inspiring Call** (3x) — {2}{G} | Instant
Draw a card for each creature with a +1/+1 counter on it. Make them all indestructible until EOT. In this deck almost every creature has counters by turn 3. Typically draws 4-5 cards and makes the board immune to wipes. Three copies.

**Biosynthic Burst** (2x) — {1}{G} | Instant
+1/+1 counter + reach + trample + indestructible + untap for {1}{G}. Protects Ouroboroid from exile removal and untaps it for a second attack (useful with Tyvar's tap ability). With Doubling Season, the +1 counter becomes +2.

**Deepfathom Echo** (2x) — {2}{G}{U} | Creature — Merfolk Spirit | Rare
At the beginning of combat: explores (counter or land to hand), then can copy another creature until EOT. The key use: become a copy of Ouroboroid. That "copy" enters at Ouroboroid's current power and triggers the combat ability again — effectively doubling Ouroboroid's trigger in the same combat. Two copies — important enough to run but not a four-of.

---

## Mana Base Analysis

**Total: 20 lands**

| Land | Count | Role |
|------|-------|------|
| Breeding Pool | 4 | Fast G/U dual |
| Botanical Sanctum | 4 | Fast G/U dual |
| Willowrush Verge | 4 | Conditional G/U dual (Forest/Island required) |
| Fabled Passage | 2 | Fetch → triggers Bristly Bill landfall |
| Hedge Maze | 2 | Forest Island + surveil 1 |
| Escape Tunnel | 1 | Fetch + unblockable utility |
| Forest | 2 | Basic G |
| Island | 1 | Basic U |

**Why fetches matter here:** Fabled Passage and Escape Tunnel actively trigger Bristly Bill's Landfall ability. Every fetch land puts an extra counter on a creature. With Doubling Season: every fetch puts 2 counters. Bioengineered Future makes fetching on the same turn as playing a creature give that creature bonus entry counters.

**Colored pip analysis:**
- Green: 26 pips (heavily green)
- Blue: 7 pips (primarily for Repulsive Mutation)

The deck is functional on 2-3 green sources. Blue is splashed only for Repulsive Mutation and Deepfathom Echo. 13 green sources, 8 blue sources out of 20 lands.

---

## Curve Analysis

| CMC | Cards | Count |
|-----|-------|-------|
| 1 | District Mascot | 4 |
| 2 | Bristly Bill, Jadelight Spelunker (X=1), Innkeeper's Talent, Repulsive Mutation, Biosynthic Burst | 14 |
| 3 | Mossborn Hydra, Bioengineered Future, Case of the Trampled Garden, Inspiring Call | 12 |
| 4 | Ouroboroid, Deepfathom Echo, Repulsive Mutation (X=2), Jadelight Spelunker (X=3) | 7 |
| 5 | Doubling Season, Tyvar activation, Bristly Bill activation | variable |

**Average CMC (non-land):** ~2.8

**Ideal curve:**
- T1: District Mascot (enters with 1 counter, primed for Bristly Bill) or Jadelight Spelunker (X=0, explores)
- T2: Bristly Bill, Spine Sower (now every land = counter)
- T3: Mossborn Hydra (enters with 2 counters) + land drop → Mossborn doubles to 4 counters from landfall
- T4: Ouroboroid → combat trigger puts 4 counters on every creature → or Doubling Season this turn
- T5: If Doubling Season on T4: Ouroboroid trigger puts 8 counters → Bristly Bill doubles all → kill

---

## The Interaction Chains

```
Bristly Bill + Fabled Passage
  → Fetch triggers Landfall → +1 counter on any creature
  → With Doubling Season: +2 counters per fetch

Mossborn Hydra + Bristly Bill + Doubling Season
  → T3: Mossborn enters with 2 counters (DS doubles 1→2)
  → T3 land: Landfall doubles Mossborn's counters → 4
  → T3 with DS: each landfall doubles → 8 counters on T3
  → Mossborn is an 11/11 trample by end of T3

Ouroboroid + Doubling Season + Bristly Bill activation
  → Ouroboroid combat trigger: +8 to all (4 doubled)
  → Bristly Bill {3}{G}{G}: double all counters again → ×2
  → Net: ×4 counters added vs. base scenario

Deepfathom Echo copying Ouroboroid
  → At beginning of combat:
     1. Echo explores (likely +1 counter, +2 with DS)
     2. Echo becomes a copy of Ouroboroid until EOT
     3. "Copy Ouroboroid" triggers its own combat ability
     4. Now TWO Ouroboroid triggers fire in the same combat
  → With Ouroboroid at 12 power: each trigger adds 12+ counters to all
  → Two triggers: +24 to all creatures in one combat

Repulsive Mutation on anything after Ouroboroid fires
  → Ouroboroid fires: all creatures at 12+ power
  → Cast Repulsive Mutation for X=1 on anything → "counter target spell unless pay 13+"
  → Their board wipe gets countered for {1}{G}{U}

Inspiring Call after Ouroboroid fires
  → Every creature has 8+ new counters → draw 6-7 cards
  → All creatures indestructible until EOT
  → They cannot wipe the board
```

---

## Matchup Table

| Matchup | Approach | Key Cards | Board-In / Board-Out |
|---------|----------|-----------|-----------------------|
| Aggro (Red/White) | District Mascot blocks profitably (1 counter = 2/2 for {G}); Biosynthic Burst saves Bristly Bill | Biosynthic Burst, District Mascot, Inspiring Call | +3 Blossoming Defense, +2 Snakeskin Veil / −2 Doubling Season, −1 Goldvein Hydra, −1 Deepfathom Echo, −1 Case of the Trampled Garden |
| Control (Blue) | Repulsive Mutation taxes counterspells; Inspiring Call draws through wipes | Repulsive Mutation, Inspiring Call, Deepfathom Echo | +2 Confounding Riddle, +2 Disdainful Stroke / −2 Bioengineered Future, −1 Tyvar, −1 Case of the Trampled Garden |
| Midrange | Out-scale on counter accumulation; Repulsive Mutation answers spot removal | Ouroboroid, Bristly Bill, Mossborn Hydra | +2 Synchronized Charge, +2 Case of the Trampled Garden / −1 Deepfathom Echo, −1 Goldvein Hydra, −1 Tyvar, −1 Biosynthic Burst |
| Ramp/Domain | Race or counter their key spells; Tyvar kills before they untap with big mana | Disdainful Stroke, Repulsive Mutation, Tyvar | +3 Disdainful Stroke, +2 Confounding Riddle / −2 Bioengineered Future, −1 Case, −1 Deepfathom Echo, −1 Goldvein Hydra |
| Tokens/Wide | Mossborn and Ouroboroid grow past any token army; trample wins | Mossborn Hydra, Tyvar, Ouroboroid | +2 Synchronized Charge (trample), +1 Tyvar / −1 Case, −2 Biosynthic Burst |

---

## Weaknesses and Mitigations

1. **Ouroboroid removed before combat trigger:** Priority window exists between declaring attacks and the trigger. Biosynthic Burst (instant speed indestructible + untap) answers destroy-effects at {1}{G}. Repulsive Mutation answers non-exile removal while countering their response spell.

2. **Doubling Season answered before Ouroboroid plays:** The deck still wins without Doubling Season — Bristly Bill's landfall engine grows creatures meaningfully on its own. DS is an accelerant, not a requirement.

3. **Exile-based removal (Sunfall, etc.):** Inspiring Call's indestructible doesn't protect from exile. Blossoming Defense's hexproof (sideboard) is the answer for key creatures. Don't put all counters on one creature.

4. **Fast combo kills before we stabilize:** We can win by turn 5-6 but not turn 3. Counter suite (Repulsive Mutation + Disdainful Stroke SB) provides some disruption. Repulsive Mutation on a 2/2 Jadelight Spelunker on turn 2 still forces them to pay {2} for any spell.

5. **Legendary redundancy (Bristly Bill, Tyvar):** Both are legendary 4-ofs. Having two Bristly Bills in hand after one is in play wastes a draw. Mitigated by the fact that the second is always a live card to play (it triggers the Landfall counter for the first one when it enters, then you discard the extra).
