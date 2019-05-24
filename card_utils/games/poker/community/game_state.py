""" class for generic omaha game state """
import logging
from typing import List, Dict

from card_utils.games.poker.action import Action
from card_utils.games.poker.game_state import PokerGameState

logger = logging.getLogger(__name__)


class CommunityGameState(PokerGameState):
    """ basic community card game state """

    # NOTE: override these in subclasses!
    name = 'abstract_community'
    num_hole_cards = 0

    # preflop = 1
    # postflop = 2
    # turn = 3
    # river = 4
    max_streets = 4

    def __init__(self,
                 num_players: int,
                 deck: List[str],
                 hands: List[List[str]],
                 starting_stacks: List[int],
                 boards: List[List[str]] = None,
                 ante: int = 0,
                 blinds: List[int] = None,
                 actions: List[Dict] = None,
                 ):
        """
        :param num_players: (int)
        :param deck: ([str])
        :param hands: ([[str]])
        :param starting_stacks: ([[int]])
        :param boards: ([[str]])
        :param blinds: ([int])
        :param actions: ([dict])
        """
        if boards is None:
            boards = [[]]

        if len(boards) != 1:
            raise ValueError(
                f'{self.name} is a community-card game, '
                f'so it must only have one board'
            )
        for hand in hands:
            if len(hand) != self.num_hole_cards:
                raise ValueError(
                    f'Hands in {self.name} must have exactly '
                    f'{self.num_hole_cards}\n'
                    f'Perhaps you need to override the num_hole_cards '
                    f'class variable in {self.__class__.__name__}'
                )

        if num_players == 2 and blinds[0] < blinds[1]:
            logger.warning(
                f'Flipping the blinds for 2-handed play. To suppress this warning, '
                f'you should flip the order of blinds in heads up play. '
                f'e.g. input the blinds as [2, 1] rather than [1, 2] '
                f'because the dealer pays the small blind '
                f'and acts second on all later streets'
            )
            blinds = [blinds[1], blinds[0]]

        super().__init__(
            num_players=num_players,
            deck=deck,
            hands=hands,
            starting_stacks=starting_stacks,
            boards=boards,
            ante=ante,
            blinds=blinds,
            actions=actions,
        )

    def order_hands(self, players):
        """ given a list of players who've seen the hand to showdown,
            sort them by their hand strength,
            first on the resulting list having the strongest hands,
            to last on the list with the weakest hand

        :param players: ([int])
        :return: ([[int]])
        """
        raise NotImplementedError(
            f'All CommunityGameState objects must implement order_hands '
            f'to decide who wins at showdown'
        )

    def extract_blinds(self):
        """ move blinds from self.stacks to self.pot """
        for player, blind in enumerate(self.blinds):
            amount = min(self.stacks[player], blind)
            self.put_money_in_pot(player, amount)

    def get_starting_action(self):
        """ given self.street_actions, derive the current:
            - street
            - action
            - players who have folded
        """
        if self.street == 1:
            # Pre-flop action begins with UTG (2) except 2-handed
            return (
                # In heads-up, player 1 is the button AND the small blind,
                # and therefore starts the action before the flop
                1 if self.num_players == 2
                # Otherwise, the "UTG" player goes first.
                # In 3-handed games, this is the dealer
                else 2
            )
        else:
            # Post-flop action always begins with the first player
            # left of the dealer who hasn't folded
            # e.g. small blind (0), then big blind (1)... etc
            return next(
                p for p in range(self.num_players)
                if self.last_actions.get(p) == Action.action_fold
            )

    def move_street(self):
        """ increment the street and then deal out flop/turn/river if necessary """
        super().move_street()
        if self.street == 2 and len(self.board) == 0:
            # Flop
            self.deal_cards_to_board(3)
        elif self.street == 3 and len(self.board) == 3:
            # Turn
            self.deal_cards_to_board(1)
        elif self.street == 4 and len(self.board) == 4:
            # River
            self.deal_cards_to_board(1)

    def deal_cards_to_board(self, n):
        """
        :param n: (int)
        """
        cards = self.deck[0:n]
        self.deck = self.deck[n:]
        self.boards[0].extend(cards)

    @property
    def board(self):
        """ in community card games, there is only one board,
            so use this property to set/get it

        :return: ([str])
        """
        return self.boards[0]
