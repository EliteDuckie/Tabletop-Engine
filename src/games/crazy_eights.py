"""
crazy_eights.py  —  Crazy Eights: Player vs CPU.

Rules:
  - 5 cards dealt to each player from a standard 52-card deck.
  - Match the top discard by SUIT or RANK.
  - 8s are wild — play on anything, then declare the new suit.
  - If you can't play, draw until you can (or deck runs out).
  - First to empty their hand wins.
"""

import random
from typing import Optional

from src.engine.card import BaseCard
from src.engine.deck import BaseDeck
from src.engine.base_game import BaseGameEngine

SUITS: list[str] = ["♠ Spades", "♥ Hearts", "♦ Diamonds", "♣ Clubs"]
SUIT_SHORT = {"♠ Spades": "♠", "♥ Hearts": "♥", "♦ Diamonds": "♦", "♣ Clubs": "♣"}
RANKS: list[str] = ["2","3","4","5","6","7","8","9","10","Jack","Queen","King","Ace"]
SUIT_EMOJI = {"♠ Spades":"♠","♥ Hearts":"♥","♦ Diamonds":"♦","♣ Clubs":"♣"}


class EightsCard(BaseCard):
    def __init__(self, rank: str, suit: str) -> None:
        self.rank = rank
        self.suit = suit

    def get_value(self) -> int:
        if self.rank == "8":    return 50
        if self.rank in ("Jack","Queen","King"): return 10
        if self.rank == "Ace":  return 1
        return int(self.rank)

    def __str__(self) -> str:
        return f"{SUIT_EMOJI.get(self.suit,'?')} {self.rank} of {self.suit}"

    @property
    def is_eight(self) -> bool:
        return self.rank == "8"


class EightsDeck(BaseDeck):
    def _build(self) -> None:
        self.cards = [EightsCard(r, s) for s in SUITS for r in RANKS]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Optional[EightsCard]:
        return self.cards.pop() if self.cards else None

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def refill_from_discard(self, discard: list) -> None:
        if len(discard) <= 1:
            return
        top = discard[-1]
        refill = discard[:-1]
        random.shuffle(refill)
        self.cards = refill
        discard.clear()
        discard.append(top)
        print("  ♻️  Deck reshuffled from discard.")


class CrazyEightsGame(BaseGameEngine):
    HAND_SIZE = 5

    def __init__(self) -> None:
        self.deck: EightsDeck = EightsDeck()
        self.discard: list[EightsCard] = []
        self.player_hand: list[EightsCard] = []
        self.cpu_hand:    list[EightsCard] = []
        self.current_suit: str = ""          # can be overridden by an 8
        self.top_card: Optional[EightsCard] = None
        self._winner: Optional[str] = None

    def setup(self) -> None:
        self.deck = EightsDeck()
        self.deck.shuffle()
        self.discard = []
        self.player_hand = []
        self.cpu_hand    = []
        self._winner     = None

        for _ in range(self.HAND_SIZE):
            self.player_hand.append(self.deck.draw())
            self.cpu_hand.append(self.deck.draw())

        # Flip starter — never an 8
        while True:
            c = self.deck.draw()
            if c and not c.is_eight:
                self.discard.append(c)
                self.top_card     = c
                self.current_suit = c.suit
                break

    def play_turn(self) -> None:
        self.setup()
        print("\n" + "═" * 50)
        print("  8️⃣   CRAZY EIGHTS  —  You vs CPU")
        print("═" * 50)
        print(f"  Starting card: {self.top_card}")
        print("  Match the suit or rank. 8s are wild!")
        print("═" * 50)

        skip_player = False

        while True:
            if self.deck.is_empty():
                self.deck.refill_from_discard(self.discard)
                self.top_card     = self.discard[-1]
                self.current_suit = self.top_card.suit if not self.top_card.is_eight else self.current_suit

            # ── PLAYER TURN ──────────────────────────────────────────────
            if not skip_player:
                self._show_state()
                self._player_turn()
                if not self.player_hand:
                    self._winner = "player"
                    break
                if len(self.player_hand) == 1:
                    print("  🔔  One card left!")
            else:
                print("\n  ⏭️  Your turn was skipped (2 played)!")
                skip_player = False

            # ── CPU TURN ─────────────────────────────────────────────────
            if self.deck.is_empty():
                self.deck.refill_from_discard(self.discard)

            print(f"\n  🤖 CPU's turn ({len(self.cpu_hand)} cards)…")
            played, skips = self._cpu_turn()
            if played:
                print(f"  🤖 CPU plays: {played}")
            else:
                print(f"  🤖 CPU draws. ({len(self.cpu_hand)} cards)")
            if skips:
                skip_player = True
            if not self.cpu_hand:
                self._winner = "cpu"
                break
            if len(self.cpu_hand) == 1:
                print("  🤖 CPU has one card left!")

        print("\n" + "═" * 50)
        w = self.evaluate_winner()
        print("  🏆  YOU WIN!" if w == "player" else "  💀  CPU WINS!")
        print("═" * 50 + "\n")

    def evaluate_winner(self) -> str:
        if self._winner:        return self._winner
        if not self.player_hand: return "player"
        if not self.cpu_hand:    return "cpu"
        return "ongoing"

    def auto_play(self) -> str:
        self.setup()
        for turn in range(500):
            actor = "player" if turn % 2 == 0 else "cpu"
            hand  = self.player_hand if actor == "player" else self.cpu_hand

            if self.deck.is_empty():
                self.deck.refill_from_discard(self.discard)

            playable = [c for c in hand if self._is_valid(c)]
            if playable:
                card = max(playable, key=lambda c: c.get_value())
                if card.is_eight:
                    counts = {s: sum(1 for x in hand if x.suit == s) for s in SUITS}
                    self.current_suit = max(counts, key=counts.get)
                hand.remove(card)
                self.discard.append(card)
                self.top_card = card
                if not card.is_eight:
                    self.current_suit = card.suit
                if not hand:
                    self._winner = actor
                    return actor
            else:
                drawn = self.deck.draw()
                if drawn:
                    hand.append(drawn)

        self._winner = "cpu"
        return "cpu"

    # ── Helpers ───────────────────────────────────────────────────────────

    def _is_valid(self, card: EightsCard) -> bool:
        if card.is_eight:
            return True
        return card.suit == self.current_suit or card.rank == self.top_card.rank

    def _show_state(self) -> None:
        suit_sym = SUIT_SHORT.get(self.current_suit, self.current_suit)
        print(f"\n{'─'*50}")
        print(f"  Top card     : {self.top_card}  (active suit: {suit_sym})")
        print(f"  CPU hand     : {len(self.cpu_hand)} cards  |  Deck: {self.deck.cards_remaining()}")
        print("\n  YOUR HAND:")
        for i, c in enumerate(self.player_hand):
            mark = "✓" if self._is_valid(c) else " "
            print(f"    [{i}]  {mark}  {c}")
        print()

    def _player_turn(self) -> None:
        while True:
            valid = [i for i, c in enumerate(self.player_hand) if self._is_valid(c)]
            if not valid:
                drawn = self.deck.draw() or (self.deck.refill_from_discard(self.discard) or self.deck.draw())
                if drawn:
                    self.player_hand.append(drawn)
                    print(f"  No playable cards — drew: {drawn}")
                    if self._is_valid(drawn):
                        if input("  Play it? [Y/N]: ").strip().lower() in ("y","yes"):
                            self.player_hand.remove(drawn)
                            self._commit(drawn, actor="player")
                return

            raw = input(f"  Play [0-{len(self.player_hand)-1}] or [D]raw: ").strip().lower()
            if raw in ("d","draw"):
                drawn = self.deck.draw()
                if drawn:
                    self.player_hand.append(drawn)
                    print(f"  Drew: {drawn}")
                    if self._is_valid(drawn):
                        if input("  Play it? [Y/N]: ").strip().lower() in ("y","yes"):
                            self.player_hand.remove(drawn)
                            self._commit(drawn, actor="player")
                return
            if raw.isdigit():
                idx = int(raw)
                if 0 <= idx < len(self.player_hand):
                    card = self.player_hand[idx]
                    if self._is_valid(card):
                        self.player_hand.pop(idx)
                        self._commit(card, actor="player")
                        print(f"  ✅ You played: {card}")
                        return
                    else:
                        print("  ✗ That card doesn't match suit or rank.")
                else:
                    print(f"  ✗ Enter 0 to {len(self.player_hand)-1}.")
            else:
                print("  ✗ Enter a number or D.")

    def _commit(self, card: EightsCard, actor: str) -> None:
        """Place card on discard, update suit. Prompt for suit if 8."""
        self.discard.append(card)
        self.top_card = card
        if card.is_eight:
            if actor == "player":
                self.current_suit = self._player_pick_suit()
            else:
                counts = {s: sum(1 for c in self.cpu_hand if c.suit == s) for s in SUITS}
                self.current_suit = max(counts, key=counts.get)
                print(f"  🤖 CPU declares suit: {SUIT_SHORT[self.current_suit]} {self.current_suit}")
        else:
            self.current_suit = card.suit

    def _player_pick_suit(self) -> str:
        print("  Pick a suit:  [S]pades  [H]earts  [D]iamonds  [C]lubs")
        m = {"s":"♠ Spades","h":"♥ Hearts","d":"♦ Diamonds","c":"♣ Clubs",
             "spades":"♠ Spades","hearts":"♥ Hearts","diamonds":"♦ Diamonds","clubs":"♣ Clubs"}
        while True:
            r = input("  Suit: ").strip().lower()
            if r in m:
                print(f"  Suit set to {SUIT_SHORT[m[r]]} {m[r]}")
                return m[r]
            print("  ✗ Enter S, H, D, or C.")

    def _cpu_turn(self) -> tuple[Optional[EightsCard], bool]:
        playable = [c for c in self.cpu_hand if self._is_valid(c)]
        if not playable:
            drawn = self.deck.draw()
            if drawn:
                self.cpu_hand.append(drawn)
            return None, False
        # CPU prefers 8s last (save them), otherwise highest value
        non_eights = [c for c in playable if not c.is_eight]
        card = max(non_eights, key=lambda c: c.get_value()) if non_eights else playable[0]
        self.cpu_hand.remove(card)
        self._commit(card, actor="cpu")
        return card, False   # Crazy Eights has no skip mechanic in base rules
