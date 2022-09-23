import random
from collections import defaultdict, namedtuple
from IPython.display import HTML, display
from typing import List


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


ACROSS = 1  # The 'across' direction; 'down' depends on the size of the board
OFF = '#'  # A square that is off the board
SL, DL, TL, STAR, DW, TW = EMPTY = '.:;*-='
# Single/double/triple letter; star, double/triple word bonuses

Square = int  # Squares are implemented as integer indexes.
Direction = int  # Directions are implemented as integer increments


def board_html(board) -> str:
    """ An HTML representation of the board. """
    size = board.down - 2
    squares = [square_html(sq) for sq in board if sq != OFF]
    row = ('<tr>' + '{}' * size)
    return ('<table>' + row * size + '</table>').format(*squares)


board_colors = {
    DL: ('lightblue', 66, 'DL'),
    TL: ('lightgreen', 66, 'TL'),
    DW: ('lightcoral', 66, 'DW'),
    TW: ('orange', 66, 'TW'),
    SL: ('whitesmoke', 66, ''),
    STAR: ('violet', 100, '&#10029;')}


def square_html(sq) -> str:
    "An HTML representation of a square."
    color, size, text = board_colors.get(sq, ('gold', 120, sq))
    if text.isupper():
        text = '<b>{}</b><sub style="font-size: 60%">{}</sub>'.format(text, POINTS.get(text, ''))
    style = ("background-color:{}; font-size:{}%; width:25px; height:25px; "
             "text-align:center; padding:0px; border-style:solid; border-width: thin")
    return ('<td bgcolor="{}" style="' + style + '">{}').format(color, color, size, text)


POINTS = defaultdict(int,
                     A=1, B=3, C=3, D=2, E=1, F=4, G=2, H=4, I=1, J=8, K=5, L=1, M=3,
                     N=1, O=1, P=3, Q=10, R=1, S=1, T=1, U=1, V=4, W=4, X=8, Y=4, Z=10)

Play = namedtuple('Play', 'start, dir, letters, rack')


class Board(list):
    """
    A Board is a (linear) list of squares, each a single character.
    Note that board[s + down] is directly below board[s].
    """

    def __init__(self, squares: List[str]):
        list.__init__(self, squares)
        down = int(len(squares) ** 0.5)
        self.down = down
        self.directions = (ACROSS, down, -ACROSS, -down)

        self.current_player = 0

    def set_player(self, player: int) -> None:
        self.current_player = player

    def get_current_player(self) -> int:
        return self.current_player

    def clone(self):
        """ Returns a deep copy of the current board """
        copy = Board(self)
        copy.current_player = self.current_player
        # copy.set_player(self.get_current_player())
        return copy

    def _repr_html_(self) -> str:
        return board_html(self)

    def make_play(self, play: Play) -> List[str]:
        """ Make the play on a copy of board and return the copy. """
        # copy = Board(board)
        copy = self.clone()
        # TODO: update current_player to next player ..
        end = play.start + len(play.letters) * play.dir
        copy[play.start:end:play.dir] = play.letters
        return copy

    def all_plays(self, rack):
        """
        Generate all plays that can be played on board with this rack.
        Try placing every possible prefix before every anchor point;
        then extend one letter at a time, looking for valid plays.
        """
        anchors = all_anchors(self)
        prefixes = rack_prefixes(rack)
        yield Play(0, ACROSS, '', rack)  # The empty play (no letters, no points)
        for anchor in anchors:
            for dir in (ACROSS, self.down):
                for play in prefix_plays(prefixes, self, anchor, dir, rack):
                    yield from extend_play(self, play)

    def score(board, play) -> int:
        """ The number of points scored by making this play on the board. """
        return (word_score(board, play)
                + bingo(board, play)
                + sum(word_score(board, cplay)
                      for cplay in cross_plays(board, play)))

    # ---------- Enf of Board Class ---------- #


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
        word_bonus *= (3 if sq == TW else 2 if sq == DW else 1)
        total += POINTS[L] * (3 if sq == TL else 2 if sq == DL else 1)
    return word_bonus * total


def bingo(board, play) -> int:
    """ A bonus for using 7 letters from the rack. """
    return BINGO if (play.rack == '' and letters_played(board, play) == 7) else 0


BINGO = 35  # 35 for Words with Friends; 50 for Scrabble


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


def highest_scoring_play(board, rack) -> Play:
    """ Return the Play that gives the most points. """
    return max(all_plays(board, rack), key=lambda play: score(board, play))


BAG = 'AAAAAAAAA' \
      'BB' \
      'CC' \
      'DDDD' \
      'EEEEEEEEEEEE' \
      'FF' \
      'GGG' \
      'HH' \
      'IIIIIIIII' \
      'J' \
      'K' \
      'LLLL' \
      'MM' \
      'NNNNNN' \
      'OOOOOOOO' \
      'PP' \
      'Q' \
      'RRRRRR' \
      'SSSS' \
      'TTTTTT' \
      'UUUU' \
      'VV' \
      'WW' \
      'X' \
      'YY' \
      'Z' \
      '__'

WWF = Board("""
    # # # # # # # # # # # # # # # # #
    # . . . = . . ; . ; . . = . . . #
    # . . : . . - . . . - . . : . . #
    # . : . . : . . . . . : . . : . #
    # = . . ; . . . - . . . ; . . = #
    # . . : . . . : . : . . . : . . #
    # . - . . . ; . . . ; . . . - . #
    # ; . . . : . . . . . : . . . ; #
    # . . . - . . . * . . . - . . . #
    # ; . . . : . . . . . : . . . ; #
    # . - . . . ; . . . ; . . . - . #
    # . . : . . . : . : . . . : . . #
    # = . . ; . . . - . . . ; . . = #
    # . : . . : . . . . . : . . : . #
    # . . : . . - . . . - . . : . . #
    # . . . = . . ; . ; . . = . . . #
    # # # # # # # # # # # # # # # # #
    """.split())


def play_game(strategies=[highest_scoring_play] * 2, verbose=True, seed=None) -> list:
    """ A number of players play a game; return a list of their scores. """
    board = Board(WWF)
    bag = list(BAG)
    random.seed(seed)
    random.shuffle(bag)
    scores = [0 for _ in strategies]
    racks = [replenish('', bag) for _ in strategies]
    while True:
        old_board = board
        for (p, strategy) in enumerate(strategies):
            board = make_one_play(board, p, strategy, scores, racks, bag, verbose)
            if racks[p] == '':
                # Player p has gone out; game over
                return subtract_remaining_tiles(racks, scores, p)
        if old_board == board:
            # No player has a move; game over
            return scores


def make_one_play(board, p, strategy, scores, racks, bag, verbose) -> Board:
    """
    One player, player p, chooses a move according to the strategy.
    We make the move, replenish the rack, update scores, and return the new Board.
    """
    rack = racks[p]
    play = strategy(board, racks[p])
    racks[p] = replenish(play.rack, bag)
    points = score(board, play)
    scores[p] += points
    board = make_play(board, play)
    if verbose:
        display(HTML('Player {} with rack {} makes {}<br>for {} points; draws: {}; scores: {}'
                     .format(p, rack, play, points, racks[p], scores)),
                board)
    return board


def subtract_remaining_tiles(racks, scores, p) -> list:
    """ Subtract point values from each player and give them to player p. """
    for i in range(len(racks)):
        points = sum(POINTS[L] for L in racks[i])
        scores[i] -= points
        scores[p] += points
    return scores


def replenish(rack, bag) -> str:
    """ Fill rack with 7 letters (as long as there are letters left in the bag). """
    while len(rack) < 7 and bag:
        rack += bag.pop()
    return rack


if __name__ == '__main__':    
    # print(len(DICTIONARY))
    # print(list(DICTIONARY)[:10])
    # print('WORD' in DICTIONARY)

    # print(is_word('LETTERs'))
    # print(letters('LETTERS'))
    # print(letters('EELRTT_'))
    # print(remove('SET', 'LETTERS'))
    # print(remove('TREaT', 'LETTER_'))

    # WWF = Board("""
    # # # # # # # # # # # # # # # # # #
    # # . . . = . . ; . ; . . = . . . #
    # # . . : . . - . . . - . . : . . #
    # # . : . . : . . . . . : . . : . #
    # # = . . ; . . . - . . . ; . . = #
    # # . . : . . . : . : . . . : . . #
    # # . - . . . ; . . . ; . . . - . #
    # # ; . . . : . . . . . : . . . ; #
    # # . . . - . . . * . . . - . . . #
    # # ; . . . : . . . . . : . . . ; #
    # # . - . . . ; . . . ; . . . - . #
    # # . . : . . . : . : . . . : . . #
    # # = . . ; . . . - . . . ; . . = #
    # # . : . . : . . . . . : . . : . #
    # # . . : . . - . . . - . . : . . #
    # # . . . = . . ; . ; . . = . . . #
    # # # # # # # # # # # # # # # # # #
    # """.split())
    # assert len(WWF) == 17 * 17
    # print(board_html(WWF))
    # print(WWF)

    # print(len(PREFIXES))
    # print(dict_prefixes({'HELLO', 'HELP', 'HELPER'}))

    # rack = 'ABC'
    # print(rack_prefixes(rack))
    # print(len(rack_prefixes('LETTERS')))
    # print(len(rack_prefixes('LETTER_')))

    # print(all_anchors(WWF))

    # DOWN = WWF.down
    # plays = {Play(145, DOWN, 'ENTER', ''),
    #          Play(144, ACROSS, 'BE', ''),
    #          Play(138, DOWN, 'GAVE', ''),
    #          Play(158, DOWN, 'MUSES', ''),
    #          Play(172, ACROSS, 'VIRULeNT', ''),
    #          Play(213, ACROSS, 'RED', ''),
    #          Play(198, ACROSS, 'LYTHE', ''),
    #          Play(147, DOWN, 'CHILDREN', ''),
    #          Play(164, ACROSS, 'HEARD', ''),
    #          Play(117, DOWN, 'BRIDLES', ''),
    #          Play(131, ACROSS, 'TOUR', '')}
    #
    # board = Board(WWF)
    # for play in plays:
    #     board = make_play(board, play)

    # anchors = all_anchors(board)
    # print(len(anchors))

    # play_game(seed=2)

    Ngames = 20
    results = [play_game(verbose=False, seed=None) for _ in range(Ngames)]
    scores = sorted(score for pair in results for score in pair)

    print(f'min: {min(scores)}, median: {scores[Ngames]}, max: {max(scores)}')
