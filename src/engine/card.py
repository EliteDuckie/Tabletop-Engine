"""
card.py
-------
Abstract base class for all cards in the PyTabletop Engine.
Any game-specific card must inherit from BaseCard and implement
the required abstract methods.
"""

from abc import ABC, abstractmethod


class BaseCard(ABC):
    """
    Abstract base class representing a single playing card.

    Subclasses must implement `get_value()` and `__str__()` to define
    how a card contributes to game logic and how it is displayed.
    """

    @abstractmethod
    def get_value(self) -> int | list[int]:
        """
        Return the numeric value of the card.

        For games where a card may have multiple possible values
        (e.g. an Ace in Blackjack), a list of integers may be returned.

        Returns:
            int | list[int]: The card's value(s).
        """

    @abstractmethod
    def __str__(self) -> str:
        """
        Return a human-readable string representation of the card.

        Returns:
            str: A display string such as 'Ace of Spades' or 'Red 7'.
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self}>"
