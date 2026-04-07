#!/usr/bin/env python3
"""
Goldfish Simulator — Opening hand and curve execution analysis.

Simulates N random opening hands from a decklist.txt and models
greedy curve execution (play lands, cast highest-CMC affordable spell each turn).

Outputs:
  - Land drought/flood probability
  - Key card access probability by turn (for focus cards)
  - Average CMC of spells cast by turn N
  - Perfect curve (1+2+3+4-drop) probability

Usage:
  python scripts/goldfish.py Decks/my_deck/decklist.txt
  python scripts/goldfish.py Decks/my_deck/decklist.txt --hands 2000 --turns 6
  python scripts/goldfish.py Decks/my_deck/decklist.txt --focus "Sheoldred" "Hope Estheim"
"""

import argparse
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mtg_utils import RepoPaths, parse_decklist


def load_decklist(path: Path) -> list[dict]:
    """Returns list of card dicts with name, cmc, is_land, qty."""
    content = path.read_text(encoding="utf-8")
    cards = []
    in_deck = False
    for line in content.splitlines():
        line = line.strip()
        if line.lower() == "deck":
            in_deck = True
            continue
        if line.lower() == "sideboard":
            break
        if not in_deck or not line:
            continue
        # Format: "4 Card Name (SET) 123"
        parts = line.split()
        if not parts[0].isdigit():
            continue
        qty = int(parts[0])
        # Strip set/collector from name
        name_parts = []
        for part in parts[1:]:
            if part.startswith("("):
                break
            name_parts.append(part)
        name = " ".join(name_parts)
        cards.append({"name": name, "qty": qty})
    return cards


def load_card_data(card_names: list[str], paths: RepoPaths) -> dict[str, dict]:
    """Look up cmc and type_line from local DB."""
    import csv
    target = {n.lower(): n for n in card_names}
    found = {}
    from search_cards import CARD_TYPES
    for card_type in CARD_TYPES:
        type_dir = paths.cards_dir / card_type
        if not type_dir.exists():
            continue
        for csv_file in sorted(type_dir.glob("*.csv")):
            try:
                with open(csv_file, encoding="utf-8") as f:
                    for row in csv.DictReader(f):
                        name_lower = row.get("name", "").lower()
                        if name_lower in target and name_lower not in found:
                            found[name_lower] = row
                            if len(found) == len(target):
                                return found
            except Exception:
                continue
    return found


def build_deck(decklist: list[dict], card_data: dict[str, dict]) -> list[dict]:
    """Expand decklist to individual cards with cmc and is_land."""
    deck = []
    for entry in decklist:
        name = entry["name"]
        qty = entry["qty"]
        data = card_data.get(name.lower(), {})
        cmc = float(data.get("cmc") or 0)
        type_line = (data.get("type_line") or "").lower()
        is_land = "land" in type_line and "spell" not in type_line
        for _ in range(qty):
            deck.append({"name": name, "cmc": cmc, "is_land": is_land})
    return deck


def simulate_goldfish(
    deck: list[dict],
    n_hands: int,
    n_turns: int,
    focus_cards: list[str],
) -> dict:
    """Main simulation loop."""
    focus_lower = {f.lower() for f in focus_cards}

    results = {
        "land_counts": Counter(),           # opener land count → frequency
        "mulligans": 0,
        "focus_seen_by_turn": defaultdict(int),  # turn → count
        "avg_cmc_cast_by_turn": defaultdict(list),
        "lands_played_by_turn": defaultdict(list),
        "on_curve_counts": Counter(),        # number of consecutive curve turns
        "total_hands": n_hands,
    }

    for _ in range(n_hands):
        shuffled = deck[:]
        random.shuffle(shuffled)
        hand = shuffled[:7]
        library = shuffled[7:]

        land_count = sum(1 for c in hand if c["is_land"])
        results["land_counts"][land_count] += 1

        # Simple mulligan: if 0 or 1 lands or 6+ lands, note it
        if land_count <= 1 or land_count >= 6:
            results["mulligans"] += 1

        # Track focus cards seen
        seen_focus = set()
        for card in hand:
            if card["name"].lower() in focus_lower:
                seen_focus.add(card["name"].lower())

        # Simulate turns
        mana_available = 0
        graveyard = []
        on_curve_turns = 0

        for turn in range(1, n_turns + 1):
            # Draw
            if library:
                drawn = library.pop(0)
                hand.append(drawn)

            # Check focus
            for card in hand:
                if card["name"].lower() in focus_lower and card["name"].lower() not in seen_focus:
                    seen_focus.add(card["name"].lower())
                    results["focus_seen_by_turn"][turn] += 1

            # Play a land
            land_to_play = next((c for c in hand if c["is_land"]), None)
            if land_to_play:
                hand.remove(land_to_play)
                mana_available += 1

            results["lands_played_by_turn"][turn].append(mana_available)

            # Cast highest affordable spell (greedy)
            castable = [c for c in hand if not c["is_land"] and c["cmc"] <= mana_available and c["cmc"] > 0]
            if castable:
                best = max(castable, key=lambda c: c["cmc"])
                hand.remove(best)
                mana_available -= int(best["cmc"])
                results["avg_cmc_cast_by_turn"][turn].append(best["cmc"])
                if best["cmc"] >= turn:
                    on_curve_turns += 1
            else:
                results["avg_cmc_cast_by_turn"][turn].append(0)

        results["on_curve_counts"][on_curve_turns] += 1

        # Record focus cards seen in opener
        for card in hand:
            if card["name"].lower() in focus_lower and card["name"].lower() not in seen_focus:
                results["focus_seen_by_turn"][0] += 1

    return results


def print_report(results: dict, n_turns: int, focus_cards: list[str], decklist: list[dict]):
    N = results["total_hands"]
    print(f"\n{'='*65}")
    print(f"  GOLDFISH SIMULATOR — {N:,} hands, {n_turns} turns")
    print(f"{'='*65}\n")

    # Land distribution
    print("── OPENING HAND LAND DISTRIBUTION ──────────────────────────────")
    print(f"  {'Lands':<8} {'Frequency':>10} {'%':>7}  {'Rating':>12}")
    print(f"  {'-'*8} {'-'*10} {'-'*7}  {'-'*12}")
    ratings = {0: "SCOOP 🚫", 1: "Very Weak ⚠️", 2: "Keepable ✅", 3: "Good ✅",
               4: "Good ✅", 5: "Flood Risk ⚠️", 6: "Flood ⚠️", 7: "Mulligan 🚫"}
    for lands in range(8):
        count = results["land_counts"].get(lands, 0)
        pct = count / N * 100
        rating = ratings.get(lands, "")
        print(f"  {lands:<8} {count:>10,} {pct:>6.1f}%  {rating}")

    mull_rate = results["mulligans"] / N * 100
    keep_rate = 100 - mull_rate
    print(f"\n  Keeper rate (2-5 lands): {keep_rate:.1f}%")
    print(f"  Mulligan candidates:     {mull_rate:.1f}%\n")

    # Curve execution
    print("── AVERAGE CURVE EXECUTION ──────────────────────────────────────")
    print(f"  {'Turn':<6} {'Avg CMC Cast':>13} {'Avg Lands':>11}")
    print(f"  {'-'*6} {'-'*13} {'-'*11}")
    for turn in range(1, n_turns + 1):
        cmcs = results["avg_cmc_cast_by_turn"].get(turn, [0])
        avg_cmc = sum(cmcs) / len(cmcs) if cmcs else 0
        lands = results["lands_played_by_turn"].get(turn, [0])
        avg_lands = sum(lands) / len(lands) if lands else 0
        print(f"  T{turn:<5} {avg_cmc:>12.2f}  {avg_lands:>10.2f}")

    print()

    # Perfect curve probability
    print("── ON-CURVE PROBABILITY ─────────────────────────────────────────")
    total_on_curve = sum(count for turns, count in results["on_curve_counts"].items() if turns >= 3)
    p_three_curve = total_on_curve / N * 100
    total_perfect = sum(count for turns, count in results["on_curve_counts"].items() if turns >= n_turns - 1)
    p_perfect = total_perfect / N * 100
    print(f"  3+ on-curve turns: {p_three_curve:.1f}%")
    print(f"  {n_turns-1}+ on-curve turns: {p_perfect:.1f}%")
    print()

    # Focus card access
    if focus_cards:
        print("── FOCUS CARD ACCESS ────────────────────────────────────────────")
        cumulative = 0
        print(f"  Card(s): {', '.join(focus_cards)}")
        print(f"  {'By Turn':<12} {'New Sightings':>14} {'Cumulative %':>13}")
        print(f"  {'-'*12} {'-'*14} {'-'*13}")
        print(f"  {'In opener':<12} {results['focus_seen_by_turn'].get(0, 0):>14,} {results['focus_seen_by_turn'].get(0, 0)/N*100:>12.1f}%")
        for turn in range(1, n_turns + 1):
            new = results["focus_seen_by_turn"].get(turn, 0)
            cumulative += new
            print(f"  {'T'+str(turn):<12} {new:>14,} {cumulative/N*100:>12.1f}%")
        print()

    print(f"{'='*65}\n")


def main():
    p = argparse.ArgumentParser(
        description="Goldfish hand simulator for MTG decklists.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("decklist", help="Path to decklist.txt")
    p.add_argument("--hands", type=int, default=1000, help="Number of hands to simulate (default 1000)")
    p.add_argument("--turns", type=int, default=5, help="Turns to simulate (default 5)")
    p.add_argument("--focus", nargs="*", default=[], help="Focus card name(s) to track")
    args = p.parse_args()

    deck_path = Path(args.decklist)
    if not deck_path.exists():
        print(f"ERROR: {deck_path} not found.", file=sys.stderr)
        sys.exit(1)

    decklist = load_decklist(deck_path)
    card_names = [e["name"] for e in decklist]

    print(f"Looking up card data...", file=sys.stderr)
    paths = RepoPaths()
    card_data = load_card_data(card_names, paths)

    not_found = [n for n in card_names if n.lower() not in card_data]
    if not_found:
        print(f"  Not found in DB (will treat as CMC 3 spell): {', '.join(not_found[:5])}", file=sys.stderr)
        for n in not_found:
            card_data[n.lower()] = {"cmc": "3", "type_line": "Spell"}

    deck = build_deck(decklist, card_data)
    print(f"Simulating {args.hands:,} hands ({len(deck)}-card deck)...", file=sys.stderr)

    results = simulate_goldfish(deck, args.hands, args.turns, args.focus)
    print_report(results, args.turns, args.focus, decklist)


if __name__ == "__main__":
    main()
