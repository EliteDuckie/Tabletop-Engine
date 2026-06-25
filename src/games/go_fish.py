"""
go_fish.py  —  Go Fish: Player vs CPU.

Rules:
  - 7 cards dealt to each player (5 if more than 2 players, but we use 7).
  - On your turn, ask the opponent for a rank you hold.
  - If they have it, they hand ALL matching cards to you and you go again.
  - If not, they say "Go Fish!" and you draw from the deck. If you drew what
    you asked for, you go again; otherwise the turn passes.
  - Collect all 4 cards of a rank → lay down a "book" (set of 4).
  - Game ends when all 13 books are laid down.
  - Most books wins.
"""

import random
from typing import Optional
from collections import Counter

from src.engine.card import BaseCard
from src.engine.deck import BaseDeck
from src.engine.base_game import BaseGameEngine

SUITS: list[str] = ["♠ Spades", "♥ Hearts", "♦ Diamonds", "♣ Clubs"]
RANKS: list[str] = ["2","3","4","5","6","7","8","9","10","Jack","Queen","King","Ace"]


class FishCard(BaseCard):
    def __init__(self, rank: str, suit: str) -> None:
        self.rank = rank
        self.suit = suit

    def get_value(self) -> int:
        return RANKS.index(self.rank)

    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"


class FishDeck(BaseDeck):
    def _build(self) -> None:
        self.cards = [FishCard(r, s) for s in SUITS for r in RANKS]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Optional[FishCard]:
        return self.cards.pop() if self.cards else None

    def is_empty(self) -> bool:
        return len(self.cards) == 0


class GoFishGame(BaseGameEngine):
    HAND_SIZE = 7

    def __init__(self) -> None:
        self.deck: FishDeck = FishDeck()
        self.player_hand: list[FishCard] = []
        self.cpu_hand:    list[FishCard] = []
        self.player_books: list[str] = []
        self.cpu_books:    list[str] = []
        self._winner: Optional[str] = None

    def setup(self) -> None:
        self.deck = FishDeck()
        self.deck.shuffle()
        self.player_hand  = []
        self.cpu_hand     = []
        self.player_books = []
        self.cpu_books    = []
        self._winner      = None
        for _ in range(self.HAND_SIZE):
            self.player_hand.append(self.deck.draw())
            self.cpu_hand.append(self.deck.draw())
        self._check_books(self.player_hand, self.player_books, verbose=False)
        self._check_books(self.cpu_hand,    self.cpu_books,    verbose=False)

    def play_turn(self) -> None:
        self.setup()
        print("\n" + "═" * 50)
        print("  🐟  GO FISH  —  You vs CPU")
        print("═" * 50)
        print(f"  7 cards each. Collect all 4 of a rank to score a book.")
        print(f"  13 books total — most books wins!")
        print("═" * 50)

        player_turn = True

        while not self._game_over():
            if not self.player_hand and not self.deck.is_empty():
                self.player_hand.append(self.deck.draw())
            if not self.cpu_hand and not self.deck.is_empty():
                self.cpu_hand.append(self.deck.draw())

            if player_turn:
                player_turn = self._player_turn()
            else:
                player_turn = not self._cpu_turn()

        print("\n" + "═" * 50)
        w = self.evaluate_winner()
        pb, cb = len(self.player_books), len(self.cpu_books)
        print(f"  Books — You: {pb}  CPU: {cb}")
        if w == "player":
            print("  🏆  YOU WIN!")
        elif w == "cpu":
            print("  💀  CPU WINS!")
        else:
            print("  🤝  It's a tie!")
        print("═" * 50 + "\n")

    def evaluate_winner(self) -> str:
        if self._winner:
            return self._winner
        pb, cb = len(self.player_books), len(self.cpu_books)
        if pb > cb:   return "player"
        elif cb > pb: return "cpu"
        return "push"

    def auto_play(self) -> str:
        self.setup()
        player_turn = True
        iterations  = 0
        while not self._game_over() and iterations < 500:
            iterations += 1
            if not self.player_hand and not self.deck.is_empty():
                self.player_hand.append(self.deck.draw())
            if not self.cpu_hand and not self.deck.is_empty():
                self.cpu_hand.append(self.deck.draw())
            if player_turn:
                player_turn = self._auto_ask(
                    asker=self.player_hand, asked=self.cpu_hand,
                    asker_books=self.player_books, asked_books=self.cpu_books,
                    asker_name="player"
                )
            else:
                cpu_goes_again = self._auto_ask(
                    asker=self.cpu_hand, asked=self.player_hand,
                    asker_books=self.cpu_books, asked_books=self.player_books,
                    asker_name="cpu"
                )
                player_turn = not cpu_goes_again
        return self.evaluate_winner()

    # ── Helpers ───────────────────────────────────────────────────────────

    def _game_over(self) -> bool:
        total_books = len(self.player_books) + len(self.cpu_books)
        if total_books == 13:
            return True
        if self.deck.is_empty() and not self.player_hand and not self.cpu_hand:
            return True
        return False

    def _check_books(self, hand: list[FishCard], books: list[str], verbose: bool = True) -> None:
        counts = Counter(c.rank for c in hand)
        for rank, count in counts.items():
            if count == 4 and rank not in books:
                books.append(rank)
                hand[:] = [c for c in hand if c.rank != rank]
                if verbose:
                    owner = "You" if books is self.player_books else "CPU"
                    print(f"  📚 {owner} laid down a book of {rank}s! ({len(books)} book{'s' if len(books)!=1 else ''})")

    def _player_turn(self) -> bool:
        """Returns True if player goes again."""
        self._show_state()
        ranks_in_hand = sorted(set(c.rank for c in self.player_hand), key=lambda r: RANKS.index(r))
        print(f"  Ranks you hold: {', '.join(ranks_in_hand)}")

        while True:
            asked = input("  Ask CPU for rank (e.g. Ace, 7, King): ").strip().title()
            # normalise "7" → "7", "ace" → "Ace"
            if asked not in RANKS:
                # try matching partial
                matches = [r for r in RANKS if r.lower().startswith(asked.lower())]
                if len(matches) == 1:
                    asked = matches[0]
                else:
                    print(f"  ✗ '{asked}' isn't a valid rank. Try: {', '.join(ranks_in_hand)}")
                    continue
            if asked not in ranks_in_hand:
                print(f"  ✗ You must ask for a rank you hold. You have: {', '.join(ranks_in_hand)}")
                continue
            break

        matching = [c for c in self.cpu_hand if c.rank == asked]
        if matching:
            print(f"  ✅  CPU had {len(matching)} {asked}(s) — take them!")
            for c in matching:
                self.cpu_hand.remove(c)
                self.player_hand.append(c)
            self._check_books(self.player_hand, self.player_books)
            return True   # go again
        else:
            print(f"  🐟  Go Fish!")
            drawn = self.deck.draw()
            if drawn:
                print(f"  You drew: {drawn}")
                self.player_hand.append(drawn)
                self._check_books(self.player_hand, self.player_books)
                if drawn.rank == asked:
                    print(f"  Lucky! You drew the {asked} you asked for — go again!")
                    return True
            return False  # turn passes

    def _cpu_turn(self) -> bool:
        """CPU asks for the rank it has the most of. Returns True if goes again."""
        if not self.cpu_hand:
            return False
        counts   = Counter(c.rank for c in self.cpu_hand)
        asked    = max(counts, key=counts.get)
        print(f"\n  🤖 CPU asks: Do you have any {asked}s?")

        matching = [c for c in self.player_hand if c.rank == asked]
        if matching:
            print(f"  You hand over {len(matching)} {asked}(s).")
            for c in matching:
                self.player_hand.remove(c)
                self.cpu_hand.append(c)
            self._check_books(self.cpu_hand, self.cpu_books)
            return True
        else:
            print(f"  🐟  Go Fish, CPU!")
            drawn = self.deck.draw()
            if drawn:
                self.cpu_hand.append(drawn)
                print(f"  CPU drew a card. ({len(self.cpu_hand)} in hand)")
                self._check_books(self.cpu_hand, self.cpu_books)
                if drawn.rank == asked:
                    print(f"  CPU got lucky — goes again!")
                    return True
            return False

    def _auto_ask(self, asker, asked, asker_books, asked_books, asker_name) -> bool:
        if not asker: return False
        counts  = Counter(c.rank for c in asker)
        rank    = max(counts, key=counts.get)
        matching = [c for c in asked if c.rank == rank]
        if matching:
            for c in matching:
                asked.remove(c)
                asker.append(c)
            self._check_books(asker, asker_books, verbose=False)
            return True
        else:
            drawn = self.deck.draw()
            if drawn:
                asker.append(drawn)
                self._check_books(asker, asker_books, verbose=False)
                return drawn.rank == rank
            return False

    def _show_state(self) -> None:
        pb, cb = len(self.player_books), len(self.cpu_books)
        print(f"\n{'─'*50}")
        print(f"  Books — You: {pb}  CPU: {cb}  |  Deck: {self.deck.cards_remaining()}")
        if self.player_books:
            print(f"  Your books : {', '.join(self.player_books)}")
        print(f"\n  YOUR HAND ({len(self.player_hand)} cards):")
        for i, c in enumerate(self.player_hand):
            print(f"    [{i}]  {c}")
        print()
