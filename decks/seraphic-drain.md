# Seraphic Drain
**Format:** Standard (2025–2026)
**Colors:** Azorius (W/U)
**Archetype:** Lifelink Angel Mill

---

## Overview

An Azorius combo-control deck built around three interlocking engines:

1. **Life gain snowball** — Cheap lifelink creatures and "creature enters → gain 1 life" triggers rapidly inflate your life total.
2. **Hope Estheim** — At each end step, mills opponents for X cards, where X = life gained this turn. With 6–8 triggers per turn, this alone mills 10–15 cards/turn by mid-game.
3. **Space-Time Anomaly** — At 30+ life, one casting mills an opponent's entire remaining library.

Lyra Dawnbringer is the top-end finisher, granting all other Angels +1/+1 and lifelink, which compounds the life gain and makes every attacker lethal from a mill perspective.

---

## Decklist (60 Cards)

### Creatures (24)

| Qty | Card | Mana Cost | Set | Role |
|-----|------|-----------|-----|------|
| 4 | Healer's Hawk | {W} | FDN | Turn-1 lifelink flyer |
| 4 | Hinterland Sanctifier | {W} | FDN | ETB life trigger engine |
| 4 | Hope Estheim | {W}{U} | FIN | Mill engine — end step mills X = life gained |
| 4 | Lifecreed Duo | {1}{W} | BLB | Flying + ETB life trigger |
| 4 | Haliya, Guided by Light | {2}{W} | EOE | ETB life + end-step card draw if 3+ life gained |
| 2 | Linden, the Steadfast Queen | {W}{W}{W} | FDN | Attack-trigger life gain (1 per white creature) |
| 2 | Lyra Dawnbringer | {3}{W}{W} | FDN | All Angels +1/+1 + lifelink; 5/5 Flying First Strike Lifelink |

### Spells (12)

| Qty | Card | Mana Cost | Set | Role |
|-----|------|-----------|-----|------|
| 4 | Space-Time Anomaly | {2}{W}{U} | EOE | Mills target player X = your life total |
| 3 | Split Up | {1}{W}{W} | DSK | Flexible sorcery — destroy all tapped OR all untapped creatures |
| 3 | Starfall Invocation | {3}{W}{W} | BLB | Board wipe; gift clause returns your best creature |
| 2 | Negate | {1}{U} | FDN | Counter noncreature — protect Hope Estheim / Lyra |

### Lands (24)

| Qty | Card |
|-----|------|
| 4 | Glacial Fortress |
| 4 | Adarkar Wastes |
| 12 | Plains |
| 4 | Island |

---

## Win Conditions

### Primary — Space-Time Anomaly Kill
```
With Hope Estheim + 2x Hinterland Sanctifier + 2x Lifecreed Duo + Haliya on board:
  Each creature entering = 5 life gained (2×Sanctifier + 2×Lifecreed + Haliya)
  Hope Estheim mills 5 cards per creature played at end of turn

Life total math:
  Start: 20
  Turn 3 (3 triggers per turn): ~26–28 life
  Turn 4: Cast Space-Time Anomaly → mill 28 cards
  Turn 5: Lyra Dawnbringer → life gain explodes
  Turn 6: Space-Time Anomaly #2 at 35+ life → mill remaining library
```

### Secondary — Angel Beatdown
```
With Lyra Dawnbringer on board:
  Healer's Hawk becomes 2/2 Flying Lifelink
  Lifecreed Duo becomes 2/3 Flying Lifelink
  Haliya becomes 4/4 Lifelink
  Linden becomes 4/4 Vigilance Lifelink
  → Lyra herself hits for 6 First Strike Flying Lifelink
  → Massive life total swings amplify Hope Estheim milling 15-20+ per turn
```

---

## Card Synergy Map

```
Healer's Hawk ──────────────┐
Hinterland Sanctifier ──────┤──→ Life Gain ──→ Hope Estheim (mills X)
Lifecreed Duo ──────────────┤                       │
Haliya, Guided by Light ────┤                       │
Linden, the Steadfast Queen ┘                       ↓
                                             High Life Total
                                                    │
Lyra Dawnbringer ───────────→ Angels get Lifelink   │
                                    │               ↓
                                    └──────→ Space-Time Anomaly
                                             (mills = life total)
```

---

## Turn-by-Turn Game Plan

| Turn | Play | Life Total | Notes |
|------|------|-----------|-------|
| 1 | Healer's Hawk or Hinterland Sanctifier | 20 | Establish early board |
| 2 | Hope Estheim | ~22 | Mill engine online, start gaining 2–3/turn |
| 3 | Lifecreed Duo + hold Negate | ~26 | ETB triggers start compounding |
| 4 | Space-Time Anomaly | ~28 | Mills 28 cards; opponent at ~32 remaining |
| 5 | Lyra Dawnbringer | ~34 | All angels explode; gains 10+ per attack |
| 6 | Space-Time Anomaly #2 | ~38 | Mills 38 cards — game over |

---

## Matchup Notes

**vs. Aggro:** Healer's Hawk / Hinterland Sanctifier stabilize early. Life total climbs faster than they can race. Split Up handles resolved threats.

**vs. Midrange:** Starfall Invocation resets the board while returning Lyra to the battlefield. You re-establish faster with your cheap curve.

**vs. Control:** Resolve Hope Estheim early (they often don't have turn-2 counters). Back up key threats with Negate. Space-Time Anomaly is hard to answer at sorcery speed.

**vs. Other Mill:** You gain life faster than your library empties. Herald of Eternal Dawn in sideboard stops the kill condition entirely.

---

## Sideboard (15)

| Qty | Card | Set | Purpose |
|-----|------|-----|---------|
| 2 | Lyra Dawnbringer | FDN | Additional copies vs. creature-heavy builds |
| 2 | Linden, the Steadfast Queen | FDN | More attack-trigger life gain vs. aggro |
| 2 | Herald of Eternal Dawn | FDN | "You can't lose" vs. combo / burn |
| 2 | Negate | FDN | Extra counter protection vs. control |
| 3 | Spectacular Pileup | DFT | Go-wide hate with cycling to avoid dead draws |
| 4 | [Graveyard hate, e.g. Suncleanser or Void Rend] | — | Opponent graveyard recursion off milled cards |

---

## Card Notes

- **Hope Estheim** (FIN #226): The deck's namesake engine. As little as 5 life gained/turn mills an opponent's library in 12 turns passively; with Haliya and multiple Sanctifiers, you can hit 15–20 mills/end step by turn 5.
- **Space-Time Anomaly** (EOE #229): With 30 life, this is effectively "mill 30" for 4 mana at sorcery speed. Two castings with a healthy life total = instant win.
- **Lyra Dawnbringer** (FDN #707): Retroactively gives every angel in the deck lifelink. Makes each Haliya, Herald, and all other angels trigger Hope Estheim for massive mill bursts.
- **Haliya, Guided by Light** (EOE #19): Dual-purpose engine — generates life on each ETB *and* draws a card at end step if you gained 3+ life. Keeps the hand full while fueling the combo.
- **Split Up** (DSK #32): Asymmetric wipe — choose tapped to clear attackers without losing your untapped defenders, or choose untapped to hit prepared boards.
- **Starfall Invocation** (BLB #34): When behind, gift a card to the opponent and bring Lyra back to the field. Resets the board while keeping your key piece.
