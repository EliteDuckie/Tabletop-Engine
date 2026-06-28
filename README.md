# 🃏 PyTabletop Engine

A modular, object-oriented tabletop game engine built entirely in Python. Six classic card games playable in your terminal — no installs, no dependencies, just Python.

---

## Setup

**Requirements:** Python 3.10+

```bash
python main.py
```

That's it.

---

## Games

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

### ♠ Blackjack
Beat the dealer to 21 without going over. `H` to hit, `S` to stand. Aces auto-adjust between 11 and 1. Dealer hits until 17.

### 📊 Blackjack Simulation
Runs 10,000 hands headlessly using a basic "hit below 17" strategy and prints win/loss/push percentages. Typical result: ~39% player, ~51% dealer, ~10% push — matching real Blackjack house-edge statistics.

### 🃏 Uno vs CPU
Full 108-card Uno. Enter a card index to play or `D` to draw. All action cards work: Skip, Reverse, Draw Two, Wild, Wild Draw Four. On Wilds, pick a colour with `R` `B` `G` `Y`. CPU plays a priority-based strategy and saves Wilds for when it's stuck.

### ⚔️ War vs CPU
Press ENTER each round to flip the top card from each pile. Highest rank wins both cards. On a tie, three cards go face-down and one more flips — highest wins the whole pot. First player to collect all 52 cards wins.

### 8️⃣ Crazy Eights vs CPU
Match the top discard card by suit or rank. 8s are wild — play one any time, then declare the new suit with `S` `H` `D` `C`. If you have nothing playable, draw until you do. First to empty their hand wins.

### 🐟 Go Fish vs CPU
Ask the CPU for any rank you already hold (e.g. `Ace`, `7`, `King`). If they have it, you take all their matching cards and go again. If not — Go Fish, draw one from the deck. Collect all four of a rank to score a book. Most books after all 13 are claimed wins.

### ♠ 5-Card Draw Poker vs CPU
Chip-based poker starting at 1,000 chips each.

| Phase | What happens |
|-------|-------------|
| Ante | 10 chips from each player to open the pot |
| Betting round 1 | Check / Call / Raise / Fold |
| Draw | Click indices to discard (e.g. `0 2 4`), or keep all |
| Betting round 2 | Check / Call / Raise / Fold |
| Showdown | Best 5-card hand wins the pot |

Hand rankings: High Card → One Pair → Two Pair → Three of a Kind → Straight → Flush → Full House → Four of a Kind → Straight Flush → Royal Flush

---

## Project Structure

```
PyTabletop_Engine/
├── main.py              ← Entry point
├── clean.py             ← Removes __pycache__ and temp files
├── README.md
└── src/
    ├── engine/          ← Abstract base classes
    │   ├── card.py          BaseCard
    │   ├── deck.py          BaseDeck
    │   └── base_game.py     BaseGameEngine
    ├── games/           ← Game implementations
    │   ├── blackjack.py
    │   ├── uno.py
    │   ├── war.py
    │   ├── crazy_eights.py
    │   ├── go_fish.py
    │   └── poker.py
    └── utils/
        └── simulator.py     Headless simulation engine
```

---

## Maintenance

```bash
python clean.py
```

Removes all `__pycache__/`, `.pyc`, `.DS_Store`, and `Thumbs.db` files from the project.

---

## Architecture

Every game inherits from three abstract base classes enforced by Python's `abc` module:

```python
class BaseGameEngine(ABC):
    @abstractmethod
    def setup(self) -> None: ...          # reset to starting state

    @abstractmethod
    def play_turn(self) -> None: ...      # interactive game loop

    @abstractmethod
    def evaluate_winner(self) -> str: ... # returns 'player' / 'cpu' / 'push'

    @abstractmethod
    def auto_play(self) -> str: ...       # headless run for simulation
```

Missing any of these raises a `TypeError` at instantiation — caught immediately, not silently at runtime. The simulator works with any game that implements `auto_play()`.
