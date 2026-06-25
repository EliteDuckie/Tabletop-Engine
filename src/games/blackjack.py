"""
blackjack.py
------------
Complete Blackjack implementation built on the PyTabletop Engine base classes.

Classes:
    BlackjackCard   – a standard playing card with Blackjack-specific values.
    StandardDeck    – a 52-card deck of BlackjackCards.
    BlackjackGame   – the full game engine with interactive and auto-play modes.
"""

import random
from typing import Optional

from src.engine.card import BaseCard
from src.engine.deck import BaseDeck
from src.engine.base_game import BaseGameEngine


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------

SUITS: list[str] = ["♠ Spades", "♥ Hearts", "♦ Diamonds", "♣ Clubs"]
RANKS: list[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "10",
                    "Jack", "Queen", "King", "Ace"]

FACE_CARDS: set[str] = {"Jack", "Queen", "King"}


class BlackjackCard(BaseCard):
    """
    A standard playing card for use in Blackjack.

    Attributes:
        rank (str): The card's rank, e.g. ``'Ace'``, ``'10'``, ``'King'``.
        suit (str): The card's suit, e.g. ``'♠ Spades'``.
    """

    def __init__(self, rank: str, suit: str) -> None:
        self.rank = rank
        self.suit = suit

    def get_value(self) -> int | list[int]:
        """
        Return the Blackjack value of the card.

        Face cards (Jack, Queen, King) are worth 10.
        Aces return ``[1, 11]`` so callers can choose the best fit.
        All other cards return their numeric face value.

        Returns:
            int | list[int]: Numeric value(s) of the card.
        """
        if self.rank in FACE_CARDS:
            return 10
        if self.rank == "Ace":
            return [1, 11]
        return int(self.rank)

    def __str__(self) -> str:
        return f"{self.rank} of {self.suit}"


# ---------------------------------------------------------------------------
# Deck
# ---------------------------------------------------------------------------

class StandardDeck(BaseDeck):
    """
    A standard 52-card deck composed entirely of BlackjackCards.
    """

    def _build(self) -> None:
        """Populate the deck with all 52 rank × suit combinations."""
        self.cards = [
            BlackjackCard(rank, suit)
            for suit in SUITS
            for rank in RANKS
        ]

    def shuffle(self) -> None:
        """Shuffle the deck in place using Fisher-Yates via ``random.shuffle``."""
        random.shuffle(self.cards)

    def draw(self) -> Optional[BlackjackCard]:
        """
        Remove and return the top card.

        Returns:
            BlackjackCard | None: The drawn card, or ``None`` if empty.
        """
        if self.is_empty():
            return None
        return self.cards.pop()

    def is_empty(self) -> bool:
        """Return ``True`` when no cards remain."""
        return len(self.cards) == 0


# ---------------------------------------------------------------------------
# Hand helpers
# ---------------------------------------------------------------------------

def calculate_hand_total(hand: list[BlackjackCard]) -> int:
    """
    Compute the best possible Blackjack total for a hand.

    Aces are counted as 11 first; if the total exceeds 21, each Ace
    is re-counted as 1 until the total is ≤ 21 or all Aces are soft.

    Args:
        hand (list[BlackjackCard]): The cards in the hand.

    Returns:
        int: The optimal total (may still exceed 21 if the hand is bust).
    """
    total = 0
    aces = 0

    for card in hand:
        value = card.get_value()
        if isinstance(value, list):          # Ace
            aces += 1
            total += 11
        else:
            total += value

    # Demote Aces from 11 → 1 while bust
    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


def hand_str(hand: list[BlackjackCard]) -> str:
    """Return a comma-separated display of cards in a hand."""
    return ", ".join(str(c) for c in hand)


# ---------------------------------------------------------------------------
# Game Engine
# ---------------------------------------------------------------------------

class BlackjackGame(BaseGameEngine):
    """
    Full Blackjack game engine.

    Supports both interactive play (``play_turn()``) and headless
    simulation (``auto_play()``).

    Attributes:
        player_hand (list[BlackjackCard]): Cards held by the player.
        dealer_hand (list[BlackjackCard]): Cards held by the dealer.
        deck (StandardDeck): The deck in play.
        _game_over (bool): Internal flag marking whether the round has ended.
    """

    def __init__(self) -> None:
        self.player_hand: list[BlackjackCard] = []
        self.dealer_hand: list[BlackjackCard] = []
        self.deck: StandardDeck = StandardDeck()
        self._game_over: bool = False

    # ------------------------------------------------------------------
    # BaseGameEngine interface
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """Build a fresh shuffled deck and deal two cards to each side."""
        self.player_hand = []
        self.dealer_hand = []
        self._game_over = False

        self.deck = StandardDeck()
        self.deck.shuffle()

        # Deal two cards each, alternating (standard casino style)
        for _ in range(2):
            self.player_hand.append(self.deck.draw())
            self.dealer_hand.append(self.deck.draw())

    def play_turn(self) -> None:
        """
        Run a full interactive round: player hits/stands, then dealer plays.

        Prints the current state to the terminal and reads input from stdin.
        """
        self.setup()

        print("\n" + "═" * 44)
        print("  ♠  BLACKJACK  ♥")
        print("═" * 44)
        print(f"  Dealer shows : {self.dealer_hand[0]}  [hidden]")
        print(f"  Your hand    : {hand_str(self.player_hand)}")
        print(f"  Your total   : {calculate_hand_total(self.player_hand)}")

        # --- Player phase ---
        while True:
            player_total = calculate_hand_total(self.player_hand)

            if player_total == 21:
                print("\n  ★  Blackjack! 21!  ★")
                break
            if player_total > 21:
                print(f"\n  Bust! Total: {player_total}")
                self._game_over = True
                print(f"\n  Result: {self.evaluate_winner()}")
                return

            choice = input("\n  [H]it or [S]tand? ").strip().lower()
            if choice in ("h", "hit"):
                card = self.deck.draw()
                self.player_hand.append(card)
                print(f"  Drew: {card}")
                print(f"  Your hand : {hand_str(self.player_hand)}")
                print(f"  Total     : {calculate_hand_total(self.player_hand)}")
            elif choice in ("s", "stand"):
                break
            else:
                print("  Please enter H or S.")

        # --- Dealer phase ---
        print(f"\n  Dealer reveals: {hand_str(self.dealer_hand)}")
        self._dealer_play()

        print(f"\n  Dealer total : {calculate_hand_total(self.dealer_hand)}")
        print(f"  Your total   : {calculate_hand_total(self.player_hand)}")
        print(f"\n  ► Result: {self.evaluate_winner().upper()}")
        print("═" * 44 + "\n")

    def evaluate_winner(self) -> str:
        """
        Compare totals and return the round result.

        Returns:
            str: One of ``'player'``, ``'dealer'``, or ``'push'``.
        """
        player_total = calculate_hand_total(self.player_hand)
        dealer_total = calculate_hand_total(self.dealer_hand)

        if player_total > 21:
            return "dealer"
        if dealer_total > 21:
            return "player"
        if player_total > dealer_total:
            return "player"
        if dealer_total > player_total:
            return "dealer"
        return "push"

    def auto_play(self) -> str:
        """
        Simulate one complete Blackjack hand with a basic strategy:
        the player hits on ≤ 16, stands on ≥ 17 (mirrors the dealer rule).

        Returns:
            str: The outcome — ``'player'``, ``'dealer'``, or ``'push'``.
        """
        self.setup()

        # Player hits until 17+
        while calculate_hand_total(self.player_hand) < 17:
            drawn = self.deck.draw()
            if drawn:
                self.player_hand.append(drawn)

        # Dealer plays standard rules
        if calculate_hand_total(self.player_hand) <= 21:
            self._dealer_play()

        return self.evaluate_winner()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dealer_play(self) -> None:
        """
        Apply the standard dealer rule: hit until total ≥ 17.
        """
        while calculate_hand_total(self.dealer_hand) < 17:
            card = self.deck.draw()
            if card is None:
                break
            self.dealer_hand.append(card)
            print(f"  Dealer draws: {card}")
