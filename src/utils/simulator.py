"""
simulator.py
------------
Headless simulation utility for the PyTabletop Engine.

Runs any `BaseGameEngine` subclass thousands of times without human
input to gather win/loss/tie probability statistics.
"""

from typing import Type

from src.engine.base_game import BaseGameEngine


def run_simulation(
    game_class: Type[BaseGameEngine],
    iterations: int = 1000,
    verbose: bool = False,
) -> dict[str, int | float]:
    """
    Simulate ``iterations`` rounds of the given game and tally results.

    The game class must implement an ``auto_play()`` method that:
      - sets the game up from scratch,
      - plays through all turns automatically, and
      - returns a result string: ``'player'``, ``'dealer'``, or ``'push'``.

    Args:
        game_class (Type[BaseGameEngine]): The game class to instantiate
            and simulate (e.g. ``BlackjackGame``).
        iterations (int): Number of rounds to simulate. Defaults to 1 000.
        verbose (bool): If ``True``, print a progress dot every 1 000 rounds.

    Returns:
        dict[str, int | float]: A dictionary containing:
            - ``'player_wins'``  : number of rounds won by the player.
            - ``'dealer_wins'``  : number of rounds won by the dealer.
            - ``'pushes'``       : number of tied rounds.
            - ``'total'``        : total rounds played.
            - ``'player_win_pct'``: player win percentage (0–100).
            - ``'dealer_win_pct'``: dealer win percentage (0–100).
            - ``'push_pct'``     : push percentage (0–100).

    Example::

        from src.games.blackjack import BlackjackGame
        from src.utils.simulator import run_simulation

        results = run_simulation(BlackjackGame, iterations=10_000)
        print(results)
    """
    counts: dict[str, int] = {"player": 0, "dealer": 0, "push": 0}
    game = game_class()

    for i in range(iterations):
        result = game.auto_play()

        # Normalise to lower-case and map unexpected values to 'push'
        outcome = result.lower().strip() if result else "push"
        if outcome not in counts:
            outcome = "push"
        counts[outcome] += 1

        if verbose and (i + 1) % 1_000 == 0:
            print(f"  … {i + 1:,} / {iterations:,} rounds simulated", flush=True)

    total = iterations
    player_wins = counts["player"]
    dealer_wins = counts["dealer"]
    pushes = counts["push"]

    def pct(n: int) -> float:
        return round(n / total * 100, 2) if total else 0.0

    return {
        "player_wins": player_wins,
        "dealer_wins": dealer_wins,
        "pushes": pushes,
        "total": total,
        "player_win_pct": pct(player_wins),
        "dealer_win_pct": pct(dealer_wins),
        "push_pct": pct(pushes),
    }


def print_simulation_report(results: dict[str, int | float], game_name: str = "Game") -> None:
    """
    Pretty-print the results dictionary returned by ``run_simulation()``.

    Args:
        results (dict): Output from ``run_simulation()``.
        game_name (str): Display name used in the report header.
    """
    total = results["total"]
    sep = "─" * 44

    print(f"\n{sep}")
    print(f"  📊  {game_name} Simulation  ({total:,} rounds)")
    print(sep)
    print(f"  Player wins  : {results['player_wins']:>7,}  ({results['player_win_pct']:>6.2f}%)")
    print(f"  Dealer wins  : {results['dealer_wins']:>7,}  ({results['dealer_win_pct']:>6.2f}%)")
    print(f"  Pushes (tie) : {results['pushes']:>7,}  ({results['push_pct']:>6.2f}%)")
    print(sep + "\n")
