# Esper Hope — Recursion Engine v2

> *"Every death feeds the next rebirth."*

---

## Fork Origin

Forked from: `Decks/2026-03-27_Esper_Hope_Recursion/` (v1)

**Core thesis shift:** v1 used Shinra Reinforcements as the only dedicated Smile at Death target. v2 expands the ETB package with three new Standard-legal creatures that each bring unique value to the recursion loop, while cutting underperforming slots.

---

## Key Changes (v1 → v2)

### OUT
- −1 Deep-Cavern Bat (3→2): Good disruption but not an engine piece; freeing a slot
- −2 Exemplar of Light: Weakest engine piece; counter accumulation too slow compared to mill output
- −2 Resplendent Angel: High floor but CMC 3 competes with Carrion Cruiser; Angel token upside requires 5+ life per turn which isn't guaranteed early
- −1 Three Steps Ahead (2→1): Luxury counterspell, trimmed to 1-of
- −2 Deduce: Lowest-value draw spell in the list; replaced by board presence
- −1 Sheltered by Ghosts (2→1): Trimmed to 1-of for space

### IN
- +2 Scarblade Scout (ECL) 118: `{1}{B}`, 2/2 lifelink, ETB mill 2. Cheapest Smile-recurrable ETB in Standard. Lifelink = ongoing Hope triggers every time it attacks/blocks.
- +2 Billowing Shriekmass (FDN) 56: `{3}{B}`, 2/3, ETB mill 3. Same mill output as Shinra Reinforcements, in black. Grows to 4/4 at threshold (7+ GY cards) — achievable by T6 with Smile loops. Second Shinra-tier Smile target.
- +2 Bloodghast (DFT) 337: `{B}{B}`, 2/1. No ETB — but landfall returns it from GY to battlefield. Every land drop = free Smile target. Dies → Scavenger's Food token → lifegain → Hope mills. Passive Soul Enervation drain on every return. Haste at opp ≤10 life.
- +1 Swamp (3 total): Bloodghast needs `{B}{B}` reliably; black mana base reinforced

---

## The Upgraded ETB Hierarchy for Smile at Death

| Priority | Card | Cost | Mill | Life | Other |
|----------|------|------|------|------|-------|
| 1 | Shinra Reinforcements | `{3}{W}` | 3 | +3 | → Hope mills 3 more |
| 1 | Billowing Shriekmass | `{3}{B}` | 3 | — | Grows to 4/4 at threshold |
| 2 | Scarblade Scout | `{1}{B}` | 2 | lifelink | Cheapest Smile target; ongoing value |
| 3 | Deep-Cavern Bat | `{1}{B}` | — | — | Hand disruption; 1/1 base |
| Passive | Bloodghast | `{B}{B}` | — | — | Self-recurs with landfall |

**Smile at Death priority targeting (v2):**
1. Shinra Reinforcements OR Billowing Shriekmass (mill 3 each)
2. Scarblade Scout if you need lifelink stabilisation
3. Bat only if opponent has key instants in hand

---

## Mana Base Notes

- 21 lands is tight but correct for avg CMC ~2.6 with 18 creatures
- Bloodghast at `{B}{B}` is the hardest cast; prioritise black dual fetching (Watery Grave, Godless Shrine, Concealed Courtyard) on T1-T2
- Scarblade Scout at `{1}{B}` is trivially castable on T2 off any black source
- Billowing Shriekmass at `{3}{B}` — same curve as Shinra; cast whichever color you have open on T4

---

## Updated Recursion Loop

```
SMILE AT DEATH ENGINE (v2):

Every upkeep (T6+):
├── Return Shinra Reinforcements: ETB mill 3, gain 3 → Hope mills 3
├── Return Billowing Shriekmass: ETB mill 3 → Hope mills 3 (if threshold, grows to 4/4)
├── OR Return Scarblade Scout: ETB mill 2 (cheaper; lifelink on attacks)
├── Soul Enervation passive: creatures left GY → drain 1, gain 1 → Hope mills 1
│
Each land drop:
└── Bloodghast returns from GY (landfall) → dies to blockers/wipe
    → Scavenger's Talent L1: creates Food → sacrifice → Hope lifegain → Hope mills
    → Soul Enervation: GY leave trigger → drain 1 more

Per-turn value at engine speed (T6+):
- Mill: 8–12 cards/turn
- Life: +5–8/turn  
- Bodies: 2–3 creatures returned, growing each Smile cycle
```

---

## Deck Runout Risk

This deck intentionally mills itself as part of the engine. With 60 cards and milling 8–12/turn from T6, you have ~3–4 turns before self-mill is a concern. **This is not a bug — it's the race:**
- Opponent starts at 60 cards
- You mill opponent 8–12/turn
- Opponent mills out T9–T10 before you do
- If game goes long: Scavenger's Talent L3 can sacrifice permanents to recur big threats; Bloodghast self-recurs independently of library size
- There is no Standard-legal GY→library reset in the current card pool. Win before you deck.

---

## Sideboard (unchanged from v1)

| Card | vs. |
|------|-----|
| Moment of Craving ×2 | Aggro — cheap lifegain removal |
| Enduring Innocence ×2 | Aggro — lifegain engine |
| Bitter Triumph ×1 | Midrange — cheap exile |
| Negate ×2 | Control — counter their sweepers |
| Enduring Curiosity ×2 | Control — card advantage |
| Spellgyre ×1 | Control — bounce + draw |
| Angel of Finality ×2 | GY decks — exile their GY on ETB |
| Deadly Cover-Up ×2 | GY decks — mass GY exile + tutor |
| Consuming Ashes ×1 | Midrange — exile a creature |
