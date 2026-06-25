"""
war.py  —  War card game: Player vs CPU.

Rules:
  - Deck split evenly between player and CPU.
  - Each round both flip the top card; highest rank wins both cards.
  - On a tie ("War"): each player places 3 face-down cards then flips one more.
  - Game ends when one player has all 52 cards (or opponent runs out).
  - For simulation, capped at 1000 rounds to avoid infinite loops.
"""

import random
from collections import deque
from typing import Optional

from src.engine.card import BaseCard
from src.engine.deck import BaseDeck
from src.engine.base_game import BaseGameEngine

SUITS: list[str] = ["♠ Spades", "♥ Hearts", "♦ Diamonds", "♣ Clubs"]
RANKS: list[str] = ["2","3","4","5","6","7","8","9","10","Jack","Queen","King","Ace"]
RANK_VALUE: dict[str, int] = {r: i for i, r in enumerate(RANKS)}


class WarCard(BaseCard):
    def __init__(self, rank: str, suit: str) -> None:
        self.rank = rank
        self.suit = suit

    def get_value(self) -> int:
        return RANK_VALUE[self.rank]

    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"


class WarDeck(BaseDeck):
    def _build(self) -> None:
        self.cards = [WarCard(r, s) for s in SUITS for r in RANKS]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Optional[WarCard]:
        return self.cards.pop() if self.cards else None

    def is_empty(self) -> bool:
        return len(self.cards) == 0


class WarGame(BaseGameEngine):
    MAX_ROUNDS = 1000

    def __init__(self) -> None:
        self.player_pile: deque[WarCard] = deque()
        self.cpu_pile:    deque[WarCard] = deque()
        self._winner: Optional[str] = None
        self._rounds = 0

    def setup(self) -> None:
        deck = WarDeck()
        deck.shuffle()
        self.player_pile = deque()
        self.cpu_pile    = deque()
        self._winner     = None
        self._rounds     = 0
        # Split deck evenly
        for i, card in enumerate(deck.cards):
            (self.player_pile if i % 2 == 0 else self.cpu_pile).append(card)

    def play_turn(self) -> None:
        """Interactive War — plays round by round until the game ends."""
        self.setup()
        print("\n" + "═" * 50)
        print("  ⚔️   WAR  —  You vs CPU")
        print("═" * 50)
        print(f"  Each player starts with {len(self.player_pile)} cards.")
        print("  Press ENTER each round to flip, or Q to quit.")
        print("═" * 50)

        while self.player_pile and self.cpu_pile and self._rounds < self.MAX_ROUNDS:
            key = input(f"\n  [Round {self._rounds+1}] Press ENTER to flip (Q to quit): ").strip().lower()
            if key == "q":
                print("  Game abandoned.")
                return

            result = self._play_round(verbose=True)
            p = len(self.player_pile)
            c = len(self.cpu_pile)
            print(f"  Cards — You: {p}  CPU: {c}")

            if not self.player_pile:
                self._winner = "cpu"
                break
            if not self.cpu_pile:
                self._winner = "player"
                break

        print("\n" + "═" * 50)
        w = self.evaluate_winner()
        if w == "player":
            print("  🏆  YOU WIN!  You collected all 52 cards!")
        elif w == "cpu":
            print("  💀  CPU WINS!")
        else:
            print("  🤝  Draw — round limit reached.")
        print(f"  Total rounds played: {self._rounds}")
        print("═" * 50 + "\n")

    def evaluate_winner(self) -> str:
        if self._winner:
            return self._winner
        if not self.player_pile:
            return "cpu"
        if not self.cpu_pile:
            return "player"
        return "push"

    def auto_play(self) -> str:
        self.setup()
        while self.player_pile and self.cpu_pile and self._rounds < self.MAX_ROUNDS:
            self._play_round(verbose=False)
        if not self.player_pile:
            self._winner = "cpu"
        elif not self.cpu_pile:
            self._winner = "player"
        return self.evaluate_winner()

    def _play_round(self, verbose: bool) -> str:
        self._rounds += 1
        pot: list[WarCard] = []

        p_card = self.player_pile.popleft()
        c_card = self.cpu_pile.popleft()
        pot.extend([p_card, c_card])

        if verbose:
            print(f"  You : {p_card}")
            print(f"  CPU : {c_card}")

        p_val = p_card.get_value()
        c_val = c_card.get_value()

        if p_val > c_val:
            if verbose: print(f"  ✅  You win this round! (+{len(pot)} cards)")
            random.shuffle(pot)
            self.player_pile.extend(pot)
            return "player"

        elif c_val > p_val:
            if verbose: print(f"  ❌  CPU wins this round. (+{len(pot)} cards)")
            random.shuffle(pot)
            self.cpu_pile.extend(pot)
            return "cpu"

        else:
            if verbose: print("  ⚔️   WAR!  Placing 3 face-down cards each…")
            # Each player puts up to 3 cards face-down + 1 face-up
            for _ in range(3):
                if self.player_pile: pot.append(self.player_pile.popleft())
                if self.cpu_pile:    pot.append(self.cpu_pile.popleft())

            if not self.player_pile or not self.cpu_pile:
                # Someone ran out during war — split pot
                random.shuffle(pot)
                half = len(pot) // 2
                self.player_pile.extend(pot[:half])
                self.cpu_pile.extend(pot[half:])
                if verbose: print("  Someone ran out during war — pot split.")
                return "push"

            wp = self.player_pile.popleft()
            wc = self.cpu_pile.popleft()
            pot.extend([wp, wc])
            if verbose:
                print(f"  War flip — You: {wp}  |  CPU: {wc}")

            random.shuffle(pot)
            if wp.get_value() > wc.get_value():
                if verbose: print(f"  ✅  You win the war! (+{len(pot)} cards)")
                self.player_pile.extend(pot)
                return "player"
            elif wc.get_value() > wp.get_value():
                if verbose: print(f"  ❌  CPU wins the war! (+{len(pot)} cards)")
                self.cpu_pile.extend(pot)
                return "cpu"
            else:
                # Double war — split pot
                half = len(pot) // 2
                self.player_pile.extend(pot[:half])
                self.cpu_pile.extend(pot[half:])
                if verbose: print("  Another tie — pot split.")
                return "push"
