"""
main.py  —  PyTabletop Engine  —  Main Menu  v1.2
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.games.blackjack    import BlackjackGame
from src.games.uno          import UnoGame
from src.games.war          import WarGame
from src.games.crazy_eights import CrazyEightsGame
from src.games.go_fish      import GoFishGame
from src.games.poker        import PokerGame
from src.utils.simulator    import run_simulation, print_simulation_report

SIM_HANDS = 10_000

BANNER = r"""
  ____        _____     _    _     _
 |  _ \ _   |_   _|_ _| |__| |___| |_ ___  _ __
 | |_) | | | || |/ _` | '_ \ / _ \ __/ _ \| '_ \
 |  __/| |_| || | (_| | |_) |  __/ || (_) | |_) |
 |_|    \__, ||_|\__,_|_.__/ \___|\__\___/| .__/
        |___/                              |_|
    ♠  ♥  Engine v1.2  —  6 Games  ♦  ♣
"""

def menu() -> None:
    print("═" * 52)
    print("  MAIN MENU")
    print("═" * 52)
    print("  [1]  ♠  Blackjack")
    print(f"  [2]  📊 Blackjack Simulation ({SIM_HANDS:,} hands)")
    print("  [3]  🃏 Uno vs CPU")
    print("  [4]  ⚔️  War vs CPU")
    print("  [5]  8️⃣  Crazy Eights vs CPU")
    print("  [6]  🐟 Go Fish vs CPU")
    print("  [7]  ♠  5-Card Draw Poker vs CPU")
    print("  [8]  Exit")
    print("═" * 52)

def loop(game_class, **kwargs) -> None:
    game = game_class(**kwargs)
    while True:
        game.play_turn()
        if input("  Play again? [Y/N]: ").strip().lower() not in ("y","yes"):
            break

def main() -> None:
    print(BANNER)
    while True:
        menu()
        c = input("\n  Your choice: ").strip()
        if   c == "1": loop(BlackjackGame)
        elif c == "2":
            print(f"\n  Running {SIM_HANDS:,} hands…")
            r = run_simulation(BlackjackGame, iterations=SIM_HANDS, verbose=True)
            print_simulation_report(r, "Blackjack")
        elif c == "3": loop(UnoGame)
        elif c == "4": loop(WarGame)
        elif c == "5": loop(CrazyEightsGame)
        elif c == "6": loop(GoFishGame)
        elif c == "7": loop(PokerGame)
        elif c == "8":
            print("\n  Thanks for playing! ♠\n")
            sys.exit(0)
        else:
            print("\n  ✗ Enter 1–8.\n")

if __name__ == "__main__":
    main()
