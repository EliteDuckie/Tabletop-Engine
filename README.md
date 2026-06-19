PyTabletop Engine 🎲🃏

A modular, object-oriented tabletop game engine and probability simulator built in Python.

This project was developed to explore advanced Object-Oriented Programming (OOP) concepts, software architecture, and statistical simulation. Rather than hardcoding individual games, this engine provides a unified foundation for card manipulation, turn management, and probability tracking that can be extended to run various tabletop games.

Currently implemented games:

Blackjack (Including a probability simulation mode)

Uno (WIP)

✨ Core Features

Polymorphic Architecture: Uses abstract base classes for GameEngine, Card, and Deck to allow seamless integration of new game types with entirely different rule sets.

Statistical Simulation Mode: Run thousands of headless games (e.g., Blackjack hands) in seconds to track win rates, optimal strategies, and house-edge probabilities.

Pluggable AI Opponents: State-based bots that make decisions based on specific game rules (e.g., standard dealer rules for Blackjack).

Clean State Management: Utilizes a state-machine-inspired game loop to handle transitions between setup, player turns, and evaluation phases.
