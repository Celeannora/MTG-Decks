# Esper Hope — WUB Lifegain/Mill/Angel Control

> *"Where there is life, there is hope — and where there is hope, memories fade."*

---

## Database Query Report

### Queries Run (v2 additions)

| Query | Results |
|-------|---------|
| `search_cards.py --type sorcery --colors WUB --tags wipe` | 18 candidates |
| `search_cards.py --type creature --colors WUB --tags lifegain --oracle "mill"` | 7 candidates |
| Individual detail lookups (Day of Judgment, Split Up, Shinra Reinforcements, Deadly Cover-Up) | 4 detail reads |

### v2 Changes

**IN (Mainboard):**
- +2 Day of Judgment (FDN) 140 — sorcery/sorcery_d.csv — {2}{W}{W}, destroy all creatures, rare/mythic ✅
- +2 Split Up (DSK) 32 — sorcery/sorcery_s.csv — {1}{W}{W}, destroy all tapped OR all untapped, rare ✅
- +2 Shinra Reinforcements (FIN) 118 — creature/creature_s2.csv — {2}{B}, ETB mills 3 + you gain 3 life, common ✅

**OUT (Mainboard):**
- −2 Ajani's Pridemate — no evasion, weakest competitive body, replaced by Shinra Reinforcements
- −2 Opt — lowest-impact cantrip; 4 board wipe slots more critical for tournament resilience
- −2 Think Twice — flashback cute but slot value < wipe redundancy at tournament level

**IN (Sideboard):**
- +2 Deadly Cover-Up (MKM) 83 — sorcery/sorcery_d.csv — {3}{B}{B}, destroy all creatures + optional full-name exile, rare ✅

**OUT (Sideboard):**
- −2 Malicious Eclipse — replaced by Deadly Cover-Up; exile is strictly better than -2/-2 sweep for tournament graveyard hosing

### Rejected v2 Candidates

- **Spectacular Pileup** {3}{W}{W} — Destroys all creatures+Vehicles, indestructible removal. Excellent but CMC 5 competes with Lyra on same turn. Day of Judgment at CMC 4 is more reliable. Cut.
- **Singularity Rupture** {3}{U}{B}{B} — UB wipe + mill half library. Double black + double blue is too color-intensive for turn 6 in this mana base. Cut.
- **Shroudstomper** {3}{W}{W}{B}{B} — 5/5 deathtouch ETB drain + draw. Mana cost requires 5 specifically colored sources by turn 7; too slow at CMC 7. Cut.
- **Shimmercreep** {4}{B} — Vivid ETB lifegain scales with color count. Good in long games but ETB is once; Shinra Reinforcements at CMC 3 contributes sooner. Cut.
- **Day of Black Sun** {X}{B}{B} — X-based wipe is mana-intensive and conditional on mana value. Day of Judgment at flat {2}{W}{W} is more reliable. Cut.

---

## Executive Summary

**Deck name:** Esper Hope v2
**Colors:** Esper (White/Blue/Black)
**Format:** Standard
**Archetype:** Lifegain/Mill/Angel Control

**What changed from v1:** The two structural weaknesses — no mainboard board wipe and thin lifegain density — are now directly addressed. Day of Judgment and Split Up provide two distinct wipe modes at CMC 3-4. Shinra Reinforcements adds a synergistic lifegain + mill body that feeds Hope Estheim on both axes simultaneously. Opt and Think Twice were the lowest-value draw spells; their slots are fully justified by the new board control package. Sideboard Deadly Cover-Up replaces Malicious Eclipse for hard exile + full board destruction, which is superior in a tournament environment where graveyard recursion is prevalent.

**The Core Loop (unchanged):**
1. Deploy Hope Estheim and lifegain enablers
2. Every point of life gained triggers Hope Estheim's end-step mill
3. Mill engines (Mindskinner, Overlord, Stillness in Motion, Shinra Reinforcements) attack the library directly
4. Angel finishers (Resplendent Angel, Exemplar, Lyra) provide aerial beatdown backup
5. **NEW: Board wipes (Day of Judgment, Split Up) reset go-wide threats that the Angel package cannot race**

---

## Turn-by-Turn Projection

### Ideal Line (Keep Hand: Authority + Concealed Courtyard + Hope Estheim + Deep-Cavern Bat + Heartless Act + Deduce + Plains)

| Turn | Action | Life | Opponent Mill |
|------|--------|------|---------------|
| T1 | Authority of the Consuls | 20 | 0 |
| T2 | Hope Estheim (lifelink) + Concealed Courtyard | 20 | 0 |
| T3 | Deep-Cavern Bat ETB: exile their removal. Bat attacks → Hope triggers → mill 1 (lifelink). Authority trigger if they played a creature. | 21 | 1 |
| T4 | Shinra Reinforcements ETB: mill 3, gain 3 → Hope triggers → mill 3. Deduce → draw + Clue. | 24 | 7 |
| T4 EoT | Heartless Act holds up | 24 | 7 |
| T5 | Resplendent Angel. Attack with Hope + Bat + Shinra → ~4 life gained → mill 4. Resplendent triggers: gained 4 ≥ 5? No. | 28 | 11 |
| T5 EoT | Resplendent checks: 4 life gained T5. No token yet — need 5. | 28 | 11 |
| T6 | Lyra Dawnbringer enters. All Angels gain lifelink. Attack: Hope (2 lifelink) + Bat (1 lifelink) + Resplendent Angel (3/3 lifelink) + Shinra (2 regular) = 8 life. Hope triggers mill 8. Resplendent: 8 ≥ 5 → **4/4 Angel token EoT**. | 36 | 19 |
| T7 | Angel token + Exemplar of Light (gains counters from T6 lifegain). Attack: 5 fliers dealing ~12 damage + 12 life gained → mill 12. Exemplar now has 8 counters from accrued lifegain — can exile 2 permanents. | 48 | 31 |
| T8 | Opponent at ~20 cards left in library. Mill 15+ expected this turn. **Win by empty library T9 or T8 attack lethal.** | 55+ | 46+ |

### Against Aggro (Adjusted Line)

| Turn | Action | Note |
|------|--------|------|
| T1 | Authority of the Consuls | Taps their T1 creature |
| T2 | Hope Estheim | Their creature is tapped; no race yet |
| T3 | Heartless Act / Get Lost | Remove their largest threat |
| T4 | **Split Up** (destroy all tapped) | After their attack step, all their tapped creatures die. Your untapped Hope survives. |
| T5 | Shinra Reinforcements | Refuel: gain 3, mill 3 |
| T6 | Lyra Dawnbringer | Stabilized, begin kill clock |

### Against Control (Adjusted Line)

| Turn | Action | Note |
|------|--------|------|
| T1-2 | No More Lies / Spell Pierce up | Counter their early sweepers |
| T3 | The Mindskinner | Unblockable, mills every combat |
| T4 | Overlord of the Balemurk (Impend {1}{B}) | Already milled 4 on T2 if deployed then; now a 6/5 |
| T5 | **Day of Judgment** if they've rebuilt a board | Clean wipe while Mindskinner is unblockable |
| T6+ | Mindskinner + Hope Estheim end-step trigger | 3-4 cards milled per turn passively, more with attacks |

---

## Updated Curve Analysis

| CMC | Cards | Count |
|-----|-------|-------|
| 1 | Authority of the Consuls, Spell Pierce | 2 |
| 2 | Hope Estheim (×4), Deep-Cavern Bat (×3), Heartless Act (×2), Get Lost (×2), No More Lies (×2), Deduce (×2) | 15 |
| 3 | Split Up (×2), The Mindskinner (×2), Resplendent Angel (×2), Three Steps Ahead (×2), Shinra Reinforcements (×2), Stillness in Motion (×1), Sheltered by Ghosts (×2) | 13 |
| 4 | Day of Judgment (×2), Exemplar of Light (×2) | 4 |
| 5 | Overlord of the Balemurk (×2), Lyra Dawnbringer (×2) | 4 |

**Average CMC (non-land):** 2.68

**Note on Curve Shift:** v1 was 2.42 average CMC; v2 is 2.68. The four 1-mana cantrips (Opt × 2, Think Twice flashback mode) are replaced by CMC 3-4 board wipes. This is an intentional tournament calibration — the deck needs to answer wide boards, and the lifegain engine generates enough mana advantage through Deduce Clue tokens and Three Steps Ahead to compensate for losing the pure cantrips.

---

## Updated Matchup Table

| Matchup | Game Plan | Key Cards | Board-In / Board-Out |
|---------|-----------|-----------|----------------------|
| Aggro (Red/Gruul) | Stabilize with wipes, gain life, wall with Angels | **Split Up**, Day of Judgment, Authority of the Consuls, Heartless Act | +2 Moment of Craving, +2 Enduring Innocence / −2 The Mindskinner, −1 Stillness in Motion |
| Control (Azorius/Dimir) | Protect threats, mill as win-con, grind | No More Lies, Three Steps Ahead, The Mindskinner | +2 Negate, +2 Enduring Curiosity / −2 Heartless Act, −2 Get Lost |
| Midrange (Golgari/Rakdos) | Out-value on lifegain, wipe their board, aerial pressure | **Day of Judgment**, Exemplar of Light, Lyra Dawnbringer | +1 Bitter Triumph, +2 Enduring Innocence / −1 Stillness in Motion, −1 Spell Pierce, −1 Authority |
| Graveyard/Reanimator | Counter key spells, exile graveyard aggressively | No More Lies, Angel of Finality, **Deadly Cover-Up** | +2 Angel of Finality, +2 Deadly Cover-Up, +1 Consuming Ashes / −2 The Mindskinner, −1 Authority, −2 Shinra Reinforcements |
| Tokens/Go-Wide | **Split Up** or **Day of Judgment** after their attack, Lyra lifelink overwhelms | **Day of Judgment**, **Split Up**, Lyra Dawnbringer | +2 Deadly Cover-Up / −1 Stillness in Motion, −1 Spell Pierce |

---

## Structural Weaknesses (Updated)

1. ~~No mainboard board wipe~~ — **RESOLVED** with Day of Judgment ×2 + Split Up ×2
2. ~~Thin lifegain density~~ — **IMPROVED** with Shinra Reinforcements (ETB: +3 life +3 mill)
3. **Reduced cantrip count** — Opt and Think Twice removed; Deduce ×2 + Three Steps Ahead ×2 + Spell Pierce remain. Clue tokens from Deduce partially compensate.
4. **Three-color mana base** — unchanged. 16W / 13U / 13B sources. The Mindskinner {U}{U}{U} remains the hardest cast; 13 blue sources achievable by turn 4.
5. **Legendary creature density** — unchanged from v1. Hope Estheim ×4, The Mindskinner ×2, Lyra ×2.

---

## Playtesting Notes

**v2 key decision points:**
- **Split Up vs Day of Judgment:** Deploy Split Up after opponents' attack step (all their creatures are tapped). Deploy Day of Judgment when opponent has untapped threats you cannot outrace. Never tap out for a wipe if Mindskinner is unblocked and winning the mill race.
- **Shinra Reinforcements timing:** Play on T3 to curve into T4 wipe or T4 Exemplar. The ETB gain + mill means it feeds Hope Estheim on the same turn it enters — don't hold it for value.
- **Deadly Cover-Up (sideboard):** Collect Evidence 6 mode is usually achievable by turn 5+ in this deck (graveyard fills fast via Shinra, Overlord, Stillness in Motion). Always pay the additional cost when you can — the name-exile crushes recursion decks.
