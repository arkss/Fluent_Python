import doctest
import collections

Card = collections.namedtuple('Card', ['rank', 'suit']) # 개별 카드를 나타내는 클래스

class FrenchDeck:
    """
    Example
    -------
    >>> deck = FrenchDeck()
    >>> len(deck)
    52
    >>> for card in sorted(deck, key=spades_high): # doctest: +ELLIPSIS
    ...     print(card)
    """
    ranks = [str(n) for n in range(2,11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()
    

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits
                                        for rank in self.ranks]
                                        
    def __len__(self):
        return len(self._cards) # 완벽하지 않은 private

    def __getitem__(self, position):
        return self._cards[position]


suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)

def spades_high(card):
    rank_value = FrenchDeck.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]

doctest.testmod()