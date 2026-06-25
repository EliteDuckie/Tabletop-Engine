"""
deck.py
-------
Abstract base class for all decks in the PyTabletop Engine.
Any game-specific deck must inherit from BaseDeck and implement
the required abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.engine.card import BaseCard


class BaseDeck(ABC):
    """
    Abstract base class representing a deck of cards.

    Maintains an ordered list of `BaseCard` instances and enforces
    that subclasses implement shuffling, drawing, and empty-checking.

    Attributes:
        cards (list[BaseCard]): The ordered collection of cards in the deck.
    """

    def __init__(self) -> None:
        self.cards: list[BaseCard] = []
        self._build()

    @abstractmethod
    def _build(self) -> None:
        """
        Populate `self.cards` with the initial set of cards for this deck.

        Called automatically during `__init__`. Subclasses must override
        this to define the composition of the deck (e.g. 52 standard cards,
        108 Uno cards, etc.).
        """

    @abstractmethod
    def shuffle(self) -> None:
        """
        Randomise the order of cards currently in `self.cards`.
        """

    @abstractmethod
    def draw(self) -> Optional[BaseCard]:
        """
        Remove and return the top card from the deck.

        Returns:
            BaseCard | None: The top card, or ``None`` if the deck is empty.
        """

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Check whether the deck has no cards remaining.

        Returns:
            bool: ``True`` if the deck is empty, ``False`` otherwise.
        """

    def cards_remaining(self) -> int:
        """
        Convenience method — returns the number of cards left in the deck.

        Returns:
            int: Length of `self.cards`.
        """
        return len(self.cards)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.cards_remaining()} cards>"
