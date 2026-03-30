# Jeskai Angels Aggro — Deck Analysis
**Date:** 2026-03-30
**Format:** MTG Arena Standard
**Archetype:** Jeskai (WUR) — Aggro Lifegain +1/+1 Counters
**Target Kill Turn:** 4-5

---

## Database Query Report

### Queries Run

| Query | Results |
|-------|---------|
| `search_cards.py --type creature --colors WUR --tags lifegain --cmc-max 1` | 13 candidates |
| `search_cards.py --type creature --colors WUR --tags lifegain --cmc-max 2` | 39 candidates |
| `search_cards.py --type creature --colors WUR --name "Angel" --cmc-max 4` | 8 candidates |
| `search_cards.py --type creature --colors WUR --oracle "+1/+1 counter" --cmc-max 4` | 149 candidates |
| `search_cards.py --type creature --colors WUR --keywords "Lifelink" --cmc-max 3` | 30 candidates |
| `search_cards.py --type creature --colors WUR --tags lifegain --cmc-max 3 --oracle "whenever"` | — |
| `search_cards.py --name "Warleader's Call"` | 1 candidate |
| `search_cards.py --name "Voice of Victory"` | 1 candidate |
| `search_cards.py --name "Anim Pakal"` | 1 candidate |
| `search_cards.py --name "Enduring Innocence"` | 1 candidate |
| `search_cards.py --name "Delney"` | 1 candidate |
| `search_cards.py --name "Arabella"` | 1 candidate |
| `search_cards.py --type land --colors WUR` | 120+ candidates |
| `search_cards.py --type instant --colors WUR --tags removal --cmc-max 3` | 33 candidates |
| `search_cards.py --type instant --colors WU --tags counter --cmc-max 3` | 24 candidates |

### Per-Card Verification (ALL 60+15 cards)

#### Mainboard Creatures (30)
✓ **Hinterland Sanctifier** ×4 — `creature/creature_h2.csv` — (FDN) #730
✓ **Healer's Hawk** ×4 — `creature/creature_h1.csv` — (GRN) #14
✓ **Ajani's Pridemate** ×4 — `creature/creature_a1.csv` — (CLU) #52
✓ **Essence Channeler** ×4 — `creature/creature_e.csv` — (PBLB) #12s
✓ **Voice of Victory** ×4 — `creature/creature_v.csv` — (PTDM) #33s
✓ **Arabella, Abandoned Doll** ×2 — `creature/creature_a2.csv` — (DSK) #208
✓ **Anim Pakal, Thousandth Moon** ×2 — `creature/creature_a2.csv` — (PLCI) #223s
✓ **Dazzling Angel** ×2 — `creature/creature_d1.csv` — (FDN) #9
✓ **Angel of Vitality** ×2 — `creature/creature_a2.csv` — (CLU) #53
✓ **Delney, Streetwise Lookout** ×1 — `creature/creature_d1.csv` — (MKM) #378
✓ **Resplendent Angel** ×1 — `creature/creature_r2.csv` — (PLCI) #32p

#### Mainboard Noncreatures (8)
✓ **Warleader's Call** ×3 — `enchantment/enchantment_w.csv` — (PMKM) #242p
✓ **Authority of the Consuls** ×2 — `enchantment/enchantment_a.csv` — (PKLD) #5s
✓ **Lightning Helix** ×3 — `instant/instant_l.csv` — (RAV) #213

#### Mainboard Lands (22)
✓ **Inspiring Vantage** ×4 — `land/land_i1.csv` — (SLD) #1375
✓ **Sacred Foundry** ×4 — `land/land_s1.csv` — (RVR) #409z
✓ **Hallowed Fountain** ×4 — `land/land_h.csv` — (UNF) #277
✓ **Floodfarm Verge** ×2 — `land/land_f1.csv` — (DSK) #330
✓ **Sunbillow Verge** ×2 — `land/land_s1.csv` — (DFT) #264
✓ **Starting Town** ×2 — `land/land_s1.csv` — (PFIN) #289s
✓ **Plains** ×2 — `land/land_p1.csv` — (CMA) #292
✓ **Mountain** ×1 — `land/land_m4.csv` — (ELD) #262
✓ **Island** ×1 — `land/land_i1.csv` — (ELD) #255

#### Sideboard (15)
✓ **No More Lies** ×3 — `instant/instant_n.csv` — (MKM) #221
✓ **Unwanted Remake** ×2 — `instant/instant_u.csv` — (DSK) #39
✓ **Abrade** ×2 — `instant/instant_a.csv` — (2XM) #114
✓ **Get Lost** ×2 — `instant/instant_g.csv` — (PLCI) #14p
✓ **Kutzil's Flanker** ×2 — `creature/creature_k.csv` — (LCI) #355
✓ **Torch the Tower** ×1 — `instant/instant_t.csv` — (WOE) #153
✓ **Day of Judgment** ×1 — `sorcery/sorcery_d.csv` — (M11) #12
✓ **Enduring Innocence** ×1 — `creature/creature_e.csv` — (DSK) #6
✓ **Authority of the Consuls** ×1 — `enchantment/enchantment_a.csv` — (PKLD) #5s

### Validation Script Result

```
$ python scripts/validate_decklist.py Decks/2026-03-30_Jeskai_Angels_Aggro/decklist.txt
✅ VALIDATION PASSED
Mainboard: 60 cards | Sideboard: 15 cards
```

---

## Executive Summary

This is a true aggro deck that kills on turn 4-5 through snowballing lifegain creatures that grow via +1/+1 counters. Every creature either gains life, grows from lifegain, or generates tokens. Delney doubles all of it.

**The kill:**
- T1: Sanctifier/Hawk (establish lifegain)
- T2: Pridemate/Channeler (start growing)
- T3: Warleader's Call / Voice of Victory / Anim Pakal (go wide + anthem)
- T4-5: Attack with 3-5 creatures, Pridemate is a 5/5+, Arabella pings for X, Warleader's Call pings per ETB

**Only 5 noncreature spells** (3 Helix, 2 Authority main) + 3 enchantments (Warleader's Call). Everything else attacks.

---

## Card-by-Card Breakdown

### T1 Plays (8 creatures)

**Hinterland Sanctifier** ×4 — Every creature you play after this gains 1 life. With Delney: 2 life per creature. Feeds Pridemate and Channeler counters every turn.

**Healer's Hawk** ×4 — 1/1 flying lifelink. Attacks immediately turn 2 for 1 lifelink (triggers Pridemate). Flying means it connects every turn. With Warleader's Call anthem: 2/2 flying lifelink.

### T2 Plays (14 creatures)

**Ajani's Pridemate** ×4 — THE payoff. Every life gain event = +1/+1 counter. T1 Sanctifier → T2 Pridemate → T3 play creature (Sanctifier triggers +1 life → Pridemate gets counter) + attack Hawk (lifelink → Pridemate gets counter). By T4 Pridemate is a 4/4 or 5/5 without any help.

**Essence Channeler** ×4 — Same as Pridemate but with flying when you've lost life (shocklands). Counter transfer on death = nothing is wasted. If they kill it, counters go to Pridemate or another threat.

**Voice of Victory** ×4 — The aggro closer. Mobilize 2 creates two 1/1 attacking tokens every time it attacks. Those tokens trigger Hinterland Sanctifier (+2 life), Warleader's Call (+2 damage pings), and Dazzling Angel (+2 life). Opponents can't cast spells during your turn = no tricks.

**Arabella, Abandoned Doll** ×2 — Attacks, counts power-2-or-less creatures you control, deals X damage to opponent and gains X life. With a board of Sanctifier + Hawk + Pridemate (still power 2 early) + Arabella = 4 damage + 4 life. Every lifegain event pumps Pridemate/Channeler further.

### T3 Plays (9 creatures + 3 enchantments)

**Anim Pakal, Thousandth Moon** ×2 — Attacks → gets +1/+1 counter → creates X Gnome tokens tapped and attacking (X = counters on Anim Pakal). Turn 4: 1 Gnome. Turn 5: 2 Gnomes. Turn 6: 3 Gnomes. Each Gnome triggers Sanctifier and Warleader's Call. Snowball engine.

**Dazzling Angel** ×2 — 2/2 flying Angel. Whenever another creature enters, gain 1 life. Redundant Sanctifier on a flying body. With Delney: triggers twice.

**Angel of Vitality** ×2 — "If you would gain life, gain that much plus 1 instead." Turns every Sanctifier trigger from +1 to +2. Every Hawk lifelink from +1 to +2. Every Arabella trigger gains extra. Gets +2/+2 when you're at 25+ life (common by T5). A 4/4 flying angel for 3.

**Delney, Streetwise Lookout** ×1 — Doubles triggered abilities of power-2-or-less creatures. Sanctifier triggers twice. Arabella triggers twice. Pridemate grows twice. Voice of Victory's Mobilize creates FOUR tokens instead of two. One copy because legendary, but game-ending when it resolves.

**Resplendent Angel** ×1 — If you gained 5+ life this turn (easy by T4), create a 4/4 flying angel token at end step. Top-end closer.

**Warleader's Call** ×3 — Anthem (+1/+1 to all creatures) + "whenever a creature you control enters, deal 1 damage to each opponent." Voice of Victory tokens trigger this. Anim Pakal Gnomes trigger this. Hawk becomes a 2/2 lifelink flyer. Pridemate enters as 2/2 minimum. This is the card that converts board presence into reach.

**Authority of the Consuls** ×2 — Opponent's creatures enter tapped (slows aggro mirrors) + gain 1 life per creature they play (feeds Pridemate). Game-defining against Izzet Prowess.

### Interaction (3 spells)

**Lightning Helix** ×3 — 3 damage to any target + gain 3 life. This is removal AND lifegain. Kills Prowess creatures, triggers Pridemate (+1/+1 counter), triggers Essence Channeler (+1/+1 counter). The only removal main because it feeds the gameplan.

---

## Mana Base Analysis (22 lands)

| Land | Count | Colors | Untapped T1? |
|------|-------|--------|-------------|
| Inspiring Vantage | 4 | RW | Yes (fast) |
| Sacred Foundry | 4 | RW | Yes (shock) |
| Hallowed Fountain | 4 | WU | Yes (shock) |
| Floodfarm Verge | 2 | WU | Yes (if Plains/Island) |
| Sunbillow Verge | 2 | RW | Yes (if Mountain/Plains) |
| Starting Town | 2 | Any | Yes (T1-3) |
| Plains | 2 | W | Yes |
| Mountain | 1 | R | Yes |
| Island | 1 | U | Yes |

**20 of 22 lands enter untapped** on T1 (Verges need a basic-type land first, but shocklands count). This is critical for aggro — no tapped lands slowing you down.

W sources: 19 (all except Mountain and Island)
R sources: 15 (Sacred Foundry 4, Inspiring Vantage 4, Sunbillow 2, Starting Town 2, Mountain 1, Steam Vents 0... actually no Steam Vents in this build)
U sources: 9 (Hallowed Fountain 4, Floodfarm 2, Starting Town 2, Island 1) — minimal, only needed for sideboard No More Lies

---

## Curve Analysis

| CMC | Count | Cards |
|-----|-------|-------|
| 1 | 10 | 4 Sanctifier, 4 Hawk, 2 Authority |
| 2 | 16 | 4 Pridemate, 4 Channeler, 4 Voice, 2 Arabella, 3 Helix (-1 is instant so flexible) |
| 3 | 12 | 2 Anim Pakal, 2 Dazzling Angel, 2 Angel of Vitality, 1 Delney, 1 Resplendent, 3 Warleader's Call |
| Lands | 22 | |

**Average CMC (spells): 1.95** — extremely low for true aggro.

---

## Matchup Table

| Matchup | Rating | Key |
|---------|--------|-----|
| Izzet Prowess | Even (50/50) | Authority taps their creatures; race with lifelink |
| Mono-Green Landfall | Favorable (55/45) | Fly over their ground blockers; grow faster |
| Dimir Mill | Favorable (60/40) | They can't interact with our speed; kill before mill matters |
| Jeskai Control | Unfavorable (40/60) | Fumigate wrecks us; board in No More Lies |
| Mono-White Aggro | Even (50/50) | Mirror-ish; Angel of Vitality + flying gives edge |
| Mono-Red Burn | Favorable (60/40) | Lifelink outraces burn |

---

## Weaknesses and Mitigations

1. **Board wipes destroy us** — Sideboard 3 No More Lies to hold up countermagic post-board vs control.
2. **No main deck interaction** beyond Lightning Helix — deliberate tradeoff for speed. Sideboard has 10 interaction spells.
3. **Legendary conflicts** (Arabella, Anim Pakal, Delney) — all at 1-2 copies to minimize dead draws.
4. **Blue sources thin** (9 total) — Blue is sideboard-only (No More Lies). Main deck is effectively Boros splash.
