"""
base_game.py
------------
Abstract base class for all game engines in the PyTabletop Engine.
Every concrete game must inherit from BaseGameEngine and implement
the required abstract methods.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseGameEngine(ABC):
    """
    Abstract base class that defines the lifecycle of a tabletop game.

    Enforces a consistent interface across all game implementations:
    setup → (play_turn)* → evaluate_winner.

    Subclasses should also implement `auto_play()` when they want to
    support headless simulation via the simulator utility.
    """

    @abstractmethod
    def setup(self) -> None:
        """
        Initialise or reset the game to its starting state.

        This includes building and shuffling decks, dealing initial
        cards, resetting scores, and preparing any game-specific state.
        """

    @abstractmethod
    def play_turn(self) -> None:
        """
        Execute one turn of interactive gameplay.

        Should handle player input, apply game rules for that turn,
        and update the game state accordingly.
        """

    @abstractmethod
    def evaluate_winner(self) -> str:
        """
        Determine and return the result of the completed game.

        Returns:
            str: A description of the outcome, e.g.
                 ``'player'``, ``'dealer'``, or ``'push'``.
        """

    @abstractmethod
    def auto_play(self) -> str:
        """
        Simulate a complete game automatically without human interaction.

        Used by the simulator utility to run thousands of iterations.

        Returns:
            str: The outcome string, identical in format to `evaluate_winner()`.
        """

    def run(self) -> None:
        """
        Template method that orchestrates a full interactive game session.

        Calls `setup()` then repeatedly calls `play_turn()` until the
        game signals completion (governed by subclass state), then calls
        `evaluate_winner()`.

        Subclasses may override this if their flow differs significantly.
        """
        self.setup()
        self.play_turn()
        result = self.evaluate_winner()
        return result

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
