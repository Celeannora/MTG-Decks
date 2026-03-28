# Esper Hope — Recursion Engine v1

> *"Death is not the end. It is merely the beginning of another cycle."*

---

## Fork Origin

Forked from: `Decks/2026-03-25_Esper_Hope/` (v2, commit 303c2c8)

**Core thesis shift:** v2 was a control deck that happened to mill. This fork is a **recursion engine** that uses death and rebirth as the primary value engine, with Hope Estheim as the bridge between lifegain, mill, and graveyard loops.

---

## Database Scan Report

### Cards Verified

| Card | Cost | Type | Set | Oracle Summary | Synergy |
|------|------|------|-----|----------------|----------|
| Smile at Death | {3}{W}{W} | Enchantment | TDM 24 | Upkeep: return up to 2 creatures (power ≤2) from GY to BF, each gets +1/+1 counter | 10/10 — recurs Hope, Bat, Shinra, Exemplar every single turn |
| Scavenger's Talent | {B} | Enchantment Class | BLB 111 | L1: creature dies → Food; L2: sacrifice → mill 2; L3: sacrifice 3 → recur any creature | 9/10 — Food triggers Hope lifegain; L3 recurs big creatures Smile can't reach |
| Carrion Cruiser | {2}{B} | Artifact — Vehicle | DFT 78 | ETB: mill 2 + return creature/Vehicle from GY to hand; Crew 1 | 8/10 — on-curve GY filler + hand refueler, crewed by any 1-power creature |
| Soul Enervation | {3}{B} | Enchantment | MKM 106 | Flash; ETB: -4/-4 to target creature; creature cards leaving GY → drain 1, gain 1 | 8/10 — every Smile at Death trigger drains opp + gains life = Hope mills more |

### Wind Crystal — NOT FOUND IN DATABASE

Wind Crystal was not located in any artifact_*.csv file. Possible explanations:
- The card may be named differently in MTGA (e.g. "Blue Crystal" or "Crystal of Wind")
- It may be a creature or instant/sorcery rather than an artifact
- It may be in a set not yet indexed in this database

**Recommendation:** Manually verify Wind Crystal's MTGA collection name and collector number. If confirmed legal, it likely slots in as a 2-of replacing 1× Spell Pierce and 1× No More Lies given its expected blue mana utility role. This analysis will be updated when the card is located.

---

## Structural Restructuring from v2

### What Changed and Why

**The v2 Problem:** v2 had 4 board wipes (Day of Judgment ×2, Split Up ×2) designed for a midrange aggro-control meta. But adding Smile at Death creates a fundamental tension:
- **Smile at Death needs creatures to die** — you WANT your small creatures to go to the graveyard so Smile can recur them
- **Split Up kills your own creatures too** — asymmetric wipes that kill your tapped creatures are anti-synergistic with Smile
- **Lyra Dawnbringer** is a dead-end for Smile (power 5, unreclaimable) AND competes on the same CMC slot as Smile itself

**The Solution:** Cut the anti-synergy cards, reinforce the loop.

### Card Changes (v2 → v3 fork)

**OUT:**
- −2 Split Up (anti-synergy: kills your own tapped creatures before Smile can recur them)
- −2 Lyra Dawnbringer (CMC 5 = competes with Smile; power 5 = Smile can't recur her; replaced by Soul Enervation at same CMC with active graveyard drain)
- −1 Three Steps Ahead (cut to 1-of to make room; lowest-utility slot in recursion build)

**IN:**
- +2 Smile at Death (TDM) 24 — the engine
- +2 Scavenger's Talent (BLB) 111 — the bridge layer
- +2 Soul Enervation (MKM) 106 — flash removal + passive drain off every Smile trigger
- +2 Carrion Cruiser (DFT) 78 — mill + return to hand on ETB; crews with any 1-power creature
- −1 Three Steps Ahead → adjusted to fit 60

**Net creature count:** 17 (down from 19 in v2). The two lost creatures are Lyra Dawnbringer, replaced by enchantment/artifact value. This is intentional — the deck now wants creatures in the graveyard, not just on the battlefield.

---

## The Recursion Loop (Full Cycle)

```
SMILE AT DEATH ENGINE:

T5: Smile at Death resolves
│
├── Every upkeep thereafter:
│   ├── Return Deep-Cavern Bat (1/1 → 2/2 w/ counter) + Shinra Reinforcements (2/3 → 3/4)
│   ├── Shinra ETB: mill 3 + gain 3 life
│   ├── Hope Estheim end-step: mill 3 (from Shinra lifegain)
│   └── Soul Enervation: creature left GY → drain 1, gain 1 → Hope mills 1 more
│
├── If Scavenger's Talent is at L1:
│   └── Creatures dying (Bat, Shinra from combat/removal) → Food tokens
│       → Food = lifegain trigger → Hope mills
│
├── If Scavenger's Talent is at L2:
│   └── Sacrifice Food → mill 2 more
│
└── If Scavenger's Talent is at L3:
    └── End step: sacrifice 3 permanents (Food ×3) → recur Overlord, Resplendent, or Mindskinner
        (big creatures Smile can't reach)
```

**Per-turn value at engine speed (T6+):**
- Mill: 6–10 cards/turn (Smile ETB + Shinra + Hope trigger + Soul Enervation + Stillness in Motion)
- Life: +4–6/turn (Shinra ETB + Soul Enervation drain + Bat lifelink)
- Bodies: 2 creatures returned free every upkeep, growing each cycle

---

## Turn-by-Turn Projection

### Ideal Line

| Turn | Action | Life | Opp Mill | Notes |
|------|--------|------|----------|-------|
| T1 | Authority of the Consuls | 20 | 0 | Taps their T1 threat |
| T2 | Hope Estheim | 20 | 0 | Engine anchor |
| T3 | Carrion Cruiser (ETB: mill 2, return Bat to hand if already in GY) | 20 | 2 | Fills GY immediately |
| T3 | Deep-Cavern Bat (hand disruption, exiles their removal) | 20 | 2 | |
| T4 | Scavenger's Talent L1. Shinra Reinforcements (ETB: +3 life, mill 3) → Hope mills 3 | 23 | 8 | |
| T4 EoT | Heartless Act / Get Lost holds up | 23 | 8 | |
| T5 | **Smile at Death** enters. Scavenger's Talent → L2 ({1}{B}). | 23 | 8 | Engine online next upkeep |
| T6 Upkeep | Smile triggers: return Bat + Shinra. Shinra ETB: mill 3, +3 life → Hope mills 3. Soul Enervation passive: GY left → drain 1, gain 1 → Hope mills 1 more. | 27 | 15 | |
| T6 | Scavenger's Talent L3 ({2}{B}). Attack: Bat (lifelink) + Shinra → Hope mills. Resplendent Angel (3/3 flying). | 30 | 20 | |
| T7 Upkeep | Smile: return Bat + Shinra again (+1/+1 stacks: now 2/2 Bat, 3/4 Shinra). ETB chain. | 35 | 28 | Bodies growing |
| T7 | Scavenger's L3: sacrifice 3 Food → **recur Overlord of the Balemurk** (6/5 with ward). Attack: 4 bodies. | 38 | 35 | |
| T8 | 40+ cards milled. Opponent at 20 or fewer cards. Attack for lethal OR mill out T9. | 44+ | 46+ | Win |

### Against Graveyard Hate (Opponent runs exile effects)

| Situation | Response |
|-----------|----------|
| Opponent exiles GY | Carrion Cruiser refills GY from library; Stillness in Motion mills 3/upkeep passively |
| Smile at Death removed | Scavenger's Talent L3 still recurs big creatures independently |
| Both enchantments removed | Fall back to control line: Day of Judgment + Overlord + Mindskinner mill win |

---

## Updated Curve Analysis

| CMC | Cards | Count |
|-----|-------|-------|
| 1 | Authority of the Consuls, Spell Pierce, Scavenger's Talent ×2 | 4 |
| 2 | Hope Estheim ×4, Deep-Cavern Bat ×3, Heartless Act ×2, Get Lost ×2, No More Lies ×2, Deduce ×2, Stillness in Motion ×1, Sheltered by Ghosts ×2 | 18 |
| 3 | Carrion Cruiser ×2, The Mindskinner ×2, Resplendent Angel ×2, Two Steps Ahead ×2, Shinra Reinforcements ×2 | 10 |
| 4 | Day of Judgment ×2, Soul Enervation ×2, Exemplar of Light ×2 | 6 |
| 5 | Smile at Death ×2, Overlord of the Balemurk ×2 | 4 |

**Average CMC (non-land):** 2.71

---

## Updated Matchup Table

| Matchup | Game Plan | Key Cards | Board-In / Board-Out |
|---------|-----------|-----------|----------------------|
| Aggro (Red/Gruul) | Authority stalls T1; Day of Judgment resets; Smile recurs blockers every upkeep | Authority, Day of Judgment, Smile at Death | +2 Moment of Craving, +2 Enduring Innocence / −2 Soul Enervation, −1 Smile at Death, −1 Scavenger's Talent |
| Control (Azorius/Dimir) | Scavenger's Talent L2+L3 is hard to interact with at {B}; Smile behind No More Lies / Three Steps Ahead | Scavenger's Talent, Smile at Death, No More Lies | +2 Negate, +2 Enduring Curiosity / −2 Heartless Act, −2 Get Lost |
| Midrange (Golgari/Rakdos) | Carrion Cruiser blocks + refuels; Soul Enervation flash kills their fatties; Smile recurs your bodies | Soul Enervation, Carrion Cruiser, Day of Judgment | +1 Bitter Triumph, +2 Enduring Innocence / −1 Spell Pierce, −1 Authority, −1 Stillness in Motion |
| Graveyard/Reanimator | Angel of Finality + Deadly Cover-Up exile their GY; our recursion is cheaper and faster | Angel of Finality, Deadly Cover-Up, No More Lies | +2 Angel of Finality, +2 Deadly Cover-Up, +1 Consuming Ashes / −2 Carrion Cruiser, −1 Smile at Death, −1 Scavenger's Talent, −1 Authority |
| Tokens/Go-Wide | Day of Judgment resets; Scavenger's L1 creates Food every time their tokens die to our wipe | Day of Judgment, Scavenger's Talent, Soul Enervation | +2 Deadly Cover-Up / −1 Stillness in Motion, −1 Spell Pierce |

---

## Remaining Weaknesses

1. **Wind Crystal unverified** — if confirmed legal in MTGA, likely replaces 1× Spell Pierce + 1× No More Lies. Update pending card location.
2. **No Lyra Dawnbringer** — the lifelink anthem is gone. Compensated by Soul Enervation drain + Scavenger's Food + Shinra ETB, but the ceiling on lifegain is lower in long games.
3. **Smile at Death is CMC 5** — must survive to T5 without dying to aggro. Authority of the Consuls on T1 is critical in this build.
4. **Carrion Cruiser crew requirement** — needs a 1-power creature to crew. In empty-board scenarios (after Day of Judgment), it's a vanilla 3/2. Mitigated by the fact that post-wipe you'll have Smile returning creatures immediately.
5. **Scavenger's Talent L3 needs 3 sacrificeable permanents** — Food tokens from L1 are the primary fuel. Without L1 online early, L3 is slow. Prioritize Scavenger's Talent on T1 in most game plans.

---

## Playtesting Notes

- **Smile at Death priority targeting:** Always return Shinra Reinforcements first (ETB mills 3 + gains 3). Second slot: Deep-Cavern Bat if opponent has instants in hand; Exemplar of Light if you need counter accumulation for permanent exile.
- **Carrion Cruiser crew:** Deep-Cavern Bat (1/1) crews it for free. After Smile gives Bat a +1/+1 counter it becomes 2/2 — still crews Cruiser.
- **Soul Enervation timing:** Hold as a flash until opponent attacks with a key threat; fire as a combat trick. The passive drain is a bonus that stacks with Smile recursion.
- **Don't level Scavenger's Talent to L2 until you have Food tokens available** — the sacrifice cost is real. L1 → wait for Food accumulation → L2 → L3.
