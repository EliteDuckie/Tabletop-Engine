"""
poker.py  —  5-Card Draw Poker: Player vs CPU with chip betting.

Rules:
  - Each player starts with 1,000 chips.
  - Ante: 10 chips each to open the pot.
  - Betting round 1 → Draw (replace 0-5 cards) → Betting round 2 → Showdown.
  - Betting options: Check (if no bet), Call, Raise, Fold.
  - Best 5-card hand wins the pot.

Hand rankings (low → high):
  High Card < One Pair < Two Pair < Three of a Kind < Straight <
  Flush < Full House < Four of a Kind < Straight Flush < Royal Flush
"""

import random
from typing import Optional
from itertools import combinations
from collections import Counter

from src.engine.card import BaseCard
from src.engine.deck import BaseDeck
from src.engine.base_game import BaseGameEngine

SUITS: list[str] = ["♠ Spades", "♥ Hearts", "♦ Diamonds", "♣ Clubs"]
SUIT_SYM = {"♠ Spades":"♠","♥ Hearts":"♥","♦ Diamonds":"♦","♣ Clubs":"♣"}
RANKS: list[str] = ["2","3","4","5","6","7","8","9","10","Jack","Queen","King","Ace"]
RANK_VAL: dict[str,int] = {r:i+2 for i,r in enumerate(RANKS)}  # 2→2 … Ace→14

HAND_NAMES = [
    "High Card","One Pair","Two Pair","Three of a Kind",
    "Straight","Flush","Full House","Four of a Kind",
    "Straight Flush","Royal Flush"
]

STARTING_CHIPS = 1000
ANTE           = 10


# ── Card / Deck ───────────────────────────────────────────────────────────────

class PokerCard(BaseCard):
    def __init__(self, rank: str, suit: str) -> None:
        self.rank = rank
        self.suit = suit

    def get_value(self) -> int:
        return RANK_VAL[self.rank]

    def __str__(self) -> str:
        return f"{SUIT_SYM[self.suit]}{self.rank}"


class PokerDeck(BaseDeck):
    def _build(self) -> None:
        self.cards = [PokerCard(r, s) for s in SUITS for r in RANKS]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Optional[PokerCard]:
        return self.cards.pop() if self.cards else None

    def is_empty(self) -> bool:
        return len(self.cards) == 0


# ── Hand evaluator ────────────────────────────────────────────────────────────

def _rank_hand(hand: list[PokerCard]) -> tuple:
    """
    Return a tuple (rank_index, tiebreaker_list) for a 5-card hand.
    Higher tuple = stronger hand.
    """
    values  = sorted([c.get_value() for c in hand], reverse=True)
    suits   = [c.suit for c in hand]
    counts  = Counter(values)
    freqs   = sorted(counts.values(), reverse=True)   # e.g. [3,1,1] for three-of-a-kind
    groups  = sorted(counts.keys(), key=lambda v: (counts[v], v), reverse=True)

    is_flush    = len(set(suits)) == 1
    is_straight = (len(set(values)) == 5 and values[0] - values[4] == 4)
    # Wheel straight: A-2-3-4-5
    wheel = values == [14,5,4,3,2]
    if wheel:
        is_straight = True
        values = [5,4,3,2,1]
        groups = [5,4,3,2,1]

    if is_straight and is_flush:
        if values[0] == 14:
            return (9, values)   # Royal Flush
        return (8, values)       # Straight Flush

    if freqs[0] == 4:            return (7, groups)   # Four of a Kind
    if freqs[:2] == [3,2]:       return (6, groups)   # Full House
    if is_flush:                 return (5, values)   # Flush
    if is_straight:              return (4, values)   # Straight
    if freqs[0] == 3:            return (3, groups)   # Three of a Kind
    if freqs[:2] == [2,2]:       return (2, groups)   # Two Pair
    if freqs[0] == 2:            return (1, groups)   # One Pair
    return (0, values)                                # High Card


def hand_name(hand: list[PokerCard]) -> str:
    return HAND_NAMES[_rank_hand(hand)[0]]


def best_hand_str(hand: list[PokerCard]) -> str:
    cards_str = "  ".join(str(c) for c in hand)
    return f"{cards_str}   [{hand_name(hand)}]"


# ── Game Engine ───────────────────────────────────────────────────────────────

class PokerGame(BaseGameEngine):

    def __init__(self) -> None:
        self.player_chips: int = STARTING_CHIPS
        self.cpu_chips:    int = STARTING_CHIPS
        self.player_hand:  list[PokerCard] = []
        self.cpu_hand:     list[PokerCard] = []
        self.deck:         PokerDeck = PokerDeck()
        self.pot:          int = 0
        self._winner:      Optional[str] = None
        self._current_bet: int = 0

    def setup(self) -> None:
        """Deal a fresh hand; ante up."""
        self.deck = PokerDeck()
        self.deck.shuffle()
        self.player_hand = []
        self.cpu_hand    = []
        self._winner     = None
        self._current_bet = 0
        self.pot         = 0

        ante = min(ANTE, self.player_chips, self.cpu_chips)
        self.player_chips -= ante
        self.cpu_chips    -= ante
        self.pot          += ante * 2

        for _ in range(5):
            self.player_hand.append(self.deck.draw())
            self.cpu_hand.append(self.deck.draw())

    def play_turn(self) -> None:
        """Run a full interactive poker hand."""
        self.setup()

        print("\n" + "═"*52)
        print(f"  ♠  POKER  —  Chips: You {self.player_chips}  CPU {self.cpu_chips}")
        print("═"*52)
        print(f"  Ante: {ANTE} chips each.  Pot: {self.pot}")
        print(f"\n  YOUR HAND:")
        self._show_hand(self.player_hand)

        # ── Betting round 1 ──────────────────────────────────────────────
        print("\n  ── Betting Round 1 ──")
        folded = self._betting_round(player_first=True)
        if folded:
            self._finish(folded)
            return

        # ── Draw phase ───────────────────────────────────────────────────
        print("\n  ── Draw Phase ──")
        self.player_hand = self._player_draw()
        self.cpu_hand    = self._cpu_draw()

        print(f"\n  YOUR HAND after draw:")
        self._show_hand(self.player_hand)

        # ── Betting round 2 ──────────────────────────────────────────────
        print("\n  ── Betting Round 2 ──")
        self._current_bet = 0
        folded = self._betting_round(player_first=True)
        if folded:
            self._finish(folded)
            return

        # ── Showdown ─────────────────────────────────────────────────────
        print("\n  ── Showdown ──")
        print(f"  YOUR hand : {best_hand_str(self.player_hand)}")
        print(f"  CPU  hand : {best_hand_str(self.cpu_hand)}")

        p_rank = _rank_hand(self.player_hand)
        c_rank = _rank_hand(self.cpu_hand)

        if p_rank > c_rank:
            self._finish("player_wins")
        elif c_rank > p_rank:
            self._finish("cpu_wins")
        else:
            self._finish("tie")

    def evaluate_winner(self) -> str:
        return self._winner or "ongoing"

    def auto_play(self) -> str:
        self.setup()
        # CPU strategy: raise if hand rank ≥ 1 (pair or better), else check/call
        p_score = _rank_hand(self.player_hand)[0]
        c_score = _rank_hand(self.cpu_hand)[0]
        bet = 50 if c_score >= 1 else 0
        if bet:
            self.pot += min(bet, self.player_chips) + min(bet, self.cpu_chips)

        # Simple draw: discard cards not in the best grouping
        self.player_hand = self._auto_draw(self.player_hand)
        self.cpu_hand    = self._auto_draw(self.cpu_hand)

        p_rank = _rank_hand(self.player_hand)
        c_rank = _rank_hand(self.cpu_hand)
        if p_rank > c_rank:
            self._winner = "player"
        elif c_rank > p_rank:
            self._winner = "cpu"
        else:
            self._winner = "push"
        return self._winner

    # ── Internal ─────────────────────────────────────────────────────────────

    def _show_hand(self, hand: list[PokerCard]) -> None:
        for i, c in enumerate(hand):
            print(f"    [{i}]  {c}")
        print(f"  → {hand_name(hand)}")

    def _betting_round(self, player_first: bool) -> Optional[str]:
        """
        Single betting round. Returns 'player' if player folds, 'cpu' if CPU folds, None otherwise.
        """
        current_bet = self._current_bet
        player_paid = 0
        cpu_paid    = 0

        # CPU decides first bet based on hand strength
        cpu_hand_rank = _rank_hand(self.cpu_hand)[0]

        for turn in range(4):   # max 2 raises each
            if turn % 2 == 0:   # player's move
                options = []
                if current_bet == player_paid:
                    options.append("[C]heck")
                else:
                    options.append(f"[C]all (+{current_bet - player_paid})")
                options += ["[R]aise", "[F]old"]
                print(f"  Pot: {self.pot}  |  Your chips: {self.player_chips}")
                print(f"  Options: {'  '.join(options)}")
                choice = input("  Your move: ").strip().lower()

                if choice in ("f","fold"):
                    return "player"
                elif choice in ("r","raise"):
                    while True:
                        amt = input(f"  Raise amount (10–{min(200,self.player_chips)}): ").strip()
                        if amt.isdigit() and 10 <= int(amt) <= min(200,self.player_chips):
                            amt = int(amt)
                            break
                        print("  ✗ Enter a number between 10 and 200.")
                    diff = (current_bet - player_paid) + amt
                    diff = min(diff, self.player_chips)
                    self.player_chips -= diff
                    self.pot          += diff
                    player_paid       += diff
                    current_bet        = player_paid
                    print(f"  You raise {amt}. Pot: {self.pot}")
                else:  # check or call
                    diff = current_bet - player_paid
                    diff = min(diff, self.player_chips)
                    self.player_chips -= diff
                    self.pot          += diff
                    player_paid       += diff
                    if diff:
                        print(f"  You call {diff}. Pot: {self.pot}")
                    else:
                        print(f"  You check. Pot: {self.pot}")
                    if player_paid == cpu_paid:
                        break   # both even — round over

            else:   # CPU's move
                if current_bet == cpu_paid:
                    if cpu_hand_rank >= 2:   # two pair or better → raise
                        amt = random.choice([20, 30, 50])
                        amt = min(amt, self.cpu_chips)
                        self.cpu_chips -= amt
                        self.pot       += amt
                        cpu_paid       += amt
                        current_bet     = cpu_paid
                        print(f"  🤖 CPU raises {amt}. Pot: {self.pot}")
                    else:
                        print(f"  🤖 CPU checks. Pot: {self.pot}")
                        break
                else:
                    if cpu_hand_rank == 0 and random.random() < 0.3:
                        print("  🤖 CPU folds.")
                        return "cpu"
                    diff = current_bet - cpu_paid
                    diff = min(diff, self.cpu_chips)
                    self.cpu_chips -= diff
                    self.pot       += diff
                    cpu_paid       += diff
                    print(f"  🤖 CPU calls {diff}. Pot: {self.pot}")
                    break

        self._current_bet = current_bet
        return None

    def _player_draw(self) -> list[PokerCard]:
        print(f"  Your hand:")
        self._show_hand(self.player_hand)
        print("  Enter indices of cards to DISCARD (e.g. 0 2 4), or ENTER to keep all:")
        raw = input("  Discard: ").strip()
        if not raw:
            print("  Keeping all cards.")
            return self.player_hand

        indices = []
        for tok in raw.split():
            if tok.isdigit() and 0 <= int(tok) <= 4:
                indices.append(int(tok))
        indices = list(set(indices))

        new_hand = []
        for i, card in enumerate(self.player_hand):
            if i in indices:
                new_card = self.deck.draw()
                if new_card:
                    new_hand.append(new_card)
                    print(f"  Replaced [{i}] with: {new_card}")
                else:
                    new_hand.append(card)
            else:
                new_hand.append(card)
        return new_hand

    def _cpu_draw(self) -> list[PokerCard]:
        new_hand = self._auto_draw(self.cpu_hand)
        discarded = len(self.cpu_hand) - sum(
            1 for c in new_hand if c in self.cpu_hand
        )
        n = sum(1 for nc in new_hand if nc not in self.cpu_hand)
        print(f"  🤖 CPU draws {n} card(s).")
        return new_hand

    def _auto_draw(self, hand: list[PokerCard]) -> list[PokerCard]:
        """Keep the best grouping, discard the rest."""
        counts  = Counter(c.get_value() for c in hand)
        # keep cards that are part of a pair or better
        keep_vals = {v for v, cnt in counts.items() if cnt >= 2}
        # if flush draw (4 of suit), keep all same suit
        suit_counts = Counter(c.suit for c in hand)
        dominant_suit = max(suit_counts, key=suit_counts.get)
        if suit_counts[dominant_suit] >= 4:
            keep_vals = {c.get_value() for c in hand if c.suit == dominant_suit}

        new_hand = []
        for card in hand:
            if card.get_value() in keep_vals:
                new_hand.append(card)
            else:
                replacement = self.deck.draw()
                new_hand.append(replacement if replacement else card)

        return new_hand[:5]

    def _finish(self, result: str) -> None:
        print("\n" + "═"*52)
        if result == "player_wins" or result == "player":
            print(f"  🏆  YOU WIN the pot of {self.pot} chips!")
            self.player_chips += self.pot
            self._winner = "player"
        elif result == "cpu_wins" or result == "cpu":
            print(f"  💀  CPU WINS the pot of {self.pot} chips!")
            self.cpu_chips += self.pot
            self._winner = "cpu"
        elif result == "tie" or result == "push":
            half = self.pot // 2
            self.player_chips += half
            self.cpu_chips    += half
            print(f"  🤝  Tie! Pot split ({half} chips each).")
            self._winner = "push"
        print(f"  Chips — You: {self.player_chips}  CPU: {self.cpu_chips}")
        print("═"*52 + "\n")
