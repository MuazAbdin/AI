################################################
# This code is written by Peter Norvig
# https://nbviewer.jupyter.org/github/norvig/pytudes/blob/main/ipynb/Scrabble.ipynb
# We made some modifications to match it to our project
###############################################

import random
import time
from collections import defaultdict, namedtuple
from typing import List, Callable

import AIAgents as AI

BOARD = ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#',
         '#', '=', '.', '.', ':', '.', '.', '.', '=', '.', '.', '.', ':', '.', '.', '=', '#',
         '#', '.', '-', '.', '.', '.', ';', '.', '.', '.', ';', '.', '.', '.', '-', '.', '#',
         '#', '.', '.', '-', '.', '.', '.', ':', '.', ':', '.', '.', '.', '-', '.', '.', '#',
         '#', ':', '.', '.', '-', '.', '.', '.', ':', '.', '.', '.', '-', '.', '.', ':', '#',
         '#', '.', '.', '.', '.', '-', '.', '.', '.', '.', '.', '-', '.', '.', '.', '.', '#',
         '#', '.', ';', '.', '.', '.', ';', '.', '.', '.', ';', '.', '.', '.', ';', '.', '#',
         '#', '.', '.', ':', '.', '.', '.', ':', '.', ':', '.', '.', '.', ':', '.', '.', '#',
         '#', '=', '.', '.', ':', '.', '.', '.', '*', '.', '.', '.', ':', '.', '.', '=', '#',
         '#', '.', '.', ':', '.', '.', '.', ':', '.', ':', '.', '.', '.', ':', '.', '.', '#',
         '#', '.', ';', '.', '.', '.', ';', '.', '.', '.', ';', '.', '.', '.', ';', '.', '#',
         '#', '.', '.', '.', '.', '-', '.', '.', '.', '.', '.', '-', '.', '.', '.', '.', '#',
         '#', ':', '.', '.', '-', '.', '.', '.', ':', '.', '.', '.', '-', '.', '.', ':', '#',
         '#', '.', '.', '-', '.', '.', '.', ':', '.', ':', '.', '.', '.', '-', '.', '.', '#',
         '#', '.', '-', '.', '.', '.', ';', '.', '.', '.', ';', '.', '.', '.', '-', '.', '#',
         '#', '=', '.', '.', ':', '.', '.', '.', '=', '.', '.', '.', ':', '.', '.', '=', '#',
         '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']


def Word(w: str) -> str: return w.strip().upper()


DICTIONARY = {Word(w) for w in open('./Dictionaries/CollinsScrabbleWords2019.txt')}


def is_word(word: str) -> bool:
    """ Is this a legal word in the dictionary? """
    return word.upper() in DICTIONARY


BLANK = '_'  # The blank tile (as it appears in the rack)
cat = ''.join  # Function to concatenate strings


def letters(rack: str) -> str:
    """ All the distinct letters in a rack (including lowercase if there is a blank). """
    if BLANK in rack:
        return cat(set(rack.replace(BLANK, ''))) + 'abcdefghijklmnopqrstuvwxyz'
    else:
        return cat(set(rack))


def remove(tiles: str, rack: str) -> str:
    """ Return a copy of rack with the given tile(s) removed. """
    for tile in tiles:
        if tile.islower():
            tile = BLANK
        rack = rack.replace(tile, '', 1)
    return rack


def fill_bag():
    bag = []

    bag.extend(['Q', 'Z', 'J', 'X', 'K'])
    for i in range(2): bag.extend(['F', 'H', 'V', 'W', 'Y', 'B', 'C', 'M', 'P', '_'])
    for i in range(3): bag.extend(['G'])
    for i in range(4): bag.extend(['D', 'U', 'S', 'L'])
    for i in range(6): bag.extend(['T', 'R', 'N'])
    for i in range(8): bag.extend(['O'])
    for i in range(9): bag.extend(['I', 'A'])
    for i in range(12): bag.extend(['E'])

    return bag


def replenish(rack, bag) -> str:
    """ Fill rack with 7 letters (as long as there are letters left in the bag). """
    while len(rack) < 7 and bag:
        rack += bag.pop()
    return rack


def exchange_letters(rack: str, bag: List[str]) -> str:
    """  Exchange three letters from the rack by new ones from the bag  """
    new_rack = rack
    num = min(len(rack), 3)
    letters_to_move = random.sample(rack, num)

    for letter in letters_to_move:
        idx = new_rack.index(letter)
        new_rack = new_rack[:idx] + new_rack[idx + 1:]

    bag += letters_to_move
    random.shuffle(bag)

    return replenish(new_rack, bag)


ACROSS = 1  # The 'across' direction; 'down' depends on the size of the board
OFF = '#'  # A square that is off the board
SL, DL, TL, STAR, DW, TW = EMPTY = '.:;*-='
# Single/double/triple letter; star, double/triple word bonuses

Square = int  # Squares are implemented as integer indexes.
Direction = int  # Directions are implemented as integer increments


def dict_prefixes(dictionary) -> set:
    """ The set of all prefixes of each word in a dictionary. """
    return {word[:i] for word in dictionary for i in range(len(word))}


PREFIXES = dict_prefixes(DICTIONARY)


def rack_prefixes(rack) -> set:
    """ All word prefixes that can be made by the rack. """
    return extend_prefixes('', rack, set())


def extend_prefixes(prefix, rack, results) -> set:
    if prefix.upper() in PREFIXES:
        results.add(prefix)
        for L in letters(rack):
            extend_prefixes(prefix + L, remove(L, rack), results)
    return results


POINTS = defaultdict(int,
                     A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3,
                     N=1, O=1, P=3, Q=10, R=1, S=1, T=1, U=1, V=4, W=4, X=8, Y=4, Z=10)


# Play = namedtuple('Play', 'start, dir, letters, rack')

class Play(namedtuple('Play', 'start, dir, letters, rack')):
    def __repr__(self):
        x = self.start // 17
        y = self.start % 17
        dir = 'ACROSS' if self.dir == ACROSS else 'DOWN'
        return f'Play(start=({x}, {y}), dir={dir}, letters={self.letters}, rack={self.rack})'


class Board(list):
    """
    A Board is a (linear) list of squares, each a single character.
    Note that board[s + down] is directly below board[s].
    """
    MAX_BOARD_SCORE = 1320

    def __init__(self, squares: List[str], players=None):
        list.__init__(self, squares)
        down = int(len(squares) ** 0.5)
        self.down = down
        self.directions = (ACROSS, down, -ACROSS, -down)

        self.bag = fill_bag()
        random.seed()
        random.shuffle(self.bag)

        self.players = players
        self.all_exchanges = 0
        self.cur_p_idx = 0
        if players:
            self.all_exchanges = 2 * len(players)
            for p in players: p.rack = replenish('', self.bag)

    def clone(self):
        """ Returns a deep copy of the current board """
        copy = Board(self)
        copy.bag = self.bag[:]
        copy.players = [p.clone() for p in self.players]
        copy.cur_p_idx = self.cur_p_idx
        copy.all_exchanges = self.all_exchanges
        return copy

    def make_partial_play(self, play):
        p = self.players[self.cur_p_idx]

        if play.letters == '' and p.num_exchanges > 0:
            p.rack = exchange_letters(p.rack, self.bag)
            p.num_exchanges -= 1
            self.all_exchanges -= 1
            return

        end = play.start + len(play.letters) * play.dir
        self[play.start:end:play.dir] = play.letters

        p.rack = play.rack  # do not replenish
        points = self.score(play)
        p.score += points

        racks = [p.rack for p in self.players]
        scores = [p.score for p in self.players]
        if p.rack == '': subtract_remaining_tiles(racks, scores, p)

        self.cur_p_idx = (self.cur_p_idx + 1) % len(self.players)

    def make_one_play(self, play, verbose=False):
        """
        One player, player p, chooses a move according to the strategy.
        We make the move, replenish the rack, update scores, and return the new Board.
        """
        p = self.players[self.cur_p_idx]

        if play.letters == '' and p.num_exchanges >= 0:
            if p.num_exchanges > 0:
                p.rack = exchange_letters(p.rack, self.bag)
                p.num_exchanges -= 1
            self.all_exchanges -= 1
            return

        rack = p.rack
        p.rack = replenish(play.rack, self.bag)
        points = self.score(play)
        p.score += points

        end = play.start + len(play.letters) * play.dir
        self[play.start:end:play.dir] = play.letters

        racks = [p.rack for p in self.players]
        scores = [p.score for p in self.players]
        if p.rack == '':
            scores = subtract_remaining_tiles(racks, scores, p)

        self.cur_p_idx = (self.cur_p_idx + 1) % len(self.players)

        if verbose:
            print('Player {} with rack {} makes {} for {} points; draws: {}; scores: {}'
                  .format(p.name, rack, play, points, p.rack, scores))
            print(self, end='\n')

    def all_plays(self):
        """
        Generate all plays that can be played on board with this rack.
        Try placing every possible prefix before every anchor point;
        then extend one letter at a time, looking for valid plays.
        """
        p = self.players[self.cur_p_idx]
        rack = p.rack
        anchors = all_anchors(self)
        prefixes = rack_prefixes(rack)
        yield Play(0, ACROSS, '', rack)  # The empty play (no letters, no points)
        for anchor in anchors:
            for dir in (ACROSS, self.down):
                for play in prefix_plays(prefixes, self, anchor, dir, rack):
                    yield from extend_play(self, play)

    def score(self, play) -> int:
        """ The number of points scored by making this play on the board. """
        return (word_score(self, play)
                + bingo(self, play)
                + sum(word_score(self, cplay)
                      for cplay in cross_plays(self, play)))

    def get_result(self, player):
        if len(self.players) == 1:
            return player.score / Board.MAX_BOARD_SCORE
        return 1.0 if player.score == max([p.score for p in self.players]) else 0.0

    def __str__(self):
        """Return a string representation of the board, suitable for human viewing.
        Uses colors to highlight various squares."""

        empty_board = BOARD[:]

        board_colors = {
            DL: (106, 30),
            TL: (44, 30),
            DW: (101, 30),
            TW: (41, 30),
            SL: (47, 30),
            STAR: (101, 30)}

        rows = []
        for row in range(1, 16):
            cols = []
            for col in range(1, 16):
                idx = row * 17 + col
                empty_sq = empty_board[idx]
                # print(f' >> {empty_sq} <<')
                sq = self[idx] if self[idx] not in EMPTY else ' '

                bg, fg = board_colors.get(empty_sq)
                if sq.islower(): bg, fg = (43, 30)

                # 256-color Xterm code is \033[38;5;Xm or 48 for background.
                # We're using 8-color mode here.
                sq = u"\u001b[%d;%dm %s \u001b[0m" % (bg, fg, sq)
                cols.append(sq)

            rows.append("".join(cols))
        return "\n".join(rows)

    # ---------- Enf of Board Class ---------- #


# Strategy = Callable[[Board, str], Play]
Strategy = Callable[[Board], Play]


class Player:
    def __init__(self, name: str, strategy: Strategy = None):
        self.name = name
        self.score = 0
        self.rack = ''
        self.strategy = strategy
        self.num_exchanges = 2

    def is_human(self):
        return self.strategy is not None

    def clone(self):
        copy = Player(self.name, self.strategy)
        copy.score = self.score
        copy.rack = self.rack
        copy.num_exchanges = self.num_exchanges
        return copy


def is_anchor(board, s) -> bool:
    """ Is this square next to a letter already on the board? (Or is it a '*')? """
    return (board[s] == STAR or
            board[s] in EMPTY and any(board[s + d].isalpha() for d in board.directions))


def all_anchors(board) -> list:
    """ A list of all anchor squares on the board. """
    return [s for s in range(len(board)) if is_anchor(board, s)]


def prefix_plays(prefixes, board, anchor, dir, rack) -> list:
    """ Return all Plays of a prefix to the left/above anchor. """
    if board[anchor - dir].isalpha():  # Prefix already on the board; only 1 prefix
        start = scan_letters(board, anchor, -dir)
        return [Play(start, dir, cat(board[start:anchor:dir]), rack)]
    else:  # Prefixes from rack fit in space before anchor
        maxlen = (anchor - scan_to_anchor(board, anchor, -dir)) // dir
        return [Play(anchor - len(prefix) * dir, dir, prefix, remove(prefix, rack))
                for prefix in prefixes if len(prefix) <= maxlen]


def extend_play(board, play):
    """ Explore all ways of adding to end of play; return ones that form full words. """
    s = play.start + play.dir * len(play.letters)
    if board[s] == OFF: return
    cword = crossword(board, s, play.dir)
    possible_letters = board[s].upper() if board[s].isalpha() else letters(play.rack)
    for L in possible_letters:
        prefix2 = play.letters + L
        if prefix2.upper() in PREFIXES and valid_crossword(cword, L):
            rack2 = play.rack if board[s].isalpha() else remove(L, play.rack)
            play2 = Play(play.start, play.dir, prefix2, rack2)
            if is_word(prefix2) and not board[s + play.dir].isalpha():
                yield play2
            yield from extend_play(board, play2)


def scan_letters(board, s, dir) -> Square:
    """ Return the last square number going from s in dir that is a letter. """
    while board[s + dir].isalpha():
        s += dir
    return s


def scan_to_anchor(board, s, dir) -> Square:
    """
    Return the last square number going from s in dir that is not an anchor nor off board.
    """
    while board[s + dir] != OFF and not is_anchor(board, s + dir):
        s += dir
    return s


def crossword(board, s, dir) -> str:
    """
    The word that intersects s in the other direction from dir.
    Use '.' for the one square that is missing a letter.
    """

    def canonical(L): return L if L.isalpha() else '.'

    d = other(dir, board)
    start = scan_letters(board, s, -d)
    end = scan_letters(board, s, d)
    return cat(canonical(board[s]) for s in range(start, end + d, d))


def valid_crossword(cword, L) -> bool:
    """ Is placing letter L valid (with respective to the crossword)? """
    return len(cword) == 1 or cword.replace('.', L).upper() in DICTIONARY


def other(dir, board) -> Direction:
    """ The other direction (across/down) on the board. """
    return board.down if dir == ACROSS else ACROSS


def word_score(board, play) -> int:
    """ Points for a single word, counting word- and letter-bonuses. """
    total, word_bonus = 0, 1
    for (s, L) in enumerate_play(play):
        sq = board[s]
        word_bonus *= (3 if sq == TW else 2 if sq in [DW, STAR] else 1)
        total += POINTS[L] * (3 if sq == TL else 2 if sq == DL else 1)
    return word_bonus * total


def bingo(board, play) -> int:
    """ A bonus for using 7 letters from the rack. """
    return BINGO if (play.rack == '' and letters_played(board, play) == 7) else 0


BINGO = 50  # 50 for Scrabble


def letters_played(board, play) -> int:
    """ The number of letters played from the rack. """
    return sum(board[s] in EMPTY for (s, L) in enumerate_play(play))


def enumerate_play(play) -> list:
    """ List (square_number, letter) pairs for each tile in the play. """
    return [(play.start + i * play.dir, L)
            for (i, L) in enumerate(play.letters)]


def cross_plays(board, play):
    """ Generate all plays for words that cross this play. """
    cross = other(play.dir, board)
    for (s, L) in enumerate_play(play):
        if board[s] in EMPTY and (board[s - cross].isalpha() or board[s + cross].isalpha()):
            start, end = scan_letters(board, s, -cross), scan_letters(board, s, cross)
            before, after = cat(board[start:s:cross]), cat(board[s + cross:end + cross:cross])
            yield Play(start, cross, before + L + after, play.rack)


def subtract_remaining_tiles(racks, scores, p) -> list:
    """ Subtract point values from each player and give them to player p. """
    for i in range(len(racks)):
        points = sum(POINTS[L] for L in racks[i])
        scores[i] -= points
        p.score += points
    return scores


STANDARD = Board(BOARD, [Player('p1', AI.greedy),
                         Player('p2', AI.greedy)])


def play_game(board=None, verbose=True):
    """ A number of players play a game; return a list of their scores. """
    start = time.time()
    if board is None:
        board = STANDARD

    while True:
        old_board = board.clone()

        for idx in range(len(board.players)):
            board.cur_p_idx = idx
            p = board.players[idx]
            play = p.strategy(board)
            board.make_one_play(play, verbose)
            # all letters have been drawn and one player uses his last letter; game over
            if p.rack == '':
                end = time.time()
                if verbose:
                    print(f'\n#################################\n'
                          f'##  Runtime = {round(end - start, 3)} seconds  ##\n'
                          f'#################################\n')
                return [p.score for p in board.players]

        # No player has a move; game over
        if old_board == board and board.all_exchanges < 0:
            end = time.time()
            if verbose:
                print(f'\n#################################\n'
                      f'##  Runtime = {round(end - start, 3)} seconds  ##\n'
                      f'#################################\n')
            return [p.score for p in board.players]

