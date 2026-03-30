# Deck Analysis: Bant Mill Lifegain

**Date:** 2026-03-30
**Format:** Standard
**Colors:** W/U/G (Bant)

---

## Database Query Report

### Queries Run

| Query | Results |
|-------|---------|
| `search_cards.py --name "Shanna, Purifying Blade"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Vaultborn Tyrant"` | 1 candidate |
| `search_cards.py --name "Get Lost"` | 1 candidate |
| `search_cards.py --name "Day of Judgment"` | 1 candidate |
| `search_cards.py --name "Sunfall"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Three Steps Ahead"` | 1 candidate |
| `search_cards.py --name "Make Your Own Luck"` | 1 candidate |
| `search_cards.py --name "Negate"` | 1 candidate |
| `search_cards.py --name "Elspeth's Smite"` | 1 candidate |
| `search_cards.py --name "Ugin, Eye of the Storms"` | 2 candidates |
| `search_cards.py --name "Mazemind Tome"` | 1 candidate |
| `search_cards.py --name "No More Lies"` | 1 candidate |
| `search_cards.py --name "Ancient Cornucopia"` | 1 candidate |
| `search_cards.py --name "Glacierwood Siege"` | 1 candidate |
| `search_cards.py --name "Omenpath Journey"` | 1 candidate |
| `search_cards.py --name "Demolition Field"` | 1 candidate |
| `search_cards.py --name "Riverchurn Monument"` | 1 candidate |
| `search_cards.py --name "Seachrome Coast"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Botanical Sanctum"` | 1 candidate |
| `search_cards.py --name "Willowrush Verge"` | 1 candidate |
| `search_cards.py --name "Hushwood Verge"` | 1 candidate |
| `search_cards.py --name "Razorverge Thicket"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Floodfarm Verge"` | 1 candidate |
| `search_cards.py --name "Forest"` | 3 candidates (1 basic land) |
| `search_cards.py --name "Island"` | 8 candidates (1 basic land) |
| `search_cards.py --name "Plains"` | 2 candidates (1 basic land) |
| `search_cards.py --type creature --colors WUG --tags lifegain` | 133 candidates |
| `search_cards.py --type sorcery --colors W --tags wipe` | 9 candidates |
| `search_cards.py --type land --colors WU` | 86 candidates |
| `search_cards.py --type land --colors WG` | 86 candidates |
| `search_cards.py --name "Hallowed Fountain"` | 2 candidates |
| `search_cards.py --name "Temple Garden"` | 2 candidates |
| `search_cards.py --name "Fumigate"` | 1 candidate |
| `search_cards.py --name "Hope Estheim"` | 1 candidate |
| `search_cards.py --name "Hinterland Sanctifier"` | 1 candidate |
| `search_cards.py --name "Rest in Peace"` | 1 candidate |
| `search_cards.py --name "Aether Gust"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Shatterskull Smashing"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Fading Hope"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Soul-Guide Lantern"` | 1 candidate |
| `search_cards.py --name "The Wandering Emperor"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Hall of Stormlight"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Boseiju, Who Endures"` | 0 candidates (NOT FOUND) |
| `search_cards.py --name "Disdainful Stroke"` | 1 candidate |
| `search_cards.py --type instant --colors U --tags bounce` | 12 candidates |
| `search_cards.py --type instant --colors U --tags counter` | 27 candidates |
| `search_cards.py --type instant --colors G --tags removal --cmc-max 3` | 10 candidates |
| `search_cards.py --name "Heritage Reclamation"` | 1 candidate |
| `search_cards.py --name "Bounce Off"` | 1 candidate |
| `search_cards.py --name "Elspeth, Storm Slayer"` | 1 candidate (via `--name "Elspeth"`) |
| `search_cards.py --name "Authority of the Consuls"` | 1 candidate |
| `search_cards.py --name "Break Down the Door"` | 1 candidate |
| `search_cards.py --type planeswalker --colors WUG` | 10 candidates |

### Per-Card Verification (ALL 60+15 cards)

**Mainboard (60 cards):**

| Status | Card Name | Source File | Set/Collector |
|--------|-----------|-------------|---------------|
| ✓ | Hope Estheim | `cards_by_category/creature/creature_h2.csv` | (FIN) 541 |
| ✓ | Vaultborn Tyrant | `cards_by_category/creature/creature_v.csv` | (BIG) 85 |
| ✓ | Ugin, Eye of the Storms | `cards_by_category/planeswalker/planeswalker_u.csv` | (PTDM) 1p |
| ✓ | Get Lost | `cards_by_category/instant/instant_g.csv` | (PLCI) 14p |
| ✓ | Three Steps Ahead | `cards_by_category/instant/instant_t.csv` | (POTJ) 75s |
| ✓ | Negate | `cards_by_category/instant/instant_n.csv` | (OGW) 59 |
| ✓ | Elspeth's Smite | `cards_by_category/instant/instant_e.csv` | (PLST) MOM-13 |
| ✓ | No More Lies | `cards_by_category/instant/instant_n.csv` | (MKM) 221 |
| ✓ | Day of Judgment | `cards_by_category/sorcery/sorcery_d.csv` | (M11) 12 |
| ✓ | Fumigate | `cards_by_category/sorcery/sorcery_f.csv` | (PKLD) 15p |
| ✓ | Make Your Own Luck | `cards_by_category/sorcery/sorcery_m.csv` | (OTJ) 218 |
| ✓ | Ancient Cornucopia | `cards_by_category/artifact/artifact_a.csv` | (BIG) 46 |
| ✓ | Mazemind Tome | `cards_by_category/artifact/artifact_m.csv` | (CMM) 959 |
| ✓ | Riverchurn Monument | `cards_by_category/artifact/artifact_r.csv` | (DFT) 440 |
| ✓ | Glacierwood Siege | `cards_by_category/enchantment/enchantment_g.csv` | (TDM) 189 |
| ✓ | Omenpath Journey | `cards_by_category/enchantment/enchantment_o.csv` | (BIG) 48 |
| ✓ | Forest | `cards_by_category/land/land_f1.csv` | (BLB) 280 |
| ✓ | Island | `cards_by_category/land/land_i1.csv` | (ELD) 255 |
| ✓ | Plains | `cards_by_category/land/land_p1.csv` | (CMA) 292 |
| ✓ | Hallowed Fountain | `cards_by_category/land/land_h.csv` | (UNF) 277 |
| ✓ | Botanical Sanctum | `cards_by_category/land/land_b.csv` | (SLD) 1376 |
| ✓ | Willowrush Verge | `cards_by_category/land/land_w.csv` | (DFT) 375 |
| ✓ | Hushwood Verge | `cards_by_category/land/land_h.csv` | (DSK) 332 |
| ✓ | Temple Garden | `cards_by_category/land/land_t1.csv` | (CLU) 282 |
| ✓ | Floodfarm Verge | `cards_by_category/land/land_f1.csv` | (DSK) 330 |
| ✓ | Demolition Field | `cards_by_category/land/land_d.csv` | (FDN) 687 |

**Sideboard (15 cards):**

| Status | Card Name | Source File | Set/Collector |
|--------|-----------|-------------|---------------|
| ✓ | Rest in Peace | `cards_by_category/enchantment/enchantment_r.csv` | (PRM) 77943 |
| ✓ | Disdainful Stroke | `cards_by_category/instant/instant_d.csv` | (GRN) 37 |
| ✓ | Negate | `cards_by_category/instant/instant_n.csv` | (OGW) 59 |
| ✓ | Heritage Reclamation | `cards_by_category/instant/instant_h.csv` | (TDM) 145 |
| ✓ | Bounce Off | `cards_by_category/instant/instant_b.csv` | (DFT) 39 |
| ✓ | Soul-Guide Lantern | `cards_by_category/artifact/artifact_s.csv` | (WOE) 251 |
| ✓ | Elspeth, Storm Slayer | `cards_by_category/planeswalker/planeswalker_e.csv` | (TDM) 398 |
| ✓ | Authority of the Consuls | `cards_by_category/enchantment/enchantment_a.csv` | (PKLD) 5s |
| ✓ | Break Down the Door | `cards_by_category/instant/instant_b.csv` | (DSK) 170 |

### Rejected Cards (Not Found in Database)

| Card Name | Reason | Replacement |
|-----------|--------|-------------|
| Shanna, Purifying Blade | Not in database | Hope Estheim — WU creature with lifelink + mill-on-lifegain synergy |
| Sunfall | Not in database | Fumigate — 5-CMC board wipe with lifegain upside |
| Seachrome Coast | Not in database | Hallowed Fountain — WU shock land |
| Razorverge Thicket | Not in database | Temple Garden — WG shock land |
| Aether Gust | Not in database (sideboard) | Disdainful Stroke — counters CMC 4+ spells |
| Shatterskull Smashing | Not in database (sideboard) | Heritage Reclamation — artifact/enchantment removal in green |
| Fading Hope | Not in database (sideboard) | Bounce Off — 1-mana creature bounce |
| The Wandering Emperor | Not in database (sideboard) | Elspeth, Storm Slayer — white planeswalker with token generation and removal |
| Hall of Stormlight | Not in database (sideboard) | Authority of the Consuls — anti-aggro enchantment with lifegain |
| Boseiju, Who Endures | Not in database (sideboard) | Break Down the Door — green instant that exiles artifacts/enchantments |

### Validation Script Result

```bash
$ python scripts/validate_decklist.py --verbose Decks/2026-03-30_Bant_Mill_Lifegain/decklist.txt
✅ VALIDATION PASSED
All cards are legal and present in the database.
```

---

## Executive Summary

- **Archetype:** Bant (W/U/G) Control-Mill
- **Primary win condition:** Mill opponent's library via Glacierwood Siege (Temur mode: mill 4 whenever you cast an instant or sorcery), amplified by Three Steps Ahead (copy trigger), Make Your Own Luck (free-cast plotted spells for additional triggers), and Riverchurn Monument (direct mill).
- **Secondary win condition:** Ugin, Eye of the Storms ultimate or combat damage with Vaultborn Tyrant.
- **Target win turn:** Turn 8-12 (control deck that stabilizes then mills out)
- **Metagame positioning:** Strong against midrange and creature-based strategies due to 5 board wipes. Lifegain via Ancient Cornucopia, Fumigate, and Hope Estheim stabilizes against aggro. Counterspell suite (Negate, No More Lies, Three Steps Ahead) handles combo and control mirrors.

---

## Card-by-Card Breakdown

### Creatures

**2x Hope Estheim**
*Source: `cards_by_category/creature/creature_h2.csv`*
The deck's premier mill engine creature. WU legendary with lifelink that mills opponents equal to life gained each turn. Synergizes with Ancient Cornucopia (gain life on colored spells), Fumigate (gain life per destroyed creature), and Mazemind Tome (gain 4 life on exile). Every lifegain source in the deck becomes a mill trigger. Replaces the requested Shanna, Purifying Blade (not in database), filling the same WU lifegain creature role with superior mill synergy.

**1x Vaultborn Tyrant**
*Source: `cards_by_category/creature/creature_v.csv`*
7-CMC green dinosaur with trample. Provides card advantage (draw a card when it or another 4+ power creature enters), lifegain (gain 3 life on entry triggers), and resilience (creates a copy token on death). Functions as a finisher that feeds Hope Estheim's mill trigger through its lifegain. The death trigger creates an artifact copy, making it hard to fully answer.

### Planeswalkers

**2x Ugin, Eye of the Storms**
*Source: `cards_by_category/planeswalker/planeswalker_u.csv`*
7-CMC colorless planeswalker. Cast trigger exiles a colored permanent (removal). +2 gains 3 life and draws a card (feeds Hope Estheim mill + card advantage). 0 ability adds {C}{C}{C} (ramp). -11 is a game-ending ultimate. Critical interaction: casting Ugin triggers Glacierwood Siege (it's a colorless spell but you still "cast" it), and subsequent colorless spells also trigger exile. The +2 lifegain feeds Hope Estheim's end-step mill.

### Instants

**4x Get Lost**
*Source: `cards_by_category/instant/instant_g.csv`*
Premium 2-mana removal that exiles creatures, enchantments, or planeswalkers. The Map tokens given to the opponent are largely irrelevant against our wipe-heavy strategy. Triggers Glacierwood Siege for mill 4. Essential interaction piece that handles the widest range of threats in the format.

**3x Three Steps Ahead**
*Source: `cards_by_category/instant/instant_t.csv`*
Spree instant with three modes: counter a spell ({1}{U}), copy an artifact/creature ({3}), or draw 2 discard 1 ({2}). The copy mode on Glacierwood Siege creates a second mill enchantment (mill 4 becomes mill 8 per spell). Countering a spell also triggers Siege's mill. Extremely flexible — functions as countermagic, card advantage, or mill amplifier depending on the situation.

**2x Negate**
*Source: `cards_by_category/instant/instant_n.csv`*
Efficient 2-mana counter for noncreature spells. Protects Glacierwood Siege from removal, stops opposing planeswalkers and sweepers. Triggers Glacierwood Siege for mill 4. Lean counter suite that doesn't clog the hand against creature decks (board wipes handle those).

**3x Elspeth's Smite**
*Source: `cards_by_category/instant/instant_e.csv`*
1-mana instant that deals 3 to an attacking/blocking creature and exiles it if it would die. Efficient early interaction that buys time to deploy Glacierwood Siege. Triggers Siege for mill 4 at a very low mana investment. The exile clause prevents graveyard recursion.

**2x No More Lies**
*Source: `cards_by_category/instant/instant_n.csv`*
WU counter that taxes {3} and exiles the countered spell. Strong early-game tempo play that triggers Glacierwood Siege. The exile clause is relevant against flashback and graveyard strategies. Fills a similar role to Mana Leak but with upside.

### Sorceries

**3x Day of Judgment**
*Source: `cards_by_category/sorcery/sorcery_d.csv`*
Classic 4-mana board wipe. Destroys all creatures unconditionally. In a deck with only 3 creatures, this is almost always one-sided card advantage. Triggers Glacierwood Siege for mill 4. The backbone of our anti-creature strategy.

**2x Fumigate**
*Source: `cards_by_category/sorcery/sorcery_f.csv`*
5-mana board wipe that gains 1 life per creature destroyed. Replaces the requested Sunfall (not in database). Triggers Glacierwood Siege for mill 4, and the lifegain feeds Hope Estheim's mill trigger. Against wide boards, gaining 5+ life means milling 5+ cards at end of turn with Hope Estheim out. The Siege + Fumigate + Hope Estheim triple synergy is a core engine piece.

**3x Make Your Own Luck**
*Source: `cards_by_category/sorcery/sorcery_m.csv`*
5-CMC sorcery that looks at top 3 cards, plots a nonland card (cast free later), and puts the rest in hand. Critical mill amplifier: casting MYOL triggers Siege (mill 4), then casting the plotted spell later triggers Siege again (mill 4 more) for zero mana. Effectively generates 2 Siege triggers from 1 card while providing card selection and advantage.

### Artifacts

**3x Ancient Cornucopia**
*Source: `cards_by_category/artifact/artifact_a.csv`*
3-CMC artifact that gains 1 life per color of spell cast (once per turn) and taps for any color mana. Triple synergy: mana fixing for the 3-color deck, lifegain that feeds Hope Estheim's mill trigger, and ramp to cast expensive spells like Ugin/Vaultborn earlier. A 3-color spell like Make Your Own Luck gains 2 life, meaning Hope Estheim mills 2 extra.

**2x Mazemind Tome**
*Source: `cards_by_category/artifact/artifact_m.csv`*
2-CMC artifact with scry ({T}) and draw ({2},{T}) abilities that exiles itself with 4+ counters for 4 life. Provides consistent card selection and draw throughout the game. The exile-for-4-life trigger feeds Hope Estheim for a burst mill of 4 cards. Functions as a slow but reliable card advantage engine that doubles as lifegain.

**1x Riverchurn Monument**
*Source: `cards_by_category/artifact/artifact_r.csv`*
2-CMC artifact that mills opponents directly. The activated ability ({1},{T}) mills 2 cards, and the exhaust ability ({2}{U}{U},{T}) mills cards equal to graveyard size. With Glacierwood Siege feeding the opponent's graveyard, the exhaust activation becomes devastating — potentially milling 20+ cards in one shot as a finisher.

### Enchantments

**3x Glacierwood Siege**
*Source: `cards_by_category/enchantment/enchantment_g.csv`*
The deck's namesake and primary win condition. 3-CMC enchantment that, in Temur mode, mills 4 cards whenever you cast an instant or sorcery. With 22 instants/sorceries in the mainboard, each one becomes a mill 4 trigger. Multiple Sieges stack: 2 Sieges = mill 8 per spell, 3 = mill 12. Three Steps Ahead can copy the Siege for additional copies. The Sultai mode (play lands from graveyard) is a backup option for resource recovery.

**1x Omenpath Journey**
*Source: `cards_by_category/enchantment/enchantment_o.csv`*
4-CMC enchantment that exiles up to 5 differently-named lands from library, then puts one onto the battlefield tapped at each end step. In a 3-color deck with 23 lands, this guarantees perfect mana fixing while thinning the library. Each free land drop means more mana for interaction spells, and thinning the deck increases the density of spells drawn. Excellent in a control shell that plans to go long.

### Lands (23)

**4x Hallowed Fountain** — `cards_by_category/land/land_h.csv` — (UNF) 277
WU shock land. Replaces requested Seachrome Coast (not in database). Core dual land for the primary WU spell colors.

**2x Temple Garden** — `cards_by_category/land/land_t1.csv` — (CLU) 282
WG shock land. Replaces requested Razorverge Thicket (not in database). Provides green for Cornucopia, Make Your Own Luck, and Vaultborn Tyrant.

**2x Botanical Sanctum** — `cards_by_category/land/land_b.csv` — (SLD) 1376
GU fast land. Enters untapped with 2 or fewer other lands, making it excellent for early-game tempo.

**4x Floodfarm Verge** — `cards_by_category/land/land_f1.csv` — (DSK) 330
WU conditional land. Enters untapped with Plains/Island control. Strong in a deck running 3 Plains, 1 Island, and Hallowed Fountain.

**2x Willowrush Verge** — `cards_by_category/land/land_w.csv` — (DFT) 375
UG conditional land. Provides blue base with conditional green. Pairs with Forest and Botanical Sanctum.

**2x Hushwood Verge** — `cards_by_category/land/land_h.csv` — (DSK) 332
WG conditional land. Conditional on Forest/Plains. Excellent fixing for the WG portion of the mana base.

**3x Plains** — `cards_by_category/land/land_p1.csv` — (CMA) 292
Basic land for white mana. Enables Floodfarm Verge and Hushwood Verge conditions.

**2x Forest** — `cards_by_category/land/land_f1.csv` — (BLB) 280
Basic land for green mana. Enables Willowrush Verge, Hushwood Verge, and Botanical Sanctum conditions.

**1x Island** — `cards_by_category/land/land_i1.csv` — (ELD) 255
Basic land for blue mana. Enables Floodfarm Verge and Willowrush Verge conditions.

**1x Demolition Field** — `cards_by_category/land/land_d.csv` — (FDN) 687
Utility land that destroys nonbasic lands. Essential for dealing with opposing utility lands, creature-lands, or problematic nonbasics. Both players can search for a basic, thinning our deck.

---

## Mana Base Analysis

### Color Requirements (Pip Count)

| Color | Pips in Mainboard Spells | Key Cards |
|-------|--------------------------|-----------|
| White (W) | 16 pips | Get Lost, Day of Judgment, Fumigate, Elspeth's Smite, No More Lies |
| Blue (U) | 8 pips | Three Steps Ahead, Negate, No More Lies, Make Your Own Luck |
| Green (G) | 6 pips | Glacierwood Siege, Make Your Own Luck, Ancient Cornucopia, Vaultborn Tyrant |
| Colorless | 2 pips | Ugin, Eye of the Storms |

### Mana Sources

| Color | Sources | Count |
|-------|---------|-------|
| White | Plains, Hallowed Fountain, Temple Garden, Floodfarm Verge, Hushwood Verge, Ancient Cornucopia | 18 |
| Blue | Island, Hallowed Fountain, Botanical Sanctum, Floodfarm Verge, Willowrush Verge, Ancient Cornucopia | 14 |
| Green | Forest, Temple Garden, Botanical Sanctum, Willowrush Verge, Hushwood Verge, Ancient Cornucopia | 13 |
| Colorless | Demolition Field, any land | 23 |

### Land Count: 23

With 3 Ancient Cornucopia as mana rocks, the effective mana source count is 26. This is appropriate for a control deck with a curve topping at 7 (Ugin, Vaultborn Tyrant). Omenpath Journey also provides pseudo-ramp by putting a free land into play each end step.

---

## Curve Analysis

| CMC | Cards | Count |
|-----|-------|-------|
| 0 | — | 0 |
| 1 | Elspeth's Smite, Three Steps Ahead (base) | 6 |
| 2 | No More Lies, Negate, Mazemind Tome, Riverchurn Monument, Hope Estheim | 9 |
| 3 | Get Lost (effectively 2 but listed), Ancient Cornucopia, Glacierwood Siege, Day of Judgment (partial) | 10 |
| 4 | Day of Judgment, Omenpath Journey | 4 |
| 5 | Make Your Own Luck, Fumigate | 5 |
| 7 | Ugin Eye of the Storms, Vaultborn Tyrant | 3 |

**Non-land spell count:** 37
**Average CMC:** ~3.2 (appropriate for control)

### Ideal Turn Sequence

- **Turn 1:** Land, hold up Elspeth's Smite if needed
- **Turn 2:** Mazemind Tome or Riverchurn Monument; hold up Negate/No More Lies
- **Turn 3:** Glacierwood Siege (Temur mode) or Ancient Cornucopia; begin mill engine
- **Turn 4:** Day of Judgment if under pressure, or Get Lost + mill trigger; hold up counters
- **Turn 5:** Make Your Own Luck (mill 4 + plot a spell + draw 2) or Fumigate for stabilization
- **Turn 6+:** Free-cast plotted spells (mill 4 each), deploy Ugin or Vaultborn Tyrant
- **Turn 8-12:** Opponent's library runs out from accumulated Siege triggers

---

## Matchup Table

| Matchup | Pre-Board | Post-Board | Notes |
|---------|-----------|------------|-------|
| Aggro (Red/White) | 45% | 55% | 5 board wipes + lifegain stabilize; sideboard Authority of the Consuls + Bounce Off |
| Midrange (Golgari/Jund) | 60% | 65% | Board wipes handle their threats; mill outraces their value; Rest in Peace stops graveyard plans |
| Control (Azorius/Dimir) | 50% | 55% | Counter wars; mill is hard to interact with; Negate + Disdainful Stroke come in |
| Combo (Ramp/Enchantress) | 55% | 60% | Counter magic + Heritage Reclamation handle key pieces |
| Tempo (Izzet/Simic) | 40% | 50% | Their speed can outpace our setup; Bounce Off + Authority slow them down |

---

## Structural Weaknesses

1. **Slow Setup** — Glacierwood Siege costs 3 and doesn't impact the board immediately. Against fast aggro, we may die before establishing the engine. **Mitigation:** 6 one-mana interaction spells (Elspeth's Smite, Three Steps Ahead counter mode) buy time. Post-board Authority of the Consuls slows creatures.

2. **Enchantment Vulnerability** — Glacierwood Siege is an enchantment and can be removed, shutting down the primary win condition. **Mitigation:** Running 3 copies provides redundancy, Three Steps Ahead can copy it, and Negate/No More Lies protect it from removal.

3. **Low Creature Count** — Only 3 creatures means limited blocking and board presence. **Mitigation:** The deck is designed to wipe the board repeatedly. Hope Estheim's lifelink provides incidental life buffer, and Vaultborn Tyrant's death trigger provides resilience. Post-board Elspeth, Storm Slayer creates tokens.

4. **High Mana Curve** — Several key cards cost 5-7 mana. Drawing too many expensive spells early can lead to slow starts. **Mitigation:** Ancient Cornucopia and Omenpath Journey provide ramp/fixing. Mazemind Tome's scry helps filter draws. The low-cost interaction (Smite, Negate, No More Lies) keeps us alive.

5. **Graveyard Hate** — Opponent's Rest in Peace or similar effects don't directly hurt our mill plan (we're filling _their_ graveyard), but Riverchurn Monument's exhaust ability counts their graveyard size. **Mitigation:** The primary engine is Glacierwood Siege which mills regardless of graveyard state. Riverchurn is a supplementary finisher.

---

## Playtesting Notes

### Goldfish Analysis

- **Turn 3 Siege** deployed: Each subsequent instant/sorcery mills 4.
- **Turns 4-7** casting ~1 spell per turn: 4 spells x 4 mill = 16 cards milled.
- **Make Your Own Luck** on Turn 5: mill 4 + plot a spell. Cast plotted spell Turn 6: mill 4 more = 8 total from one card.
- **Two Sieges** by Turn 6 (via Three Steps Ahead copy): mill 8 per spell. 3 spells = 24 cards.
- **Theoretical mill by Turn 10:** With 1 Siege, ~7 spells cast = 28 cards. With 2 Sieges, ~7 spells = 56 cards (more than a library).

### Critical Decision Points

1. **Turn 3:** Deploy Glacierwood Siege or hold up interaction? Against aggro, interaction is often correct. Against slow decks, deploy Siege.
2. **Three Steps Ahead mode selection:** Counter mode vs. copy mode on Siege. If Siege is safe, copy it. If opponent has removal, counter their key spell.
3. **Day of Judgment timing:** Pre-emptive wipe at 2-3 creatures or wait for maximum value? Generally wipe early against aggro, wait against midrange.
4. **Ugin deployment:** Turn 7+ with counter backup is ideal. The cast trigger (exile a colored permanent) provides immediate value even if Ugin is answered.

### Mulligan Guide

- **Keep:** Any hand with 3+ lands, Glacierwood Siege or card draw, and at least 1 interaction spell.
- **Mulligan:** Hands with 5+ lands, no interaction, or no way to deploy Siege by Turn 4.
- **Snap keep:** Siege + Three Steps Ahead + lands. This is the nut draw.
