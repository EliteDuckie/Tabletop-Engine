# 🃏 PyTabletop Engine

A modular, object-oriented tabletop game engine in Python. Built around abstract base classes so every new game snaps in without touching the core engine.

---

## Project Structure

```
pytabletop/
├── main.py              ← Entry point / terminal menu
├── clean.py             ← Removes __pycache__ and temp files
├── README.md
└── src/
    ├── engine/          ← Abstract base classes (the core)
    │   ├── card.py          BaseCard
    │   ├── deck.py          BaseDeck
    │   └── base_game.py     BaseGameEngine
    ├── games/           ← Concrete game implementations
    │   ├── blackjack.py     Blackjack (interactive + simulation)
    │   ├── uno.py           Uno vs CPU (all action cards)
    │   ├── war.py           War vs CPU
    │   ├── crazy_eights.py  Crazy Eights vs CPU
    │   ├── go_fish.py       Go Fish vs CPU
    │   └── poker.py         5-Card Draw Poker vs CPU (with betting)
    └── utils/
        └── simulator.py     Headless simulation engine
```

---

## Requirements

- Python **3.10+**
- No third-party packages — pure standard library

---

## Running

```bash
python main.py
```

```
  [1]  ♠  Blackjack
  [2]  📊 Blackjack Simulation (10,000 hands)
  [3]  🃏 Uno vs CPU
  [4]  ⚔️  War vs CPU
  [5]  8️⃣  Crazy Eights vs CPU
  [6]  🐟 Go Fish vs CPU
  [7]  ♠  5-Card Draw Poker vs CPU
  [8]  Exit
```

---

## Games

### ♠ Blackjack
You vs dealer. `H` to hit, `S` to stand. Aces auto-adjust. Dealer hits to 17.

### 🃏 Uno vs CPU
Full 108-card Uno. Enter card index or `D` to draw. All 5 action cards apply.  
On Wilds, pick a colour with `R` `B` `G` `Y`. CPU plays a priority-based strategy.

### ⚔️ War vs CPU
Press ENTER each round to flip cards. Higher rank wins both. Tied rank triggers War — 3 face-down cards then a tiebreaker flip. First to all 52 cards wins.

### 8️⃣ Crazy Eights vs CPU
Match the top card by suit or rank. 8s are wild — play any time, then declare the new suit with `S` `H` `D` `C`. Draw until you have a playable card.

### 🐟 Go Fish vs CPU
Ask for ranks you already hold (e.g. `Ace`, `7`, `King`). Get a match → take cards and go again. No match → Go Fish (draw one). Collect all 4 of a rank = a book. Most books after all 13 are claimed wins.

### ♠ 5-Card Draw Poker vs CPU (with chips)

| Phase | What happens |
|-------|-------------|
| Ante | 10 chips from each player |
| Betting round 1 | Check / Call / Raise / Fold |
| Draw | Discard any cards (enter indices e.g. `0 2 4`) |
| Betting round 2 | Same options |
| Showdown | Best 5-card hand wins the pot |

**Hand rankings (low → high):**  
High Card → One Pair → Two Pair → Three of a Kind → Straight → Flush → Full House → Four of a Kind → Straight Flush → Royal Flush

---

## Cleaning Up

```bash
python clean.py
```

Removes all `__pycache__/`, `.pyc`, `.DS_Store`, and `Thumbs.db` files.

---

## Architecture

```python
class BaseGameEngine(ABC):
    @abstractmethod
    def setup(self) -> None: ...          # reset to initial state
    @abstractmethod
    def play_turn(self) -> None: ...      # interactive game loop
    @abstractmethod
    def evaluate_winner(self) -> str: ... # 'player' / 'cpu' / 'push'
    @abstractmethod
    def auto_play(self) -> str: ...       # headless — no input needed
```

Any class missing one of these raises `TypeError` at instantiation — not silently at runtime.

### Adding a New Game

1. Create `src/games/your_game.py`
2. Inherit from `BaseCard`, `BaseDeck`, `BaseGameEngine`
3. Implement all four abstract methods
4. Add a menu entry in `main.py`

The simulator works with any game:

```python
from src.utils.simulator import run_simulation
from src.games.your_game import YourGame

results = run_simulation(YourGame, iterations=10_000)
```

---

## Roadmap

| Game | Status |
|------|--------|
| Blackjack | ✅ Complete |
| Uno | ✅ Complete |
| War | ✅ Complete |
| Crazy Eights | ✅ Complete |
| Go Fish | ✅ Complete |
| 5-Card Draw Poker | ✅ Complete |
| Solitaire (Klondike) | 🔲 Planned |
| Rummy | 🔲 Planned |
| Snap | 🔲 Planned |
