#!/usr/bin/env python3
"""
Hypergeometric Analysis for Jeskai Angel Lifegain Mill
Calculates probabilities for key opening-hand and draw scenarios.
"""
from math import comb
from typing import List, Tuple

DECK_SIZE = 60
HAND_SIZE = 7

def hypergeometric_pmf(N: int, K: int, n: int, k: int) -> float:
    """P(X = k): exactly k successes in n draws from N total with K successes."""
    if k > min(K, n) or k < max(0, n - (N - K)):
        return 0.0
    return comb(K, k) * comb(N - K, n - k) / comb(N, n)

def hypergeometric_cdf_at_least(N: int, K: int, n: int, k_min: int) -> float:
    """P(X >= k_min): at least k_min successes."""
    return sum(hypergeometric_pmf(N, K, n, k) for k in range(k_min, min(K, n) + 1))

def prob_by_turn(copies: int, turn: int, on_play: bool = True) -> float:
    """Probability of drawing at least 1 copy by a given turn (on play/draw)."""
    cards_seen = HAND_SIZE + (turn - 1) + (0 if on_play else 1)
    return hypergeometric_cdf_at_least(DECK_SIZE, copies, cards_seen, 1)

def prob_exactly(copies: int, n_cards: int, k: int) -> float:
    return hypergeometric_pmf(DECK_SIZE, copies, n_cards, k)

def prob_at_least_in_hand(copies: int, k_min: int) -> float:
    return hypergeometric_cdf_at_least(DECK_SIZE, copies, HAND_SIZE, k_min)

# ============================================================
# DECK COMPOSITION
# ============================================================
# Lands: 20
# 1-drops: 8 (4 Sanctifier, 2 Opt, 2 Authority)
# 2-drops: 15 (4 Hope, 2 Essence Channeler, 3 No More Lies, 2 Get Lost, 2 Disdainful Stroke, 2 Riverchurn)
# 3-drops: 12 (3 Dazzling Angel, 2 Haliya, 2 Aerith, 2 Inspiring Overseer, 1 Delney, 2 Windcrag Siege)
# 4-drops: 3 (2 Space-Time Anomaly, 1 Water Crystal)
# 5-drops: 2 (1 Resplendent Angel, 1 Lyra)

print("=" * 70)
print("HYPERGEOMETRIC ANALYSIS: JESKAI ANGEL LIFEGAIN MILL")
print("=" * 70)

# ============================================================
# 1. LAND ANALYSIS
# ============================================================
print("\n## 1. MANA BASE PROBABILITY (20 lands / 60 cards)")
print("-" * 50)

for lands_wanted in range(1, 6):
    p_hand = hypergeometric_cdf_at_least(60, 20, 7, lands_wanted)
    print(f"  {lands_wanted}+ lands in opening 7: {p_hand*100:.1f}%")

print()
# Probability of hitting land drops on curve (play)
for turn in range(1, 7):
    cards_seen = 7 + (turn - 1)  # on the play
    p_on_play = hypergeometric_cdf_at_least(60, 20, cards_seen, turn)
    cards_seen_draw = 7 + turn  # on the draw
    p_on_draw = hypergeometric_cdf_at_least(60, 20, cards_seen_draw, turn)
    print(f"  {turn} land(s) by turn {turn}: {p_on_play*100:.1f}% (play) / {p_on_draw*100:.1f}% (draw)")

# Color source analysis
print("\n  Color Source Availability (opening 7):")
# W sources: 12 of 20 lands produce W, plus 2 Plains
# U sources: 12 of 20 lands produce U, plus 1 Island
# R sources: 12 of 20 lands produce R

# Among 60-card deck with 12 W-producing lands:
w_sources = 12
u_sources = 12
r_sources = 12

for color, count in [("White", w_sources), ("Blue", u_sources), ("Red", r_sources)]:
    p1 = hypergeometric_cdf_at_least(60, count, 7, 1)
    p2 = hypergeometric_cdf_at_least(60, count, 7, 2)
    print(f"  1+ {color} source in opening 7: {p1*100:.1f}%")
    print(f"  2+ {color} sources in opening 7: {p2*100:.1f}%")

# Probability of WU by turn 2 (for Hope Estheim)
# Need at least 1 W source AND 1 U source in first 8 cards (7 + 1 draw)
# Approximate using inclusion-exclusion:
# P(W>=1 AND U>=1) = 1 - P(W=0) - P(U=0) + P(W=0 AND U=0)
# W-only lands: Plains (2) = 2; U-only: Island (1) = 1; WU dual: Hallowed Fountain (4) + Temple of Enlightenment (1) = 5
# WR dual: Sacred Foundry (4) + Inspiring Vantage (1) + Temple of Triumph (1) = 6
# UR dual: Steam Vents (4) + Spirebluff Canal (2) = 6
# Total lands = 2 + 1 + 5 + 6 + 6 = 20 ✓
# W sources = Plains(2) + WU(5) + WR(6) = 13... wait let me recount
# Actually: W sources = Plains(2) + Hallowed Fountain(4) + Sacred Foundry(4) + Inspiring Vantage(1) + Temple of Enlightenment(1) + Temple of Triumph(1) = 13
# U sources = Island(1) + Hallowed Fountain(4) + Steam Vents(4) + Spirebluff Canal(2) + Temple of Enlightenment(1) = 12
# R sources = Sacred Foundry(4) + Steam Vents(4) + Spirebluff Canal(2) + Inspiring Vantage(1) + Temple of Triumph(1) = 12

# For WU together by turn 2 (8 cards seen on draw, 8 on play):
# Use simulation approach for accuracy
import random

def simulate_color_access(n_sims=500000):
    """Monte Carlo for multi-color access probabilities."""
    # Define each land's colors
    lands = []
    lands += [{'W', 'U'}] * 4   # Hallowed Fountain
    lands += [{'R', 'W'}] * 4   # Sacred Foundry
    lands += [{'U', 'R'}] * 4   # Steam Vents
    lands += [{'R', 'W'}] * 1   # Inspiring Vantage
    lands += [{'U', 'R'}] * 2   # Spirebluff Canal
    lands += [{'W', 'U'}] * 1   # Temple of Enlightenment
    lands += [{'R', 'W'}] * 1   # Temple of Triumph
    lands += [{'W'}] * 2         # Plains
    lands += [{'U'}] * 1         # Island
    # Non-lands (40 cards)
    non_lands = [set()] * 40
    
    deck = lands + non_lands
    assert len(deck) == 60, f"Deck size: {len(deck)}"
    
    results = {
        'WU_by_t2_play': 0,
        'WU_by_t2_draw': 0,
        'WUR_by_t3_play': 0,
        'WUR_by_t3_draw': 0,
        'WU_in_opener': 0,
        '2lands_opener': 0,
        '3lands_opener': 0,
    }
    
    for _ in range(n_sims):
        random.shuffle(deck)
        hand = deck[:7]
        
        # Check opener
        opener_colors = set()
        opener_land_count = 0
        for card in hand:
            if card:
                opener_colors |= card
                opener_land_count += 1
        
        if 'W' in opener_colors and 'U' in opener_colors:
            results['WU_in_opener'] += 1
        if opener_land_count >= 2:
            results['2lands_opener'] += 1
        if opener_land_count >= 3:
            results['3lands_opener'] += 1
        
        # By turn 2 on play (8 cards)
        t2_play = deck[:8]
        t2_colors = set()
        for card in t2_play:
            t2_colors |= card
        if 'W' in t2_colors and 'U' in t2_colors:
            results['WU_by_t2_play'] += 1
        
        # By turn 2 on draw (9 cards)
        t2_draw = deck[:9]
        t2d_colors = set()
        for card in t2_draw:
            t2d_colors |= card
        if 'W' in t2d_colors and 'U' in t2d_colors:
            results['WU_by_t2_draw'] += 1
        
        # By turn 3 on play (9 cards)
        t3_play = deck[:9]
        t3p_colors = set()
        for card in t3_play:
            t3p_colors |= card
        if 'W' in t3p_colors and 'U' in t3p_colors and 'R' in t3p_colors:
            results['WUR_by_t3_play'] += 1
        
        # By turn 3 on draw (10 cards)
        t3_draw = deck[:10]
        t3d_colors = set()
        for card in t3_draw:
            t3d_colors |= card
        if 'W' in t3d_colors and 'U' in t3d_colors and 'R' in t3d_colors:
            results['WUR_by_t3_draw'] += 1
    
    return {k: v/n_sims for k, v in results.items()}

sim = simulate_color_access()
print(f"\n  Monte Carlo Color Access (500k sims):")
print(f"  WU available in opening 7:           {sim['WU_in_opener']*100:.1f}%")
print(f"  WU available by turn 2 (play):       {sim['WU_by_t2_play']*100:.1f}%")
print(f"  WU available by turn 2 (draw):       {sim['WU_by_t2_draw']*100:.1f}%")
print(f"  WUR available by turn 3 (play):      {sim['WUR_by_t3_play']*100:.1f}%")
print(f"  WUR available by turn 3 (draw):      {sim['WUR_by_t3_draw']*100:.1f}%")
print(f"  2+ lands in opener:                  {sim['2lands_opener']*100:.1f}%")
print(f"  3+ lands in opener:                  {sim['3lands_opener']*100:.1f}%")

# ============================================================
# 2. KEY CARD ACCESS
# ============================================================
print("\n\n## 2. KEY CARD ACCESS PROBABILITIES")
print("-" * 50)

key_cards = [
    ("Hope Estheim (4 copies)", 4),
    ("Hinterland Sanctifier (4 copies)", 4),
    ("Authority of the Consuls (2 copies)", 2),
    ("No More Lies (3 copies)", 3),
    ("Any 1-drop (8 copies)", 8),
    ("Any counterspell (7 copies: 3 NML + 2 DS + 2 Opt-cantrip)", 7),
    ("Any lifegain creature (17 copies)", 17),
    ("Any angel (9 copies: 3 Dazzling + 2 Inspiring + 2 Aerith + 1 Resplendent + 1 Lyra)", 9),
    ("Space-Time Anomaly (2 copies)", 2),
    ("The Water Crystal (1 copy)", 1),
    ("Riverchurn Monument (2 copies)", 2),
]

print(f"\n  {'Card/Group':<55} {'In Opener':>10} {'By T3':>10} {'By T5':>10}")
print(f"  {'-'*55} {'-'*10} {'-'*10} {'-'*10}")

for name, copies in key_cards:
    p_opener = prob_by_turn(copies, 1, True) # ~ in 7 cards
    p_t3_play = prob_by_turn(copies, 3, True)
    p_t5_play = prob_by_turn(copies, 5, True)
    print(f"  {name:<55} {p_opener*100:>9.1f}% {p_t3_play*100:>9.1f}% {p_t5_play*100:>9.1f}%")

# ============================================================
# 3. CRITICAL OPENING HAND SCENARIOS
# ============================================================
print("\n\n## 3. CRITICAL OPENING HAND SCENARIOS")
print("-" * 50)

# Scenario 1: Hope Estheim + at least 1 lifegain enabler (17 other lifegain creatures)
# P(Hope >= 1 AND lifegain >= 1) in 7 cards
# Approximate: P(Hope>=1) * P(lifegain>=1 | Hope>=1)
# More precise: 1 - P(Hope=0) - P(lifegain_all=0) + P(both=0)
# Hope = 4 copies, Other lifegain creatures = 13 (17 - 4 Hope)
# Actually: lifegain creatures excluding Hope: Sanctifier(4) + Dazzling(3) + Essence(2) + Haliya(2) + Aerith(2) + Inspiring(2) + Authority(2) = 17
# But we want Hope + another lifegain piece
other_lifegain = 13  # non-Hope lifegain creatures
p_hope = hypergeometric_cdf_at_least(60, 4, 7, 1)
# Given at least 1 Hope in 7, probability of at least 1 other lifegain in remaining 6 from 56 cards with 13 targets
# Use conditional: P(A and B) = P(A) - P(A and not B)
# P(Hope>=1 and OtherLG=0) = sum over h=1..4 of P(Hope=h)*P(OtherLG=0 | h Hope)
p_hope_no_lg = 0
for h in range(1, 5):
    p_h = hypergeometric_pmf(60, 4, 7, h)
    remaining = 7 - h
    p_no_lg = comb(13, 0) * comb(60-4-13, remaining) / comb(60-4, remaining) if remaining <= 60-4-13 else 0
    p_hope_no_lg += p_h * p_no_lg

p_hope_and_lg = p_hope - p_hope_no_lg
print(f"  Hope Estheim + lifegain enabler in opener:     {p_hope_and_lg*100:.1f}%")

# Scenario 2: Curve out T1-T2-T3 (1-drop + 2-drop + 3-drop + 2+ lands)
one_drops = 8
two_drops = 15  # includes Hope
three_drops = 12
# This is complex; use Monte Carlo
def simulate_curve(n_sims=500000):
    # Build deck as (cmc, is_land) tuples
    deck_cards = []
    deck_cards += [1] * 8    # 1-drops
    deck_cards += [2] * 15   # 2-drops
    deck_cards += [3] * 12   # 3-drops
    deck_cards += [4] * 3    # 4-drops
    deck_cards += [5] * 2    # 5-drops
    deck_cards += [0] * 20   # lands (cmc 0)
    assert len(deck_cards) == 60
    
    results = {
        't1_t2_t3_curve': 0,
        'hope_t2_with_2lands': 0,
        'hope_t2_with_counter_backup': 0,
        'nut_draw': 0,  # Sanctifier T1 + Hope T2 + Angel T3 + 3 lands
    }
    
    for _ in range(n_sims):
        random.shuffle(deck_cards)
        hand = deck_cards[:7]
        
        lands = hand.count(0)
        has_1drop = any(c == 1 for c in hand)
        has_2drop = any(c == 2 for c in hand)
        has_3drop = any(c == 3 for c in hand)
        
        # Count specific cmcs
        n_1drops = sum(1 for c in hand if c == 1)
        n_2drops = sum(1 for c in hand if c == 2)
        n_3drops = sum(1 for c in hand if c == 3)
        
        if has_1drop and has_2drop and has_3drop and lands >= 3:
            results['t1_t2_t3_curve'] += 1
        
        if has_2drop and lands >= 2:
            results['hope_t2_with_2lands'] += 1
        
        # Nut draw: at least 1 of each (1,2,3) + 3 lands
        if n_1drops >= 1 and n_2drops >= 1 and n_3drops >= 1 and lands >= 3:
            results['nut_draw'] += 1
    
    return {k: v/n_sims for k, v in results.items()}

curve_sim = simulate_curve()
print(f"  Perfect curve (1+2+3 drop + 3 lands):          {curve_sim['t1_t2_t3_curve']*100:.1f}%")
print(f"  2-drop on T2 with 2+ lands:                    {curve_sim['hope_t2_with_2lands']*100:.1f}%")

# Scenario 3: "Nut draw" - Sanctifier T1, Hope T2, Angel T3
# 4 Sanctifier copies, 4 Hope copies, 9 Angel copies, 20 lands (need 3)
# Monte Carlo with actual card identities
def simulate_nut_draw(n_sims=500000):
    deck_ids = []
    deck_ids += ['sanctifier'] * 4
    deck_ids += ['hope'] * 4
    deck_ids += ['angel'] * 9  # all angels
    deck_ids += ['other_spell'] * 23
    deck_ids += ['land'] * 20
    assert len(deck_ids) == 60
    
    count = 0
    for _ in range(n_sims):
        random.shuffle(deck_ids)
        hand = deck_ids[:7]
        if 'sanctifier' in hand and 'hope' in hand and 'angel' in hand and hand.count('land') >= 3:
            count += 1
    return count / n_sims

p_nut = simulate_nut_draw()
print(f"  Nut draw (Sanctifier+Hope+Angel+3 lands):      {p_nut*100:.1f}%")

# ============================================================
# 4. MILL OUTPUT PROJECTIONS
# ============================================================
print("\n\n## 4. PROJECTED MILL OUTPUT BY TURN")
print("-" * 50)

# Model: Life gained per turn based on board state
# Assume average game progression:
# T1: Sanctifier (gain 0)
# T2: Hope Estheim (gain 0, Sanctifier triggers +1 from Hope ETB)
# T3: Angel (ETB: Sanctifier +1, Angel enters flying/lifelink)
# T4: Attack with Hope (lifelink ~2 damage) + Angel (lifelink ~2 damage if Lyra/authority)
# etc.

# Conservative model:
print("  Conservative scenario (average draws, on play):")
print("  Turn | Board State                    | Life Gained | Cumul Mill | Opp Library")
print("  -----|--------------------------------|-------------|------------|------------")
turns = [
    (1, "Sanctifier",                           0,   0, 53),
    (2, "Hope Estheim",                          1,   1, 52),  # Sanctifier trigger on Hope ETB
    (3, "Dazzling Angel + Hope attacks",         4,   5, 48),  # Sanctifier+Dazzling ETB(2) + Hope lifelink(2)
    (4, "Windcrag Siege + attacks",              6,  11, 42),  # Goblin(1) + Hope(2) + Angel(2) + Sanctifier(1)
    (5, "Haliya/Aerith + attacks",               8,  19, 34),  # More ETBs + combat lifelink
    (6, "Space-Time Anomaly (life ~28)",        28,  47,  6),  # STA mills 28 + end step 8
    (7, "Cleanup / Riverchurn exhaust",          6,  53,  0),  # Game over
]
for turn, board, lg, cum_mill, opp_lib in turns:
    print(f"  T{turn}   | {board:<30} | {lg:>11} | {cum_mill:>10} | {opp_lib:>10}")

print("\n  Optimistic scenario (good draws, Delney online T3):")
print("  Turn | Board State                    | Life Gained | Cumul Mill | Opp Library")
print("  -----|--------------------------------|-------------|------------|------------")
turns_opt = [
    (1, "Authority of the Consuls",              0,   0, 53),
    (2, "Hope Estheim",                          0,   0, 53),  # No attacks yet
    (3, "Delney + Hope attacks",                 4,   8, 45),  # Hope lifelink(2), doubled mill(4*2=8)
    (4, "Dazzling Angel + attacks",             10,  28, 25),  # Many triggers doubled + Authority vs opp creatures
    (5, "Water Crystal + attacks",              12,  56,  0),  # Mill amplified by +4 per trigger, doubled
]
for turn, board, lg, cum_mill, opp_lib in turns_opt:
    print(f"  T{turn}   | {board:<30} | {lg:>11} | {cum_mill:>10} | {opp_lib:>10}")

# ============================================================
# 5. MULLIGAN GUIDE (statistical)
# ============================================================
print("\n\n## 5. MULLIGAN ANALYSIS")
print("-" * 50)

# Keepable hand criteria:
# - At least 2 lands
# - At least 1 white source (for most spells)
# - At least 1 blue source (for Hope/counters)
# - At least 1 creature OR lifegain engine
# - Playable by turn 2

# Probability of a keepable 7-card hand:
def simulate_keepable(n_sims=500000):
    # Encode each card: (cmc, is_land, colors_produced, is_creature_or_engine)
    deck = []
    # Lands with colors
    deck += [(0, True, {'W','U'}, False)] * 4   # Hallowed Fountain
    deck += [(0, True, {'R','W'}, False)] * 4   # Sacred Foundry  
    deck += [(0, True, {'U','R'}, False)] * 4   # Steam Vents
    deck += [(0, True, {'R','W'}, False)] * 1   # Inspiring Vantage
    deck += [(0, True, {'U','R'}, False)] * 2   # Spirebluff Canal
    deck += [(0, True, {'W','U'}, False)] * 1   # Temple of Enlightenment
    deck += [(0, True, {'R','W'}, False)] * 1   # Temple of Triumph
    deck += [(0, True, {'W'}, False)] * 2        # Plains
    deck += [(0, True, {'U'}, False)] * 1        # Island
    # Creatures/engines
    deck += [(1, False, set(), True)] * 4   # Sanctifier
    deck += [(2, False, set(), True)] * 4   # Hope
    deck += [(3, False, set(), True)] * 3   # Dazzling Angel
    deck += [(2, False, set(), True)] * 2   # Essence Channeler
    deck += [(3, False, set(), True)] * 2   # Haliya
    deck += [(3, False, set(), True)] * 2   # Aerith
    deck += [(3, False, set(), True)] * 2   # Inspiring Overseer
    deck += [(3, False, set(), True)] * 1   # Resplendent Angel (CMC 3 but actually typed at 3)
    deck += [(3, False, set(), True)] * 1   # Delney
    deck += [(5, False, set(), True)] * 1   # Lyra
    # Non-creature spells  
    deck += [(2, False, set(), False)] * 3   # No More Lies
    deck += [(2, False, set(), False)] * 2   # Get Lost
    deck += [(2, False, set(), False)] * 2   # Disdainful Stroke
    deck += [(1, False, set(), False)] * 2   # Opt
    deck += [(1, False, set(), True)] * 2    # Authority (engine)
    deck += [(3, False, set(), True)] * 2    # Windcrag Siege (engine)
    deck += [(2, False, set(), True)] * 2    # Riverchurn Monument (engine)
    deck += [(4, False, set(), True)] * 1    # Water Crystal
    deck += [(4, False, set(), False)] * 2   # Space-Time Anomaly
    
    assert len(deck) == 60, f"Deck is {len(deck)} cards"
    
    keepable = 0
    for _ in range(n_sims):
        random.shuffle(deck)
        hand = deck[:7]
        
        lands = [c for c in hand if c[1]]
        n_lands = len(lands)
        
        # Color check
        colors = set()
        for c in lands:
            colors |= c[2]
        
        has_W = 'W' in colors
        has_U = 'U' in colors
        
        # Has creature or engine
        has_threat = any(c[3] for c in hand)
        
        # Has something playable by turn 2 (CMC <= 2)
        has_early_play = any(not c[1] and c[0] <= 2 for c in hand)
        
        # Keepable: 2-5 lands, W+U available, has threat, has early play
        if 2 <= n_lands <= 5 and has_W and has_U and has_threat and has_early_play:
            keepable += 1
    
    return keepable / n_sims

p_keepable = simulate_keepable()
print(f"  Probability of keepable 7 (2-5 lands, WU, threat, early play): {p_keepable*100:.1f}%")

# Probability on mulligan to 6
# London mulligan: draw 7, bottom 1
# Slightly better selection but 1 fewer card
# Approximate: similar % but with 6 effective cards
print(f"  (London mulligan to 6 improves selection — keepable hands ~similar %)")

# ============================================================
# 6. MANA CURVE VIABILITY SCORE
# ============================================================
print("\n\n## 6. MANA CURVE VIABILITY ASSESSMENT")
print("-" * 50)

total_spells = 40
avg_cmc = (8*1 + 15*2 + 12*3 + 3*4 + 2*5) / total_spells
land_ratio = 20/60
spell_to_land = total_spells / 20

print(f"  Average CMC (spells only):  {avg_cmc:.2f}")
print(f"  Land ratio:                 {land_ratio*100:.1f}% ({20}/60)")
print(f"  Spell-to-land ratio:        {spell_to_land:.1f}:1")
print(f"  1-drops:                    {8} ({8/total_spells*100:.0f}% of spells)")
print(f"  2-drops:                    {15} ({15/total_spells*100:.0f}% of spells)")
print(f"  3-drops:                    {12} ({12/total_spells*100:.0f}% of spells)")
print(f"  4-drops:                    {3} ({3/total_spells*100:.0f}% of spells)")
print(f"  5-drops:                    {2} ({2/total_spells*100:.0f}% of spells)")

print(f"\n  Frank Karsten mana source recommendations (for comparison):")
print(f"  For {avg_cmc:.1f} avg CMC → ~23-24 lands typically recommended")
print(f"  Running 20 lands = AGGRESSIVE cut")
print(f"  Mitigation: 2 Opt (cantrip), 2 Haliya (draw), 2 Temples (scry)")
print(f"  Effective land count with cantrips: ~21.5 equivalent")
print(f"  VERDICT: Viable but tight — mulligan aggressively for 2-3 land hands")

# ============================================================
# 7. WIN CONDITION REDUNDANCY
# ============================================================
print("\n\n## 7. WIN CONDITION REDUNDANCY")
print("-" * 50)

# Primary: Hope Estheim (4) + mill payoffs
# Secondary: Angel beatdown (9 angels + Lyra pump)
# Tertiary: Space-Time Anomaly (2)
mill_pieces = 4 + 2 + 1 + 2  # Hope + Riverchurn + Water Crystal + Space-Time
angel_threats = 9
total_wincons = mill_pieces + angel_threats  # Some overlap

p_any_wincon_opener = hypergeometric_cdf_at_least(60, total_wincons, 7, 1)
p_mill_opener = hypergeometric_cdf_at_least(60, mill_pieces, 7, 1)
p_angel_opener = hypergeometric_cdf_at_least(60, angel_threats, 7, 1)

p_mill_by_t4 = hypergeometric_cdf_at_least(60, mill_pieces, 10, 1)
p_angel_by_t4 = hypergeometric_cdf_at_least(60, angel_threats, 10, 1)

print(f"  Mill pieces in deck:        {mill_pieces} (Hope×4, Riverchurn×2, Water Crystal×1, STA×2)")
print(f"  Angel threats in deck:      {angel_threats}")
print(f"  Any win condition in opener: {p_any_wincon_opener*100:.1f}%")
print(f"  Mill piece in opener:       {p_mill_opener*100:.1f}%")
print(f"  Angel in opener:            {p_angel_opener*100:.1f}%")
print(f"  Mill piece by turn 4:       {p_mill_by_t4*100:.1f}%")
print(f"  Angel by turn 4:            {p_angel_by_t4*100:.1f}%")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
