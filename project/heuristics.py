import re

BALANCED_FIRST_VALUE_DICT = {
    'A': 1.0, 'B': -3.5, 'C': -0.5, 'D': 0.0, 'E': 4.0,
    'F': -2.0, 'G': -2.0, 'H': 0.5, 'I': -0.5, 'J': -3.0,
    'K': -2.5, 'L': -1.0, 'M': -1.0, 'N': 0.5, 'O': -1.5,
    'P': -1.5, 'Q': -11.5, 'R': 1.5, 'S': 7.5, 'T': 0.0,
    'U': -3.0, 'V': -5.5, 'W': -4.0, 'X': 3.5, 'Y': -2.0,
    'Z': 2.0, '_': 24.5
}

BALANCED_CONSECUTIVE_VALUE_DICT = {
    'A': -3.0, 'B': -3.0, 'C': -3.5, 'D': -2.5, 'E': -2.5,
    'F': -2.0, 'G': -2.5, 'H': -3.5, 'I': -4.0, 'J': -3.0,
    'K': -2.5, 'L': -2.0, 'M': -2.0, 'N': -2.5, 'O': -3.5,
    'P': -2.5, 'Q': -11.5, 'R': -3.5, 'S': -4.0, 'T': -2.5,
    'U': -3.0, 'V': -3.5, 'W': -4.5, 'X': 3.5, 'Y': -4.5,
    'Z': 2.0, '_': -15.0
}


def balanced_rack_heuristic(rack: str):
    letters = len(rack)
    letter_counter = {letter: rack.count(letter) for letter in rack}
    vowels = len(re.findall(r'[aeiouAEIOU]', rack))

    balance = 0
    for letter, count in letter_counter.items():
        v1 = BALANCED_FIRST_VALUE_DICT[letter]
        v2 = BALANCED_CONSECUTIVE_VALUE_DICT[letter]
        for i in range(count):
            balance += v1 + i * v2

    # from: Gordon (1993) p.80 :
    # https://www.aaai.org/Papers/Symposia/Fall/1993/FS-93-02/FS93-02-011.pdf
    ratio_score = min(3 * vowels + 1 - letters, 2 * letters - 3 * vowels)

    return balance + ratio_score


HOLDING_U_INCENTIVE = 6


def holding_u_for_q_heuristic(board, play):
    rack = play.rack + play.letters
    if 'U' not in rack or 'Q' in board:
        return 0
    elif ('Q' in play.letters and 'U' in play.rack) or ('Q' in play.rack and 'U' in play.letters):
        return 0
    return HOLDING_U_INCENTIVE


ANCHORS_INCENTIVE_DICT = {':': 1, ';': 2, '-': 4, '=': 6}


def advantages_anchors_heuristic(game_board):
    # import inside function to avoid circular imports
    import board
    incentives_sum = 0
    anchors = board.all_anchors(game_board)
    for anchor in anchors:
        incentives_sum += ANCHORS_INCENTIVE_DICT.get(anchor, default=0)
    return incentives_sum


def heavy_playout(game_board, candidate_moves):
    """
    we will apply a three heuristics in order, the next will evaluate the previous result
    """
    # the rack we evaluate is the partial one immediately after making a move
    # and before replenish because we have no knowledge about what comes from the bag

    m = max(candidate_moves, key=lambda play: (balanced_rack_heuristic(play.rack) +
                                               holding_u_for_q_heuristic(game_board,
                                                                         play) +
                                               game_board.score(play)))

    return m


if __name__ == '__main__':
    print(balanced_rack_heuristic('IIISS'))
