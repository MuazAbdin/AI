import itertools
import random
from node import Node
import heuristics


############################################
## The greedy algo: highest scoring move  ##
############################################

def greedy(state):
    return max(state.all_plays(), key=lambda play: state.score(play))


######################################################
##           Monte Carlo Tree Search:               ##
##  UCT (Upper Confidence bounds applied to Trees)  ##
######################################################

MAX_ITERATIONS = 200


def UCT(initial_state):
    root_node = Node(game_state=initial_state)

    print(f'ITERATION: ', end='')
    for i in range(MAX_ITERATIONS):
        if i % 50 == 0: print(i, end=' ')
        node = root_node
        state = initial_state.clone()

        # I. Select stage:
        # node is fully expanded and non-terminal
        while (not node.remaining_moves) and node.child_nodes:
            # print('in selection')
            node = node.select_child()
            state.make_one_play(node.initiating_move)
        # print(f'... SELECTION: depth reached: {len(node.ancestors)}')
        # print('... SELECTION DONE ...')

        # II. Expand stage:
        # if we can expand (i.e. state/node is non-terminal)
        if node.remaining_moves:
            # print('in expansion')
            move = random.choice(node.remaining_moves)
            state.make_one_play(move)
            node = node.add_child(move, state)  # add child and descend tree
        # print('... EXPANSION DONE ...')

        # III. Rollout (Simulation) stage: 3 lookahead moves
        for depth in range(2):
            all_moves = list(state.all_plays())
            # print(len(all_moves))
            # The empty play (no letters, no points) is the only possible play
            if len(all_moves) == 1 and all_moves[0].letters == '':
                break
            # take just the highest 100
            all_moves = sorted(all_moves, key=lambda play: state.score(play))
            all_moves = all_moves[max(-len(all_moves), -100):]
            move = random.choice(all_moves)  # light playout
            # move = heuristics.heavy_playout(state, all_moves)  # heavy playout
            # move = max(all_moves, key=lambda play: state.score(play))
            state.make_one_play(move, verbose=False)
        # print('... SIMULATION DONE ...')

        # # while state is non-terminal
        # while list(state.all_plays()):
        #     """
        #     This is done as a typical Monte Carlo simulation, either purely random or
        #     with some simple weighting heuristics if a light playout is desired, or by
        #     using some computationally expensive heuristics and evaluations for a
        #     heavy playout. For games with a lower branching factor, a light playout can
        #     give good results
        #     """
        #     all_moves = list(state.all_plays())
        #     # The empty play (no letters, no points) is the only possible play
        #     if len(all_moves) == 1 and all_moves[0].letters == '':
        #         break
        #     move = random.choice(all_moves)  # light playout
        #     # move = state.heavy_playout()  # heavy playout
        #     state.make_one_play(move, verbose=False)
        # # print('... SIMULATION DONE ...')

        # IV. Backpropagation stage:
        # backpropagate from the expanded node and work back to the root node
        while node is not None:
            # state is terminal. Update node with result from POV of node.current_player
            player = state.players[node.current_player]
            node.update_node(state.get_result(player))
            node = node.parent
        # print('... BACKPROPAGATION DONE ...')

    print()

    # return the move that was most visited and scores the most
    most_visited = sorted(root_node.child_nodes, key=lambda c: c.visits)
    best = most_visited[-1]

    for node in reversed(most_visited):
        if node.visits < best.visits: break
        if node.score > best.score: best = node

    # print(f'visits= {best.visits}, ancestors= {len(best.ancestors)-1}')
    return best.initiating_move


############################
##  ExpictiMax
###################

DEPTH = 2
AGENT, OPPONENT = 0, 1
INF = float("inf")
TAIL_IDX = 20
SAMPLE_SIZE = 200


def expictimax(game_state):
    state = game_state.clone()
    # The first turn is agent's (MAXIMIZER)
    return _expectimax_helper(state, DEPTH, AGENT)[0]


def _expectimax_helper(state, depth, ply):
    # print(f'ply: {ply} depth: {depth}')
    import board
    p = state.players[0]
    # print(f'p.rack: {p.rack}')
    # The empty play (no letters, no points)
    empty_play = board.Play(0, board.ACROSS, '', p.rack)
    # I. The agent (Maximizer) turn
    if ply == AGENT:
        # check terminal states
        # if depth == 0:
        #     print(f'empty_play: {empty_play}, p.score: {p.score}')
        #     return empty_play, p.score

        legal_plays = list(state.all_plays())
        # if legal plays contains only the empty play (see how all_play works)
        if len(legal_plays) == 1 and legal_plays[0].letters == '':
        # if not legal_plays:
            # print(f'empty_play: {empty_play}, p.score: {p.score}')
            return empty_play, p.score

        # choose maximum candidate
        tail = max(-len(legal_plays), -TAIL_IDX)
        legal_plays = sorted(legal_plays, key=lambda play: state.score(play))[tail:]
        max_score = -INF
        best_play = empty_play
        for play in legal_plays:
            opponent_state = state.clone()
            # make play without replenishing
            opponent_state.make_partial_play(play)
            opponent_score = _expectimax_helper(opponent_state, depth - 1, OPPONENT)[1]
            if opponent_score > max_score:
                max_score = opponent_score
                best_play = play
        # print(f'best_play: {best_play}, max_score: {max_score}')
        return best_play, max_score
    # II. The opponent (CHANCE NODES) turn
    if ply == OPPONENT:
        # No need to return action, because we interested in the agent with
        # the first turn, which is the MAXIMIZER
        if depth == 0:
            # print(f' None, p.score: {p.score}')
            return None, p.score
        replenishments = best_replenishments(p.rack, state.bag)
        expected_score = 0
        for letters in map(lambda item: item[1], replenishments):
            successor = state.clone()
            # replenish the rack
            successor.players[0].rack += letters
            for l in letters: successor.bag.remove(l)
            expected_score += _expectimax_helper(successor, depth, AGENT)[1]
        # for simplicity assume a uniform probability
        expected_score /= len(replenishments)
        # print(f'expected_score: {expected_score}')
        return None, expected_score


def best_replenishments(rack, bag):
    """ given a rack and bag return best possible replenishments = new add letters """
    replenishments = []
    empty = 7 - len(rack)

    if len(bag) >= empty:
        # random sampling
        for i in range(SAMPLE_SIZE):
            rep = random.sample(bag, empty)
            replenishments += [''.join(rep)]
    else:
        replenishments = [''.join(bag)]

    replenishments = list(set(replenishments))  # remove duplicates

    racks = [(rack, letters) for letters in replenishments]
    tail = max(-len(racks), -TAIL_IDX)
    racks = sorted(racks, key=lambda r: (heuristics.balanced_rack_heuristic(r[0] + r[1])))

    return racks[tail:]


# if __name__ == '__main__':
    # print(best_replenishments('ABCDE', ['_', 'S', 'F', 'Z']))
#     print(filter_replenishments(['AB', 'CD'], 'ZWE'))
# #     print(all_racks('ABCDE', ['_', 'S', 'F', 'Z']))
# #     print(all_racks('ABC', ['_', 'S']))
