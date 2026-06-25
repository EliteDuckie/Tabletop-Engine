"""
uno.py  —  Full Uno: Player vs CPU with all action card effects.
"""

import random
import time
from typing import Optional

from src.engine.card import BaseCard
from src.engine.deck import BaseDeck
from src.engine.base_game import BaseGameEngine

COLORS: list[str] = ["Red", "Blue", "Green", "Yellow"]
COLOR_EMOJI = {"Red": "🔴", "Blue": "🔵", "Green": "🟢", "Yellow": "🟡"}

COLORED_VALUES: list[str] = (
    ["0"]
    + [str(n) for n in range(1, 10)] * 2
    + ["Skip", "Reverse", "Draw Two"] * 2
)
WILD_VALUES: list[str] = ["Wild", "Wild Draw Four"]


class UnoCard(BaseCard):
    def __init__(self, value: str, color: Optional[str] = None) -> None:
        self.value = value
        self.color = color

    def get_value(self) -> int:
        if self.value.lstrip("-").isdigit():
            return int(self.value)
        if self.value in ("Skip", "Reverse", "Draw Two"):
            return 20
        return 50

    def __str__(self) -> str:
        emoji = COLOR_EMOJI.get(self.color, "⬛") if self.color else "⬛"
        return f"{emoji} {self.color} {self.value}" if self.color else f"⬛ {self.value}"

    @property
    def is_wild(self) -> bool:
        return self.value in WILD_VALUES

    @property
    def is_action(self) -> bool:
        return self.value in ("Skip", "Reverse", "Draw Two", "Wild", "Wild Draw Four")


class UnoDeck(BaseDeck):
    def _build(self) -> None:
        self.cards: list[UnoCard] = []
        for color in COLORS:
            for value in COLORED_VALUES:
                self.cards.append(UnoCard(value, color))
        for _ in range(4):
            self.cards.append(UnoCard("Wild"))
            self.cards.append(UnoCard("Wild Draw Four"))

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Optional[UnoCard]:
        return self.cards.pop() if self.cards else None

    def is_empty(self) -> bool:
        return len(self.cards) == 0

    def refill_from_discard(self, discard_pile: list) -> None:
        if len(discard_pile) <= 1:
            return
        top = discard_pile[-1]
        refill = discard_pile[:-1]
        random.shuffle(refill)
        self.cards = refill
        discard_pile.clear()
        discard_pile.append(top)
        print("  ♻️  Deck reshuffled from discard pile.")


class UnoGame(BaseGameEngine):
    HAND_SIZE = 7

    def __init__(self) -> None:
        self.deck: UnoDeck = UnoDeck()
        self.discard_pile: list[UnoCard] = []
        self.player_hand: list[UnoCard] = []
        self.cpu_hand: list[UnoCard] = []
        self.top_card: Optional[UnoCard] = None
        self._winner: Optional[str] = None

    def setup(self) -> None:
        self.deck = UnoDeck()
        self.deck.shuffle()
        self.discard_pile = []
        self.player_hand = []
        self.cpu_hand = []
        self._winner = None
        for _ in range(self.HAND_SIZE):
            self.player_hand.append(self.deck.draw())
            self.cpu_hand.append(self.deck.draw())
        while True:
            card = self.deck.draw()
            if card and not card.is_wild:
                self.discard_pile.append(card)
                self.top_card = card
                break

    def play_turn(self) -> None:
        """Run a full game loop: Player vs CPU until someone empties their hand."""
        self.setup()

        print("\n" + "═" * 50)
        print("  🃏  UNO  —  You vs CPU")
        print("═" * 50)
        print(f"  Starting card: {self.top_card}")
        print(f"  Your hand ({len(self.player_hand)} cards) | CPU hand ({len(self.cpu_hand)} cards)")
        print("═" * 50)

        skip_player = False

        while True:
            # Refill deck if empty
            if self.deck.is_empty():
                self.deck.refill_from_discard(self.discard_pile)
                self.top_card = self.discard_pile[-1] if self.discard_pile else self.top_card

            # ── PLAYER TURN ──────────────────────────────────────────────
            if not skip_player:
                self._show_state()
                self._player_choose()
                if not self.player_hand:
                    self._winner = "player"
                    break
                if len(self.player_hand) == 1:
                    print("  🔔  UNO! You have one card left!")
            else:
                print("\n  ⏭️  Your turn was skipped!")
                skip_player = False

            time.sleep(0.3)

            # Refill before CPU turn
            if self.deck.is_empty():
                self.deck.refill_from_discard(self.discard_pile)

            # ── CPU TURN ─────────────────────────────────────────────────
            print(f"\n  🤖 CPU's turn  ({len(self.cpu_hand)} cards)…")
            time.sleep(0.6)

            cpu_card = self._cpu_choose()
            if cpu_card:
                print(f"  🤖 CPU plays: {cpu_card}")
                skips = self._apply_action(cpu_card, target_hand=self.player_hand, actor="cpu")
                if skips:
                    skip_player = True
                if not self.cpu_hand:
                    self._winner = "cpu"
                    break
                if len(self.cpu_hand) == 1:
                    print("  🤖 CPU says UNO!")
            else:
                drawn = self._safe_draw()
                if drawn:
                    self.cpu_hand.append(drawn)
                    print(f"  🤖 CPU draws a card. ({len(self.cpu_hand)} cards)")

            time.sleep(0.3)

        # ── Result ───────────────────────────────────────────────────────
        result = self.evaluate_winner()
        print("\n" + "═" * 50)
        if result == "player":
            print("  🏆  YOU WIN!  Congratulations!")
        else:
            print("  💀  CPU WINS!  Better luck next time.")
        print("═" * 50 + "\n")

    def evaluate_winner(self) -> str:
        if self._winner:
            return self._winner
        if not self.player_hand:
            return "player"
        if not self.cpu_hand:
            return "cpu"
        return "ongoing"

    def auto_play(self) -> str:
        self.setup()
        for turn in range(300):
            actor = "player" if turn % 2 == 0 else "cpu"
            hand = self.player_hand if actor == "player" else self.cpu_hand
            if self.deck.is_empty():
                self.deck.refill_from_discard(self.discard_pile)
            played = False
            for i, card in enumerate(hand):
                if self.is_valid_play(card):
                    if card.is_wild:
                        card.color = random.choice(COLORS)
                    hand.pop(i)
                    self.discard_pile.append(card)
                    self.top_card = card
                    played = True
                    if not hand:
                        return actor
                    break
            if not played:
                drawn = self.deck.draw()
                if drawn:
                    hand.append(drawn)
        return "cpu"

    def _show_state(self) -> None:
        print("\n" + "─" * 50)
        print(f"  Top card  : {self.top_card}")
        print(f"  CPU hand  : {len(self.cpu_hand)} cards  |  Deck: {self.deck.cards_remaining()}")
        print("\n  YOUR HAND:")
        for i, card in enumerate(self.player_hand):
            mark = "✓" if self.is_valid_play(card) else " "
            print(f"    [{i}]  {mark}  {card}")
        print()

    def _player_choose(self) -> None:
        valid = [i for i, c in enumerate(self.player_hand) if self.is_valid_play(c)]
        while True:
            if not valid:
                print("  No playable cards — drawing from deck.")
                drawn = self._safe_draw()
                if drawn:
                    self.player_hand.append(drawn)
                    print(f"  You drew: {drawn}")
                    if self.is_valid_play(drawn):
                        if input("  Play it? [Y/N]: ").strip().lower() in ("y", "yes"):
                            self.player_hand.remove(drawn)
                            self.discard_pile.append(drawn)
                            self.top_card = drawn
                            self._apply_action(drawn, target_hand=self.cpu_hand, actor="player")
                return

            raw = input(f"  Play [0-{len(self.player_hand)-1}] or [D]raw: ").strip().lower()

            if raw in ("d", "draw"):
                drawn = self._safe_draw()
                if drawn:
                    self.player_hand.append(drawn)
                    print(f"  You drew: {drawn}")
                    if self.is_valid_play(drawn):
                        if input("  Play it? [Y/N]: ").strip().lower() in ("y", "yes"):
                            self.player_hand.remove(drawn)
                            self.discard_pile.append(drawn)
                            self.top_card = drawn
                            self._apply_action(drawn, target_hand=self.cpu_hand, actor="player")
                return

            if raw.isdigit():
                idx = int(raw)
                if 0 <= idx < len(self.player_hand):
                    card = self.player_hand[idx]
                    if self.is_valid_play(card):
                        if card.is_wild:
                            card.color = self._player_pick_color()
                        self.player_hand.pop(idx)
                        self.discard_pile.append(card)
                        self.top_card = card
                        print(f"  ✅ You played: {card}")
                        self._apply_action(card, target_hand=self.cpu_hand, actor="player")
                        return
                    else:
                        print("  ✗ That card can't be played right now.")
                else:
                    print(f"  ✗ Enter 0 to {len(self.player_hand)-1}.")
            else:
                print("  ✗ Type a number or D.")

    def _player_pick_color(self) -> str:
        print("  Pick a colour:  [R]ed  [B]lue  [G]reen  [Y]ellow")
        mapping = {"r": "Red", "b": "Blue", "g": "Green", "y": "Yellow",
                   "red": "Red", "blue": "Blue", "green": "Green", "yellow": "Yellow"}
        while True:
            raw = input("  Colour: ").strip().lower()
            if raw in mapping:
                c = mapping[raw]
                print(f"  🎨 Colour → {COLOR_EMOJI[c]} {c}")
                return c
            print("  ✗ Enter R, B, G, or Y.")

    def _cpu_choose(self) -> Optional[UnoCard]:
        playable = [c for c in self.cpu_hand if self.is_valid_play(c)]
        if not playable:
            return None

        def priority(card: UnoCard) -> int:
            if card.value == "Wild Draw Four":    return 6
            if card.value == "Draw Two":          return 5
            if card.value in ("Skip","Reverse"):  return 4
            if card.value == "Wild":              return 1
            return int(card.value) if card.value.isdigit() else 3

        best = max(playable, key=priority)
        if best.is_wild:
            counts = {c: sum(1 for card in self.cpu_hand if card.color == c) for c in COLORS}
            best.color = max(counts, key=counts.get)
        self.cpu_hand.remove(best)
        self.discard_pile.append(best)
        self.top_card = best
        return best

    def _apply_action(self, card: UnoCard, target_hand: list, actor: str) -> bool:
        who = "CPU" if actor == "player" else "You"
        if card.value == "Skip":
            print(f"  ⏭️  Skip! {who} lose your next turn.")
            return True
        if card.value == "Reverse":
            print(f"  🔄 Reverse! {who} lose your next turn.")
            return True
        if card.value == "Draw Two":
            for _ in range(2):
                c = self._safe_draw()
                if c:
                    target_hand.append(c)
            print(f"  +2  {who} drew 2 cards and lost a turn.")
            return True
        if card.value == "Wild Draw Four":
            for _ in range(4):
                c = self._safe_draw()
                if c:
                    target_hand.append(c)
            print(f"  +4  {who} drew 4 cards and lost a turn.")
            return True
        return False

    def _safe_draw(self) -> Optional[UnoCard]:
        if self.deck.is_empty():
            self.deck.refill_from_discard(self.discard_pile)
            self.top_card = self.discard_pile[-1] if self.discard_pile else self.top_card
        return self.deck.draw()

    def is_valid_play(self, card: UnoCard) -> bool:
        if self.top_card is None:
            return True
        if card.is_wild:
            return True
        if card.color and self.top_card.color and card.color == self.top_card.color:
            return True
        if card.value == self.top_card.value:
            return True
        return False
