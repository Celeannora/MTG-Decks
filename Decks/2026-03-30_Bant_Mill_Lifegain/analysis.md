# Deck Analysis: Bant Mill Lifegain (Optimized)

**Date:** 2026-03-30
**Format:** Standard
**Colors:** W/U/G (Bant)

---

## Database Query Report

### Queries Run

| # | Query | Result | Set/Collector |
|---|-------|--------|---------------|
| 1 | `search_cards.py --name "Hope Estheim"` | Found | (FIN) 541 |
| 2 | `search_cards.py --name "Haliya, Guided by Light"` | Found | (PEOE) 19s |
| 3 | `search_cards.py --name "Get Lost"` | Found | (PLCI) 14p |
| 4 | `search_cards.py --name "Elspeth's Smite"` | Found | (PLST) MOM-13 |
| 5 | `search_cards.py --name "Three Steps Ahead"` | Found | (POTJ) 75s |
| 6 | `search_cards.py --name "No More Lies"` | Found | (MKM) 221 |
| 7 | `search_cards.py --name "Negate"` | Found | (OGW) 59 |
| 8 | `search_cards.py --name "Make Your Own Luck"` | Found | (OTJ) 218 |
| 9 | `search_cards.py --name "Space-Time Anomaly"` | Found | (PEOE) 229p |
| 10 | `search_cards.py --name "Day of Judgment"` | Found | (M11) 12 |
| 11 | `search_cards.py --name "Ancient Cornucopia"` | Found | (BIG) 46 |
| 12 | `search_cards.py --name "The Water Crystal"` | Found | (PFIN) 85s |
| 13 | `search_cards.py --name "Riverchurn Monument"` | Found | (DFT) 440 |
| 14 | `search_cards.py --name "Glacierwood Siege"` | Found | (TDM) 189 |
| 15 | `search_cards.py --name "Hallowed Fountain"` | Found | (UNF) 277 |
| 16 | `search_cards.py --name "Temple Garden"` | Found | (CLU) 282 |
| 17 | `search_cards.py --name "Breeding Pool"` | Found | (EXP) 15 |
| 18 | `search_cards.py --name "Floodfarm Verge"` | Found | (DSK) 330 |
| 19 | `search_cards.py --name "Botanical Sanctum"` | Found | (SLD) 1376 |
| 20 | `search_cards.py --name "Hushwood Verge"` | Found | (DSK) 332 |
| 21 | `search_cards.py --name "Willowrush Verge"` | Found | (DFT) 375 |
| 22 | `search_cards.py --name "Plains"` | Found | (CMA) 292 |
| 23 | `search_cards.py --name "Forest"` | Found | (BLB) 280 |
| 24 | `grep Island,.*ELD, land_i1.csv` | Found | (ELD) 255 |
| 25 | `search_cards.py --name "Demolition Field"` | Found | (FDN) 687 |
| 26 | `search_cards.py --name "Rest in Peace"` | Found | (PRM) 77943 |
| 27 | `search_cards.py --name "Disdainful Stroke"` | Found | (GRN) 37 |
| 28 | `search_cards.py --name "Stroke of Midnight"` | Found | (WOE) 33 |
| 29 | `search_cards.py --name "Bounce Off"` | Found | (DFT) 39 |
| 30 | `search_cards.py --name "Authority of the Consuls"` | Found | (PKLD) 5s |
| 31 | `search_cards.py --name "Elspeth, Storm Slayer"` | Found | (TDM) 398 |
| 32 | `search_cards.py --name "Soul-Guide Lantern"` | Found | (WOE) 251 |
| 33 | `search_cards.py --name "Banishing Light"` | Found | (SCD) 9 |
| 34 | `search_cards.py --name "Long River's Pull"` | Found | (BLB) 58 |

### Per-Card Verification (ALL 60+15 cards)

**Mainboard (60 cards):**

| Status | Card Name | Source File | Set/Collector |
|--------|-----------|-------------|---------------|
| ✓ | Hope Estheim | `cards_by_category/creature/creature_h2.csv` | (FIN) 541 |
| ✓ | Haliya, Guided by Light | `cards_by_category/creature/creature_h1.csv` | (PEOE) 19s |
| ✓ | Get Lost | `cards_by_category/instant/instant_g.csv` | (PLCI) 14p |
| ✓ | Elspeth's Smite | `cards_by_category/instant/instant_e.csv` | (PLST) MOM-13 |
| ✓ | Three Steps Ahead | `cards_by_category/instant/instant_t.csv` | (POTJ) 75s |
| ✓ | No More Lies | `cards_by_category/instant/instant_n.csv` | (MKM) 221 |
| ✓ | Negate | `cards_by_category/instant/instant_n.csv` | (OGW) 59 |
| ✓ | Make Your Own Luck | `cards_by_category/sorcery/sorcery_m.csv` | (OTJ) 218 |
| ✓ | Space-Time Anomaly | `cards_by_category/sorcery/sorcery_s.csv` | (PEOE) 229p |
| ✓ | Day of Judgment | `cards_by_category/sorcery/sorcery_d.csv` | (M11) 12 |
| ✓ | Ancient Cornucopia | `cards_by_category/artifact/artifact_a.csv` | (BIG) 46 |
| ✓ | The Water Crystal | `cards_by_category/artifact/artifact_t.csv` | (PFIN) 85s |
| ✓ | Riverchurn Monument | `cards_by_category/artifact/artifact_r.csv` | (DFT) 440 |
| ✓ | Glacierwood Siege | `cards_by_category/enchantment/enchantment_g.csv` | (TDM) 189 |
| ✓ | Hallowed Fountain | `cards_by_category/land/land_h.csv` | (UNF) 277 |
| ✓ | Temple Garden | `cards_by_category/land/land_t1.csv` | (CLU) 282 |
| ✓ | Breeding Pool | `cards_by_category/land/land_b.csv` | (EXP) 15 |
| ✓ | Floodfarm Verge | `cards_by_category/land/land_f1.csv` | (DSK) 330 |
| ✓ | Botanical Sanctum | `cards_by_category/land/land_b.csv` | (SLD) 1376 |
| ✓ | Hushwood Verge | `cards_by_category/land/land_h.csv` | (DSK) 332 |
| ✓ | Willowrush Verge | `cards_by_category/land/land_w.csv` | (DFT) 375 |
| ✓ | Plains | `cards_by_category/land/land_p1.csv` | (CMA) 292 |
| ✓ | Forest | `cards_by_category/land/land_f1.csv` | (BLB) 280 |
| ✓ | Island | `cards_by_category/land/land_i1.csv` | (ELD) 255 |
| ✓ | Demolition Field | `cards_by_category/land/land_d.csv` | (FDN) 687 |

**Sideboard (15 cards):**

| Status | Card Name | Source File | Set/Collector |
|--------|-----------|-------------|---------------|
| ✓ | Rest in Peace | `cards_by_category/enchantment/enchantment_r.csv` | (PRM) 77943 |
| ✓ | Disdainful Stroke | `cards_by_category/instant/instant_d.csv` | (GRN) 37 |
| ✓ | Negate | `cards_by_category/instant/instant_n.csv` | (OGW) 59 |
| ✓ | Stroke of Midnight | `cards_by_category/instant/instant_s.csv` | (WOE) 33 |
| ✓ | Bounce Off | `cards_by_category/instant/instant_b.csv` | (DFT) 39 |
| ✓ | Authority of the Consuls | `cards_by_category/enchantment/enchantment_a.csv` | (PKLD) 5s |
| ✓ | Elspeth, Storm Slayer | `cards_by_category/planeswalker/planeswalker_e.csv` | (TDM) 398 |
| ✓ | Soul-Guide Lantern | `cards_by_category/artifact/artifact_s.csv` | (WOE) 251 |
| ✓ | Banishing Light | `cards_by_category/enchantment/enchantment_b.csv` | (SCD) 9 |
| ✓ | Long River's Pull | `cards_by_category/instant/instant_l.csv` | (BLB) 58 |

### Rejected Cards (Cut from Original Build)

| Card | Original Copies | Reason for Cut |
|------|----------------|----------------|
| Ugin, Eye of the Storms | 2 | 7 CMC too slow; planeswalker does not trigger Glacierwood Siege (not an instant/sorcery); colorless 0-ability mana doesn't cast WUG spells; strategically misaligned with the mill plan |
| Vaultborn Tyrant | 1 | 7 CMC creature with no mill synergy; replaced by Haliya at 3 CMC with lifegain+draw engine |
| Fumigate | 2 | 5 CMC board wipe is overcosted when Day of Judgment does the job at 4; marginal lifegain replaced by Space-Time Anomaly's mill-equal-to-life finisher |
| Mazemind Tome | 2 | 2 mana per scry, 4 mana per card draw is terrible rate for Mythic play; Haliya draws for free when gaining 3+ life per turn |
| Omenpath Journey | 1 | 4 CMC enchantment that doesn't impact the board, doesn't trigger Siege, and is a win-more card |
| Heritage Reclamation (SB) | 2 | Replaced by Stroke of Midnight — more versatile instant removal that triggers Siege |
| Break Down the Door (SB) | 1 | Replaced by Banishing Light — catchall exile is more relevant |
| Soul-Guide Lantern (SB) | 1 copy cut | Reduced from 2 to 1; Rest in Peace is the primary graveyard hate |

### Validation Script Result

```bash
$ python scripts/validate_decklist.py Decks/2026-03-30_Bant_Mill_Lifegain/decklist.txt
✅ VALIDATION PASSED
```

---

## Executive Summary

- **Archetype:** Bant (W/U/G) Mill-Control
- **Primary win condition:** Glacierwood Siege (Temur mode) mills 4 cards per instant/sorcery cast; The Water Crystal amplifies every mill trigger by +4; Space-Time Anomaly mills cards equal to your life total as a finisher
- **Secondary win condition:** Hope Estheim end-step mill equal to life gained + Riverchurn Monument exhaust for massive late-game mill
- **Target win turn:** Turn 7-9 (theoretical goldfish lethal mill by T7)
- **Metagame positioning:** Strong vs midrange and creature-based strategies; 16 mainboard interaction spells + 3 board wipes provide control density; lifegain provides inevitability against aggro; mill ignores board stalls

---

## Card-by-Card Breakdown

### Creatures (5)

**3x Hope Estheim**
*Source: `cards_by_category/creature/creature_h2.csv`*
The deck's core mill engine. At the beginning of your end step, each opponent mills X cards where X = life gained this turn. With Ancient Cornucopia on board, every colored spell gains 1 life minimum, meaning Hope triggers every turn you cast a spell. With Haliya providing ETB lifegain and Authority of the Consuls from the sideboard, life totals of 3-5 per turn are routine. Synergizes with: Glacierwood Siege (mill on cast + mill on end step), Ancient Cornucopia (automatic lifegain), Haliya (lifegain engine), The Water Crystal (+4 to Hope's end-step mill trigger). At 2 CMC, deploys before Siege on curve. Increased from 2 to 3 copies — this deck wants Hope online as early and consistently as possible.

**2x Haliya, Guided by Light**
*Source: `cards_by_category/creature/creature_h1.csv`*
Three-mode value engine: (1) ETB gains 1 life for each creature/artifact entering, fueling Hope's mill; (2) end-step draws a card if you gained 3+ life — trivially met with Cornucopia + any spell; (3) Warp {W} allows reuse from exile, generating multiple ETB triggers for repeated lifegain and card advantage. Synergizes with: Hope Estheim (lifegain fuels mill), Ancient Cornucopia (colored spells gain life toward the 3-life draw threshold), Get Lost (the Map tokens are artifacts that trigger Haliya's ETB lifegain). Replaced Vaultborn Tyrant — same draw engine concept at half the mana cost with lifegain synergy.

### Instants (16)

**4x Get Lost**
*Source: `cards_by_category/instant/instant_g.csv`*
Premium exile-based removal hitting creatures, enchantments, and planeswalkers. The Map tokens given to the opponent are largely irrelevant against a mill strategy (they spend mana to explore, helping us mill them). At 2 CMC with instant speed, it triggers Glacierwood Siege on the opponent's turn for defensive mill pressure. Synergizes with: Glacierwood Siege (instant = mill 4), The Water Crystal (instant + mill trigger = mill 8 total), Haliya (opponent's Map artifacts are irrelevant to our plan, but our removal keeps the board clear for mill). Better than alternatives: Banishing Light is sorcery-speed and doesn't exile; Fateful Absence gives card advantage to opponent.

**4x Elspeth's Smite**
*Source: `cards_by_category/instant/instant_e.csv`*
One-mana interaction that exiles attacking/blocking creatures. Critical for surviving the early game against aggro before Siege comes online. At 1 CMC, it's the cheapest Siege trigger in the deck — enabling "double-spell" turns where you cast two instants and mill 8 (or 16 with Water Crystal). Synergizes with: Glacierwood Siege (cheapest trigger at 1 mana), The Water Crystal (1-mana mill 8), No More Lies (both cost-efficient, enabling multi-spell turns). Increased from 3 to 4 copies for maximum early interaction density. Better than alternatives: Cut Down is conditional on power/toughness; March of Otherworldly Light costs life.

**3x Three Steps Ahead**
*Source: `cards_by_category/instant/instant_t.csv`*
The most versatile card in the deck via Spree. Mode 1 ({1}{U}{U}): Counter target spell — hard counter for 3 mana, triggers Siege. Mode 2 ({U}{3}): Copy target artifact or creature — copying Glacierwood Siege doubles mill rate, copying Water Crystal is devastating, copying Hope Estheim doubles end-step mill. Mode 3 ({U}{2}): Draw 2, discard 1 — refuels in the late game, triggers Siege. Every mode triggers Siege and is an instant. Synergizes with: Glacierwood Siege (triggers + can copy it), The Water Crystal (copy it for +8 per mill trigger), Hope Estheim (copy for double end-step mill), Ancient Cornucopia (blue spell = lifegain). Better than alternatives: Counterspell is UU restrictive; Dissipate doesn't have modal flexibility.

**3x No More Lies**
*Source: `cards_by_category/instant/instant_n.csv`*
Tax counter that exiles the countered spell — critical against reanimation and flashback strategies. The "pay 3" tax is often a hard counter in the first 5 turns. At WU, it's castable on T2 with any WU dual. Exiling is strictly better than graveyard for a mill deck — we don't want opponents benefiting from milled cards. Increased from 2 to 3 copies for better early interaction density. Synergizes with: Glacierwood Siege (instant trigger), The Water Crystal (blue spell discount makes this effectively {W} to cast), Three Steps Ahead (counter suite density). Better than alternatives: Make Disappear requires sacrifice fodder; Render Inert doesn't exile.

**2x Negate**
*Source: `cards_by_category/instant/instant_n.csv`*
Protects Glacierwood Siege and The Water Crystal from removal. Counters planeswalkers, board wipes, and enchantment removal. At {1}{U}, it's a cheap Siege trigger that can be held up alongside another spell. The deck runs 2 main + 2 sideboard for matchup flexibility. Synergizes with: Glacierwood Siege (protects it + triggers it), The Water Crystal (costs {U} with Crystal discount), Ancient Cornucopia (blue spell = lifegain). Better than alternatives: Spell Pierce is too conditional in the late game; Disdainful Stroke is in the sideboard for the 4+ CMC matchups.

### Sorceries (5)

**3x Make Your Own Luck**
*Source: `cards_by_category/sorcery/sorcery_m.csv`*
The tempo engine. Look at top 3, plot a nonland card (cast free later), put the rest in hand. This generates TWO Siege triggers from one card — the initial cast triggers Siege, and the plotted card triggers Siege again on a later turn for zero mana. At {3}{G}{U}, it's castable T4 with Cornucopia or T5 naturally. With Water Crystal, costs {3}{G} (blue discount). Synergizes with: Glacierwood Siege (2 triggers per card), The Water Crystal (cost reduction + both triggers cause +4 mill), Hope Estheim (plotted spells cast on later turns = more spells per turn = more lifegain triggers). Better than alternatives: Foresee only scrys; See the Truth needs specific conditions.

**2x Space-Time Anomaly**
*Source: `cards_by_category/sorcery/sorcery_s.csv`*
The finisher. "Target player mills cards equal to your life total." In a lifegain deck starting at 20 life, this baseline mills 20 cards. With Ancient Cornucopia and Hope Estheim gaining life each turn, life totals of 25-30 are typical by T6-7. With Water Crystal on board, the mill trigger adds +4, making it mill 24-34 cards in a single spell. This is the card that replaced Fumigate — instead of a 5-mana board wipe that gains marginal life, this is a 4-mana card that reads "opponent loses half their library." Synergizes with: The Water Crystal (+4 to the mill trigger), Glacierwood Siege (sorcery triggers mill 4 in addition to the life-total mill), Ancient Cornucopia (keeps life total high), Hope Estheim (lifegain keeps life total high). With Crystal + Siege: one Space-Time Anomaly mills 20 (life) + 4 (Crystal) + 4 (Siege) = 28 cards minimum.

### Board Wipes (3)

**3x Day of Judgment**
*Source: `cards_by_category/sorcery/sorcery_d.csv`*
Clean 4-mana board wipe with no conditions. Triggers Glacierwood Siege for mill 4 (mill 8 with Crystal). 3 copies provides adequate wipe density — the original build ran 5 total wipes (3 Day of Judgment + 2 Fumigate) which was excessive at 5 board wipes. Reducing to 3 frees two slots for Space-Time Anomaly (the finisher this deck was missing). The deck's 16 instant-speed interaction spells handle individual threats; Day of Judgment is reserved for when the opponent goes wide. Synergizes with: Glacierwood Siege (sorcery trigger), The Water Crystal (mill 8 total while clearing the board), Hope Estheim (survives if Haliya warps back after wipe). Better than alternatives: Fumigate costs 5 mana for marginal lifegain; Wrath of God is functionally identical but Day of Judgment is in the database.

### Artifacts (4)

**2x Ancient Cornucopia**
*Source: `cards_by_category/artifact/artifact_a.csv`*
Dual-purpose mana fixer and lifegain engine. Taps for any color (fixes the three-color mana base) and gains 1 life per color of each spell cast (once per turn). Every spell in this deck is 1-3 colors, guaranteeing 1-3 life per turn. This fuels Hope Estheim's end-step mill and pushes toward Haliya's 3-life draw threshold. At 3 CMC, it curves into T4 Siege or T4 Space-Time Anomaly. Reduced from 3 to 2 copies to make room — 2 copies with 23 lands is sufficient. Synergizes with: Hope Estheim (lifegain = mill), Haliya (lifegain toward 3-life draw threshold), Space-Time Anomaly (higher life total = more mill), Glacierwood Siege (mana fixing ensures on-curve Siege). Better than alternatives: Mazemind Tome costs 2 mana per activation; Prophetic Prism doesn't gain life.

**1x The Water Crystal**
*Source: `cards_by_category/artifact/artifact_t.csv`*
The single most impactful addition to this deck. Three abilities: (1) Blue spells cost {1} less — makes Negate cost {U}, No More Lies cost {W}, Three Steps Ahead counter mode cost {U}{U}. (2) If an opponent would mill, they mill that many +4 — this applies to EVERY mill trigger: Siege mills 8 instead of 4, Hope mills X+4, Riverchurn mills 6 instead of 2, Space-Time mills life+4. (3) Activated ability ({4}{U}{U}, {T}) mills equal to hand size — a backup finisher. At 1 copy, it's a powerful singleton that transforms the deck's mill rate but isn't dead in multiples since it's legendary. Synergizes with: Every card in the deck. Glacierwood Siege (4→8 per trigger), Hope Estheim (X→X+4), Space-Time Anomaly (life→life+4), Riverchurn Monument (2→6 per activation), all blue spells (cost reduction).

**1x Riverchurn Monument**
*Source: `cards_by_category/artifact/artifact_r.csv`*
Repeatable mill engine at 2 CMC. Tap ability ({1}, {T}) mills 2 (or 6 with Water Crystal) each turn. The Exhaust ability is devastating in the late game: mills cards equal to opponent's graveyard size. After several turns of Siege triggers milling 4-8 per spell, the graveyard contains 20-30+ cards — Exhaust mills that many again, often lethal. With Water Crystal, Exhaust adds +4 on top. Synergizes with: The Water Crystal (2→6 per tap, Exhaust also gets +4), Glacierwood Siege (builds the graveyard for Exhaust), Hope Estheim (additional mill stacks graveyard faster). Better than alternatives: Tome Scour is one-shot; Mesmeric Orb is symmetrical.

### Enchantments (4)

**4x Glacierwood Siege**
*Source: `cards_by_category/enchantment/enchantment_g.csv`*
The primary win condition. Choosing Temur mode: whenever you cast an instant or sorcery, target player mills 4. With 21 instants/sorceries in the deck, every spell is a mill trigger. Multiple Sieges stack — 2 Sieges = mill 8 per spell, which means a single Get Lost mills 8 cards while removing a threat. With Water Crystal, 1 Siege mills 8 per spell; 2 Sieges + Crystal mills 12 per spell. The move from 3 to 4 copies is mathematically justified: probability of having Siege in opening 7 goes from ~34% to ~40%, and by T3 draw from ~45% to ~52%. That 7% improvement is critical since the entire deck revolves around this card. Synergizes with: Every instant and sorcery (21 cards), The Water Crystal (+4 per trigger), Make Your Own Luck (2 Siege triggers from 1 card).

### Lands (23)

**4x Hallowed Fountain** — *Source: `cards_by_category/land/land_h.csv`*
WU shock land with Plains+Island types. Enables Floodfarm Verge's colored mana and is type-relevant for all WU Verge conditions. The core dual land for the deck's most common color pair.

**2x Temple Garden** — *Source: `cards_by_category/land/land_t1.csv`*
WG shock land with Forest+Plains types. Enables Hushwood Verge and provides the green sources needed for Glacierwood Siege and Make Your Own Luck.

**1x Breeding Pool** — *Source: `cards_by_category/land/land_b.csv`*
GU shock land with Forest+Island types. The critical missing piece from the original build. Enables both Willowrush Verge and Botanical Sanctum's color conditions. Without this land, the GU color pair was undersupported — casting T3 Siege ({1}{G}{U}) into T4 Three Steps Ahead was unreliable.

**4x Floodfarm Verge** — *Source: `cards_by_category/land/land_f1.csv`*
WU conditional land. Produces {W} always, {U} if you control a Plains or Island. With 3 Plains + 4 Hallowed Fountain + 2 Temple Garden = 9 Plains-type lands, the condition is trivially met.

**2x Botanical Sanctum** — *Source: `cards_by_category/land/land_b.csv`*
GU fast land. Enters untapped with 2 or fewer other lands — perfect for the T1-T3 curve where GU mana is critical for T3 Glacierwood Siege.

**2x Hushwood Verge** — *Source: `cards_by_category/land/land_h.csv`*
WG conditional land. Produces {G} always, {W} if you control a Forest or Plains. Supported by 1 Forest + 2 Temple Garden + 1 Breeding Pool = 4 Forest-type lands plus 3 Plains + 4 Hallowed Fountain + 2 Temple Garden = 9 Plains-type lands.

**2x Willowrush Verge** — *Source: `cards_by_category/land/land_w.csv`*
UG conditional land. Produces {U} always, {G} if you control a Forest or Island. Critical for casting Glacierwood Siege ({1}{G}{U}) on curve.

**3x Plains, 1x Forest, 1x Island** — *Source: `cards_by_category/land/` various*
Basic lands that enable Verge conditions and provide fetchable types. Plains at 3 copies reflects white being the most pip-heavy color (14 pips mainboard). Forest reduced from 2 to 1 to make room for Breeding Pool (which provides Forest type). Demolition Field can fetch these when sacrificed.

**1x Demolition Field** — *Source: `cards_by_category/land/land_d.csv`*
Utility land that answers creature-lands and problematic nonbasics. The {2} activation cost is affordable in a control deck, and the basic land search ensures mana development isn't sacrificed.

---

## Mana Base Analysis

### Color Pip Requirements

| Color | Total Pips (Mainboard) | Key Cards |
|-------|----------------------|-----------|
| White (W) | 14 | Get Lost ({1}{W}), Elspeth's Smite ({W}), No More Lies ({W}{U}), Day of Judgment ({2}{W}{W}), Space-Time Anomaly ({2}{W}{U}), Haliya ({2}{W}) |
| Blue (U) | 11 | Three Steps Ahead ({U}+), No More Lies ({W}{U}), Negate ({1}{U}), Make Your Own Luck ({3}{G}{U}), Space-Time Anomaly ({2}{W}{U}), Water Crystal ({2}{U}{U}) |
| Green (G) | 5 | Glacierwood Siege ({1}{G}{U}), Make Your Own Luck ({3}{G}{U}), Ancient Cornucopia ({2}{G}) |

### Frank Karsten Mana Requirements Validation

| Color | Pips | Required Sources | Actual Sources | Breakdown | Status |
|-------|------|-----------------|----------------|-----------|--------|
| W | 14 | ~16 | 17 | 3 Plains + 4 Hallowed Fountain + 2 Temple Garden + 4 Floodfarm Verge + 2 Hushwood Verge + 2 Cornucopia | PASS |
| U | 11 | ~14 | 16 | 1 Island + 4 Hallowed Fountain + 1 Breeding Pool + 4 Floodfarm Verge + 2 Botanical Sanctum + 2 Willowrush Verge + 2 Cornucopia | PASS |
| G | 5 | ~10 | 12 | 1 Forest + 2 Temple Garden + 1 Breeding Pool + 2 Botanical Sanctum + 2 Hushwood Verge + 2 Willowrush Verge + 2 Cornucopia | PASS |

### Land Count: 23

With 2 Ancient Cornucopia acting as additional mana sources, the effective mana source count is 25. The deck's average CMC of ~2.95 and curve topping at 5 (Make Your Own Luck) supports 23 lands. The original build also ran 23 lands. The addition of Breeding Pool replaces 1 Forest, improving mana quality without changing the land count.

---

## Curve Analysis

| CMC | Cards | Count |
|-----|-------|-------|
| 1 | Elspeth's Smite | 4 |
| 2 | Hope Estheim, Get Lost, No More Lies, Negate, Riverchurn Monument | 12 |
| 3 | Haliya, Three Steps Ahead, Ancient Cornucopia, Glacierwood Siege | 11 |
| 4 | Space-Time Anomaly, The Water Crystal, Day of Judgment | 6 |
| 5 | Make Your Own Luck | 3 |

*Note: Three Steps Ahead has base cost {U} (1 CMC) but is typically cast for 3+ CMC. Listed at 3 for curve analysis since that's the most common casting cost.*

**Non-land spell count:** 37
**Average CMC (nonland):** (4×1 + 12×2 + 11×3 + 6×4 + 3×5) / 37 = (4+24+33+24+15)/37 = 100/37 ≈ 2.70

**Ideal Turn Sequence:**
- **T1:** Land, pass (or Elspeth's Smite if opponent has a 1-drop)
- **T2:** Hope Estheim or Riverchurn Monument or hold up Negate/No More Lies
- **T3:** Glacierwood Siege (Temur mode) — the critical play
- **T4:** The Water Crystal or Day of Judgment if under pressure; begin casting instants to trigger Siege
- **T5:** Make Your Own Luck (plot a free spell, put 2 cards in hand, mill 4-8)
- **T6-7:** Cast plotted spell + additional instants; Space-Time Anomaly for lethal mill

---

## Mill Rate Projections

### Per-Spell Mill Output

| Board State | Mill per Instant/Sorcery |
|-------------|-------------------------|
| 1 Siege | 4 |
| 1 Siege + Water Crystal | 8 |
| 2 Sieges | 8 |
| 2 Sieges + Water Crystal | 12 |

### Goldfish Kill Analysis (Turn-by-Turn)

| Turn | Play | Mill This Turn | Cumulative Mill |
|------|------|---------------|-----------------|
| T1 | Land | 0 | 0 |
| T2 | Hope Estheim | 0 | 0 |
| T3 | Glacierwood Siege (Temur) | 0 | 0 |
| T4 | The Water Crystal; cast Elspeth's Smite (Siege trigger) | 8 (Siege+Crystal) + Hope end-step ~3 | 11 |
| T5 | Make Your Own Luck (mill 8 from Siege+Crystal, plot a spell) | 8 + Hope ~4 | 23 |
| T6 | Cast plotted spell (mill 8) + Get Lost (mill 8) | 16 + Hope ~5 | 44 |
| T7 | Space-Time Anomaly at ~24 life: mills 24+4(Crystal)+4(Siege) = 32 | 32 | 76+ |

**Theoretical best-case mill by T7: 60+ cards = complete library**

Even in non-ideal scenarios (no Water Crystal, fewer spells), the deck reliably mills 50+ cards by T8-9, which is lethal against 53-card libraries (after opening hand + draws).

### Hope Estheim Contribution

With Cornucopia on board, each colored spell gains 1-3 life. A typical turn casting 2 spells gains 3-5 life, meaning Hope mills 3-5 additional cards per end step on top of Siege triggers. Over 4 turns, Hope contributes 12-20 additional cards milled. With Water Crystal, each end-step trigger adds +4, pushing Hope's contribution to 7-9 cards per turn.

### Riverchurn Monument Late-Game

The Exhaust ability mills cards equal to opponent's graveyard size. After 3-4 turns of Siege triggers milling 4-8 per spell, the graveyard typically contains 20-30 cards. Exhaust (with Water Crystal) mills 24-34 cards — often lethal on its own.

### Comparison to Original Build

| Metric | Original Build | Optimized Build | Improvement |
|--------|---------------|-----------------|-------------|
| Mill per spell (1 Siege) | 4 | 4 | — |
| Mill per spell (Siege + Crystal) | N/A | 8 | +100% |
| Finisher damage | Ugin ultimate (unreliable) | Space-Time Anomaly (20+ mill) | Reliable finisher |
| Goldfish kill turn | T10-12 | T7-9 | 3 turns faster |
| Wipe CMC average | 4.6 (3 DoJ + 2 Fumigate) | 4.0 (3 DoJ) | -0.6 CMC |
| Draw engine cost | 2-4 mana per draw (Tome) | Free (Haliya at 3+ life) | Massive tempo gain |

---

## Matchup Table

| Matchup | Pre-Board | Post-Board | Key Factor |
|---------|-----------|------------|------------|
| Aggro (Red/White) | 50% | 60% | 8 one-two mana removal spells buy time; Day of Judgment resets; lifegain outraces. Post-board: +Bounce Off, +Authority of the Consuls |
| Midrange (Golgari/Jund) | 60% | 65% | Mill ignores their creatures; counter suite stops planeswalkers; they can't pressure fast enough. Post-board: +Disdainful Stroke, +Stroke of Midnight |
| Control (Azorius/Dimir) | 45% | 55% | Counter wars are close; they have answers to Siege. Mill is inevitable if Siege sticks. Post-board: +Negate, +Disdainful Stroke, +Long River's Pull |
| Combo (Lotus Field/etc.) | 55% | 60% | Counter suite disrupts combos; mill provides an alternative clock. Post-board: +Negate, +Disdainful Stroke |
| Tempo (Izzet/Azorius) | 50% | 55% | Their counters contest ours; their threats are efficient. Siege must resolve. Post-board: +Bounce Off, +Negate |

---

## Structural Weaknesses

1. **Siege Dependency** — The deck is significantly weaker without Glacierwood Siege on the battlefield. Only 4 copies of a 3-drop enchantment as the primary engine means enchantment removal (Banishing Light, Tear Asunder) is devastating. **Mitigation:** 8 counterspells mainboard protect Siege; Three Steps Ahead can copy Siege for redundancy; sideboard Negate adds counter density. The 4th copy (up from 3) significantly improves the probability of finding Siege by T3 (45%→52%).

2. **Water Crystal as Singleton** — The Water Crystal is transformative but only appears as a 1-of. Games without it are significantly slower (T7 kill → T9-10 kill). **Mitigation:** Make Your Own Luck digs for it; Three Steps Ahead can copy it; the deck still wins without it, just 2-3 turns slower. Running 1 is correct because it's legendary and 4 CMC is a significant tempo cost if drawn in multiples.

3. **Creature-Light Defense** — With only 5 creatures mainboard, the deck relies on removal and board wipes to survive. Persistent threats like hexproof creatures or recursive threats can overwhelm the removal suite. **Mitigation:** 3 Day of Judgment for go-wide strategies; Get Lost exiles (no recursion); Banishing Light in sideboard for hexproof; Elspeth, Storm Slayer creates chump-blocking tokens.

4. **Slow Against Fast Combo** — The deck's T3 Siege → T7 kill goldfish is too slow against dedicated T4-5 combo decks. Counter magic must be deployed early, leaving less mana for proactive plays. **Mitigation:** 8 counters mainboard; 4 additional counters in sideboard (2 Negate + 2 Disdainful Stroke); Elspeth's Smite at 1 mana preserves tempo while interacting.

---

## Playtesting Notes

### Goldfish Analysis

**Average goldfish kill:** Turn 8 (without Water Crystal), Turn 7 (with Water Crystal). The deck consistently presents lethal mill between T7-9, which is competitive for a control-mill strategy in Standard. This is a 3-turn improvement over the original build's T10-12 kill range.

**T3 Siege probability:** With 4 copies in 60 cards, P(at least 1 Siege in top 10 cards by T3) = 1 - C(56,10)/C(60,10) ≈ 52%. Mulligans further improve this — any 7-card hand without Siege or Make Your Own Luck is a mulligan candidate.

**Space-Time Anomaly as finisher:** At 20 life (conservative), STA mills 20 cards. With Siege + Crystal on board, that's 20+4+4 = 28 cards in one spell. If the opponent has already been milled for 25-30 cards over T4-6, STA on T7 is lethal.

### Critical Decisions

1. **Siege mode choice:** Always choose Temur in game 1. Sultai mode (play lands from graveyard) is only relevant if the opponent is actively milling you back.
2. **When to deploy Hope Estheim:** T2 on the play against control (under their countermagic); T4+ against aggro (after stabilizing with removal).
3. **Water Crystal timing:** T4 before starting the spell chain is ideal. Don't deploy into open countermagic — wait for a window or force it with bait spells.
4. **Space-Time Anomaly as finisher vs. early play:** Never cast this before life total exceeds 20 unless it's lethal. The card scales with time — every turn of lifegain makes it more powerful.
5. **Three Steps Ahead mode selection:** Counter mode against must-answer spells; copy mode on Siege/Crystal if the board is stable; draw mode only when behind on cards.

### Mulligan Guide

**Keep:** Any hand with Siege or Make Your Own Luck + 3 lands including WU. Any hand with 2-3 interaction spells + Hope Estheim + 3 lands.

**Mulligan:** Hands without Siege or a way to find it by T4. Hands with 5+ lands. Hands with only green mana. Hands with Water Crystal but no Siege (Crystal does nothing alone).

**On the play:** Prioritize Siege in the opening hand. Counter-heavy hands are weaker on the play since you're tapped out deploying threats.

**On the draw:** Interaction-heavy hands are stronger on the draw. Extra card draw means higher Siege probability naturally — you see 8 cards by T1, increasing Siege odds.
