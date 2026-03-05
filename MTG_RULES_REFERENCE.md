# Magic: The Gathering - Comprehensive Rules Reference for AI Deck Building

## Document Purpose
This reference provides critical MTG rules, interactions, and mechanical understanding necessary for AI-assisted deck construction. It prevents common errors in card evaluation, combo identification, and strategic planning.

---

## Table of Contents
1. [Turn Structure & Priority](#turn-structure--priority)
2. [The Stack & Spell Resolution](#the-stack--spell-resolution)
3. [Permanent Types & Interactions](#permanent-types--interactions)
4. [Triggered vs. Activated Abilities](#triggered-vs-activated-abilities)
5. [Targeting & Protection Rules](#targeting--protection-rules)
6. [Combat Mechanics](#combat-mechanics)
7. [Token Rules](#token-rules)
8. [Copy Effects](#copy-effects)
9. [State-Based Actions](#state-based-actions)
10. [Layers System](#layers-system)
11. [Common Misconceptions](#common-misconceptions)
12. [Card Advantage Theory](#card-advantage-theory)
13. [Mana Efficiency Calculations](#mana-efficiency-calculations)
14. [Combo Categories](#combo-categories)

---

## 1. Turn Structure & Priority

### Turn Phases (in order)
1. **Beginning Phase**
   - Untap Step (no priority, abilities trigger but don't go on stack yet)
   - Upkeep Step (triggered abilities from untap go on stack here)
   - Draw Step (draw card, then priority)

2. **Main Phase 1** (precombat)
   - Sorcery-speed actions: play lands, cast creatures/sorceries/enchantments/artifacts/planeswalkers

3. **Combat Phase**
   - Beginning of Combat Step (triggers, last chance to tap creatures before attackers declared)
   - Declare Attackers Step (attackers declared, triggers go on stack)
   - Declare Blockers Step (blockers declared, triggers go on stack)
   - Combat Damage Step (damage assigned simultaneously, triggers)
   - End of Combat Step (cleanup triggers)

4. **Main Phase 2** (postcombat)
   - Same as Main Phase 1

5. **Ending Phase**
   - End Step ("at beginning of end step" triggers)
   - Cleanup Step (discard to hand size, damage removed, "until end of turn" effects end)

### Priority Rules
- Active player receives priority first in each step/phase
- Players must pass priority in succession for stack to resolve
- **Critical**: You CANNOT take actions during your opponent's untap step
- **Critical**: "At the beginning of your upkeep" triggers happen BEFORE you can cast spells

---

## 2. The Stack & Spell Resolution

### Stack Mechanics
- Last In, First Out (LIFO) - most recent spell/ability resolves first
- Players can respond to spells/abilities by adding more to the stack
- When both players pass priority with stack not empty, top item resolves

### Example: Counterspell Interaction
```
Player A: Casts Lightning Bolt targeting Player B
  Stack: [Lightning Bolt]
Player B: Casts Counterspell targeting Lightning Bolt
  Stack: [Lightning Bolt] <- [Counterspell]
Both pass priority:
  Counterspell resolves first, counters Lightning Bolt
  Lightning Bolt is countered, never resolves
Result: Player B takes 0 damage
```

### Spell Resolution Rules
- On resolution, spell checks if all targets are still legal
- If ALL targets illegal, spell is countered by game rules ("fizzles")
- If SOME targets illegal, spell resolves affecting only legal targets

**Critical Error to Avoid**: 
❌ "I'll counter their creature after it enters the battlefield"
✅ Creatures must be countered WHILE ON THE STACK (before resolution)
✅ Once a creature resolves and enters battlefield, it's a PERMANENT and cannot be "countered"

---

## 3. Permanent Types & Interactions

### Permanent Definition
- **Permanents**: Cards on the battlefield (creatures, artifacts, enchantments, planeswalkers, lands)
- **Non-Permanents**: Instants and sorceries (exist only on stack/graveyard)

### Creature Summoning Sickness
- Creatures have summoning sickness the turn they enter under your control
- **Cannot**: Attack or use abilities with {T} (tap symbol) in cost
- **Can**: Block, use abilities without {T}, be affected by effects
- **Haste**: Keyword that ignores summoning sickness

### Artifacts
- **Artifact Creatures**: Subject to both creature and artifact effects (e.g., artifact destruction kills them)
- **Equipment**: Attaches to creatures, survives when equipped creature dies
- **Vehicles**: Become artifact creatures when "crewed" (tap creatures with total power ≥ crew cost)

### Enchantments
- **Auras**: Target a permanent/player, attach on resolution. If target becomes illegal before resolution, Aura is countered.
- **Enchantment Creatures**: Subject to both enchantment and creature effects

### Planeswalkers
- **Not creatures**: Cannot attack or block
- **Loyalty Abilities**: Activate only at sorcery speed, only once per turn
- **Damage**: Redirected damage becomes loyalty loss (pre-2018 rules changed this, now damage can target planeswalkers directly)
- **Combat**: Can be attacked by creatures (defender chooses blockers)

---

## 4. Triggered vs. Activated Abilities

### Triggered Abilities
**Format**: "When", "Whenever", "At" [condition], [effect]

**Examples**:
- "When this creature enters, draw a card"
- "Whenever you cast a spell, deal 1 damage to any target"
- "At the beginning of your upkeep, create a token"

**Key Rules**:
- Go on stack automatically when triggered
- Can be responded to
- Controlled by controller of source permanent
- If permanent leaves battlefield, ability still resolves (uses "last known information")

### Activated Abilities
**Format**: [Cost]: [Effect]

**Examples**:
- "{T}: Add {U}"
- "{2}{R}, Sacrifice this creature: Deal 3 damage to any target"
- "{1}, Discard a card: Draw a card"

**Key Rules**:
- Player chooses when to activate (within timing restrictions)
- Go on stack when activated
- Can be responded to
- Must pay full cost to activate

### Critical Distinction
❌ **Wrong**: "I'll activate this creature's triggered ability"
✅ **Correct**: "This creature's ability will trigger when [condition]"
✅ **Correct**: "I'll activate this creature's ability by paying [cost]"

---

## 5. Targeting & Protection Rules

### Targeting Requirements
- Spell/ability must use word "target" to target
- Targets chosen on CASTING/ACTIVATION (before resolution)
- Must choose legal targets or cannot cast/activate

### Hexproof
- "Can't be the target of spells or abilities your opponents control"
- **Can**: Be affected by non-targeting effects (e.g., "Destroy all creatures")
- **Can**: Be targeted by own controller's spells/abilities

### Ward [Cost]
- When targeted by opponent's spell/ability, that spell/ability is countered unless opponent pays [Cost]
- Ward trigger goes on stack ABOVE the spell targeting it
- If opponent doesn't/can't pay, spell is countered

### Shroud (older keyword, rare in modern sets)
- "Can't be the target of spells or abilities"
- Stricter than hexproof (can't even target with own spells)

### Protection from [Quality]
**DEBT**: Damage, Enchant/Equip, Block, Target
- **Damage**: Prevents all damage from sources with that quality
- **Enchant/Equip**: Can't be enchanted/equipped by Auras/Equipment with that quality
- **Block**: Can't be blocked by creatures with that quality
- **Target**: Can't be targeted by spells/abilities with that quality

**Critical**: Protection does NOT prevent non-targeting effects
- "Destroy all creatures" kills creatures with protection
- "Each player sacrifices a creature" forces sacrifice of protected creature

---

## 6. Combat Mechanics

### Attacking
1. Declare attackers (all at once)
2. Defending player declares blockers (all at once)
3. Attacking player assigns combat damage order for each blocked attacker
4. Defending player assigns combat damage order for each blocking creature
5. Combat damage dealt simultaneously

### Blocking Rules
- One blocker can only block one attacker
- Multiple blockers can block same attacker (attacker's controller orders damage)
- Blocked attacker deals NO damage to defending player (unless trample)

### Combat Keywords

**First Strike** / **Double Strike**
- First Strike: Deals combat damage in first strike damage step
- Double Strike: Deals damage in BOTH first strike and regular damage steps
- Creatures without first strike deal damage in regular damage step
- **Critical**: If first strike kills blocker, blocker deals no damage back

**Trample**
- Excess damage beyond lethal to blockers carries over to defending player
- "Lethal damage" = toughness minus damage already marked
- **Must assign at least lethal to all blockers before trampling over**

**Flying**
- Can only be blocked by creatures with flying or reach
- Can block non-flying creatures

**Menace**
- Must be blocked by two or more creatures
- If defender can't block with 2+ creatures, attacker is unblocked

**Vigilance**
- Doesn't tap when attacking
- Can attack and still block on opponent's turn

**Deathtouch**
- Any amount of damage from this creature to another creature is lethal
- **Combo with Trample**: Only needs to assign 1 damage to blocker (deathtouch makes it lethal), rest tramples over

**Lifelink**
- Damage dealt by this source also causes controller to gain that much life
- Happens simultaneously with damage (not a trigger)

---

## 7. Token Rules

### Token Basics
- Tokens are permanents while on battlefield
- **Cannot**: Exist in hand, library, graveyard, exile (they cease to exist)
- **Exception**: If token is exiled temporarily with "return it to battlefield" effect, it DOES return

### Token Creation
- Created with specified characteristics (power/toughness, color, type, abilities)
- Not "cast" (don't trigger "whenever you cast" abilities)
- Do trigger "enters the battlefield" abilities

### Token Copying
- If effect creates token "that's a copy of" a permanent:
  - Copies all printed characteristics
  - Does NOT copy counters, auras attached, or effects modifying it
  - Does copy abilities that modify power/toughness based on conditions

**Example**:
```
Original: 3/3 creature with +1/+1 counter (currently 4/4)
Token copy: 3/3 creature (no counter)

Original: Creature with "This creature gets +1/+1 for each artifact you control"
Token copy: Also gets +1/+1 for each artifact (copies printed ability)
```

---

## 8. Copy Effects

### Copying Spells
- Copy goes on stack above original
- Copy resolves first
- Copy is NOT cast (doesn't trigger "whenever you cast" abilities)
- Controller of copy may choose new targets

### Copying Permanents
- Copy enters battlefield as a copy of target permanent
- Copies current characteristics (including abilities from other effects)
- Does NOT copy:
  - Whether it's tapped/untapped
  - Counters on it
  - Auras/Equipment attached to it
  - Non-copy effects affecting it

**Critical Interaction Error to Avoid**:
❌ "Extravagant Replication copies a planeswalker, so I get extra loyalty activations per turn"
✅ "Each planeswalker can activate ONE loyalty ability per turn (controller-wide limit per walker)"

### "Legend Rule" with Copies
- If you control two+ legendary permanents with same name, you choose one to keep, rest go to graveyard
- **Strategic Use**: Copy opponent's legendary creature, both die due to legend rule

---

## 9. State-Based Actions

### Definition
Game checks and performs these automatically (no stack, no response):

1. **Player at 0 life**: Loses the game
2. **Player draws from empty library**: Loses the game
3. **Creature with toughness ≤ 0**: Put into graveyard
4. **Creature with damage ≥ toughness**: Destroyed
5. **Creature with deathtouch damage**: Destroyed
6. **Planeswalker with 0 loyalty**: Put into graveyard
7. **Legend Rule**: If player controls 2+ legendary permanents with same name, choose one to keep
8. **Aura with illegal target**: Put into graveyard
9. **+1/+1 and -1/-1 counters on same permanent**: Cancel out in pairs

### Timing
- Checked whenever player would receive priority
- Checked after each spell/ability resolves
- **No player can respond between state-based action and its effect**

---

## 10. Layers System

### Purpose
Determines order in which continuous effects apply (critical for complex board states)

### Layer Order
1. **Copy effects**
2. **Control-changing effects**
3. **Text-changing effects**
4. **Type-changing effects**
5. **Color-changing effects**
6. **Ability-adding/removing effects**
7. **Power/Toughness effects**
   - 7a: Characteristic-defining abilities ("*/*")
   - 7b: Set power/toughness to specific value
   - 7c: Modify power/toughness (+N/+N or -N/-N)
   - 7d: Counters
   - 7e: Effects that switch power/toughness

### Example
```
Creature: 2/2
Effect 1: "Target creature becomes 0/4" (Layer 7b)
Effect 2: "Target creature gets +3/+3" (Layer 7c)
Result: 3/7 creature (0/4 set by 7b, then +3/+3 applied in 7c)

If order were reversed in timing but same layers:
Still 3/7 (layers always apply in same order regardless of timestamp)
```

---

## 11. Common Misconceptions

### Misconception 1: "I'll destroy it before it triggers"
❌ **Wrong**: "I'll destroy the creature before its enter-the-battlefield ability triggers"
✅ **Correct**: "The ability will trigger when it enters. I can respond to the trigger on the stack, but the ability will still resolve even if the creature dies."

**Example**:
```
Opponent casts creature with "When this enters, draw 2 cards"
Step 1: Creature spell resolves, enters battlefield
Step 2: ETB trigger goes on stack
You: Cast removal spell targeting creature
Result: Removal resolves first (stack order), creature dies, but trigger STILL resolves and opponent draws 2 cards
```

### Misconception 2: "I'll counter the ability"
❌ **Wrong**: "I'll use Counterspell on their creature's activated ability"
✅ **Correct**: Counterspell only counters spells on the stack, NOT abilities
✅ **Correct**: Specific cards like "Stifle" or "Tale's End" counter abilities

### Misconception 3: "Tapping prevents abilities"
❌ **Wrong**: "I'll tap their creature so it can't use its ability"
✅ **Correct**: Only abilities with {T} in cost require untapped permanent
✅ **Correct**: Abilities like "When this attacks" or "Whenever you cast a spell" work even if creature is tapped

### Misconception 4: "Indestructible prevents all removal"
❌ **Wrong**: "Indestructible creature can't be removed"
✅ **Correct**: Indestructible only prevents destruction and lethal damage
✅ **Can still remove via**: Exile effects, bounce to hand, sacrifice, -X/-X effects (toughness 0), opponents gain control

### Misconception 5: "Enchantment copying"
❌ **Wrong**: "I'll copy Extravagant Replication to get double triggers per turn"
✅ **Correct**: If you control 2 Extravagant Replications, you get 2 separate triggers at the beginning of your upkeep (choosing different targets for each)

### Misconception 6: "Instant-speed interactions during opponent's untap"
❌ **Wrong**: "During your untap step, I'll tap your creature so it doesn't untap"
✅ **Correct**: No player receives priority during untap step. You must act in opponent's upkeep (AFTER untap) or your own end step (BEFORE their untap)

---

## 12. Card Advantage Theory

### Definition
**Card Advantage**: Difference in resources (cards) between players

### Types of Card Advantage

#### Virtual Card Advantage
- Making opponent's cards irrelevant without trading cards
- **Example**: Gaining 10 life makes opponent's burn spells less relevant

#### Raw Card Advantage
- Trading 1 card for 2+ opponent cards
- **Example**: "Destroy target creature. Draw a card." (2-for-1 if it resolves)

#### Tempo vs. Card Advantage
- **Tempo**: Mana efficiency and board presence
- **Card Advantage**: Long-term resource accumulation
- **Critical Decision**: Sometimes spending 2 cards to answer 1 threat is correct if it saves you from losing

### Card Advantage Engines
- Permanents that generate ongoing card advantage
- **Examples**:
  - "At beginning of your upkeep, draw a card" (pure CA)
  - "Whenever you cast a spell, create a token" (generates value)
  - "When this enters, draw 2 cards" (immediate CA)

---

## 13. Mana Efficiency Calculations

### Rate of Damage
- **Baseline**: 1 mana = 3 damage to player (Lightning Bolt: R for 3 damage)
- **Creatures**: Typically ~1.5x mana cost in total stats for commons

### Mana Curve Optimization
- **Aggro**: Avg CMC 1.8-2.2, wants to cast 2 spells by turn 3
- **Midrange**: Avg CMC 2.5-3.5, wants card quality over speed
- **Control**: Avg CMC 3.0-4.0, wants answers for every stage of game

### Calculating "Worth It" Removal
```
Their Threat: 6 mana, 6/6 creature
Your Removal: 2 mana, "Destroy target creature"
Mana Trade: You spend 2 to answer their 6 = +4 mana advantage
Card Trade: 1-for-1 (neutral)
Result: Excellent removal trade

Their Threat: 2 mana, 2/2 creature
Your Removal: 5 mana, "Destroy target creature"
Mana Trade: You spend 5 to answer their 2 = -3 mana disadvantage
Result: Poor trade (only acceptable if 2/2 is critical engine piece)
```

---

## 14. Combo Categories

### Two-Card Combos
**Definition**: Two cards that immediately win or lock out opponent

**Example**: 
- Card A: "Whenever you gain life, deal 1 damage to each opponent"
- Card B: "Whenever opponent loses life, you gain that much life"
- Result: Infinite loop (first damage causes life gain, causes more damage, causes more life gain...)

### Engine Combos
**Definition**: Cards that synergize for exponential value (not immediate win)

**Example**:
- Extravagant Replication + Bloodthirsty Conqueror
- Each turn: Copy Conqueror, gain life from multiple Conquerors, triggers stack exponentially
- Not instant-win, but overwhelming value over 2-3 turns

### Soft Locks
**Definition**: Board state where opponent cannot win but isn't technically eliminated

**Example**:
- Continuous counterspell recursion preventing any opponent spells
- Not infinite, but effectively unbeatable

---

## 15. Critical Rules for AI Deck Building

### Interaction Timing Checklist
Before claiming a "combo" or "interaction" exists:

1. ✅ **Can both cards legally target each other?** (check targeting restrictions)
2. ✅ **Do the effects happen at compatible times?** (stack, triggers, phases)
3. ✅ **Are there costs that prevent repeated activation?** (mana, tap, sacrifice)
4. ✅ **Does the interaction actually WIN or just generate value?** (infinite vs. strong)
5. ✅ **Can opponent respond before combo assembles?** (priority, instant speed)

### Evaluation Framework
**Before suggesting card interactions**:

```
1. Read both cards' full oracle text
2. Identify trigger/activation conditions
3. Check if conditions can be met given card text
4. Verify timing (do they happen in same phase/stack?)
5. Calculate if interaction is repeatable or one-time
6. Determine if interaction wins game or just generates value
7. Assess opponent's ability to disrupt
```

### Red Flags (Likely Errors)
- Claiming "infinite" without identifying what makes it repeat
- Ignoring mana costs in combo loops
- Assuming "enters the battlefield" triggers can be prevented after resolution
- Suggesting countering abilities without specific counter-ability cards
- Claiming enchantments/artifacts "activate" when they have triggered abilities

---

## 16. Extravagant Replication - Specific Rules

### Card Text (Verified)
"At the beginning of your upkeep, create a token that's a copy of another target nonland permanent you control."

### Correct Understanding
1. **Trigger Time**: Beginning of YOUR upkeep (not every upkeep)
2. **Frequency**: Once per turn (one trigger per upkeep)
3. **Target**: Must target ANOTHER permanent (can't copy itself)
4. **Copy Rules**: Token is exact copy of permanent at time of resolution
5. **Multiple Replications**: If you control 2, you get 2 triggers (choose 2 different targets or same target for 2 copies)

### Strategic Implications
✅ **Correct**: "Extravagant Replication generates 1 copy per turn of my best permanent"
✅ **Correct**: "If I copy a creature with an ETB trigger, the token entering will trigger that ability again"
✅ **Correct**: "If I copy a planeswalker, I get 2 planeswalkers but still only 1 loyalty activation per walker per turn"
❌ **Wrong**: "Extravagant Replication creates infinite copies" (only 1 per turn)
❌ **Wrong**: "I can copy Extravagant Replication itself for exponential copies" (can't target itself - says 'another')
❌ **Wrong**: "I can activate the copy ability whenever I want" (it's a triggered ability, not activated)

---

## Document Maintenance
- **Version**: 1.0
- **Last Updated**: March 5, 2026
- **Maintained by**: Celeannora
- **Purpose**: Prevent mechanical errors in AI deck construction
- **Update Trigger**: When MTG comprehensive rules update or new mechanics introduced

---

## Quick Reference: Timing Flowchart

```
Spell Cast → Stack → Can Respond? → Resolve → Check Targets Legal?
                ↓                            ↓
              YES                          YES → Effect Happens
                ↓                            ↓
         Add to Stack                      NO → Spell Countered (fizzles)
                ↓
         Resolve in LIFO order

Permanent Enters Battlefield → ETB Triggers → Stack → Resolve
                                      ↑
                                      └── Removing permanent does NOT prevent trigger resolution

Beginning of Upkeep → All "at beginning of upkeep" triggers → Stack
                                                                  ↓
                                                         Resolve in APNAP order
                                                         (Active Player, then Non-Active Player)
```

---

**Final Directive**: When analyzing card interactions for deck building, ALWAYS:
1. Reference this document for mechanical accuracy
2. Verify trigger/activation timing
3. Check for costs that prevent infinite loops
4. Distinguish between "wins game" and "generates value"
5. Consider opponent interaction windows

**If uncertain about an interaction, state the uncertainty and explain both interpretations rather than claiming false synergies.**
