"""
simulator.py
------------
Headless simulation utility for the PyTabletop Engine.
"""

from typing import Type
from src.engine.base_game import BaseGameEngine


def run_simulation(
    game_class: Type[BaseGameEngine],
    iterations: int = 1000,
    verbose: bool = False,
) -> dict:
    counts = {"player": 0, "dealer": 0, "push": 0}
    game = game_class()

    for i in range(iterations):
        result = game.auto_play()
        outcome = (result or "push").lower().strip()
        if outcome not in counts:
            outcome = "push"
        counts[outcome] += 1

        if verbose and (i + 1) % 1_000 == 0:
            print(f"  … {i+1:,} / {iterations:,} rounds simulated", flush=True)

    total       = iterations
    player_wins = counts["player"]
    dealer_wins = counts["dealer"]
    pushes      = counts["push"]

    def pct(n): return round(n / total * 100, 2) if total else 0.0

    return {
        "player_wins":    player_wins,
        "dealer_wins":    dealer_wins,
        "pushes":         pushes,
        "total":          total,
        "player_win_pct": pct(player_wins),
        "dealer_win_pct": pct(dealer_wins),
        "push_pct":       pct(pushes),
    }


def print_simulation_report(results: dict, game_name: str = "Game") -> None:
    total = results["total"]
    sep   = "─" * 44
    print(f"\n{sep}")
    print(f"  📊  {game_name} Simulation  ({total:,} rounds)")
    print(sep)
    print(f"  Player wins  : {results['player_wins']:>7,}  ({results['player_win_pct']:>6.2f}%)")
    print(f"  Dealer wins  : {results['dealer_wins']:>7,}  ({results['dealer_win_pct']:>6.2f}%)")
    print(f"  Pushes (tie) : {results['pushes']:>7,}  ({results['push_pct']:>6.2f}%)")
    print(sep + "\n")
