import random
from node import Node
import heuristics


############################################
## The greedy algo: highest scoring move  ##
############################################

def greedy(state):
    # rack = state.current_player.rack
    return max(state.all_plays(), key=lambda play: state.score(play))


##############################
## Monte Carlo Tree Search  ##
##############################

MAX_ITERATIONS = 600     # at least 1000
EXPANSION_THRESHOLD = 400  # branching factor ~ 700 : expand half of it


def UCT(initial_state):
    # print('>> START UCT <<')
    # print(hex(id(initial_state)))
    root_node = Node(game_state=initial_state)

    # racks = [p.rack for p in initial_state.players]
    # scores = [p.score for p in initial_state.players]
    # print(f'racks: {racks}, scores: {scores}.\n')

    print(f'ITERATION: ', end='')
    for i in range(MAX_ITERATIONS):
        if i % 50 == 0: print(i, end=' ')
        node = root_node
        state = initial_state.clone()

        fully_unexpanded = len(list(state.all_plays()))

        # I. Select stage:
        # node is fully expanded and non-terminal
        # while (not node.remaining_moves) and node.child_nodes:
        while (len(node.remaining_moves) <= max(fully_unexpanded - EXPANSION_THRESHOLD, 0)) and \
                node.child_nodes:
            node = node.select_child()
            state.make_one_play(node.initiating_move)
        # print(f'... SELECTION: depth reached: {len(node.ancestors)}')
        # print('... SELECTION DONE ...')

        # II. Expand stage:
        # if we can expand (i.e. state/node is non-terminal)
        # if node.remaining_moves:
        if len(node.remaining_moves) > max(fully_unexpanded - EXPANSION_THRESHOLD, 0):
            move = random.choice(node.remaining_moves)
            state.make_one_play(move)
            node = node.add_child(move, state)  # add child and descend tree
        # print('... EXPANSION DONE ...')

        # III. Rollout (Simulation) stage: 3 lookahead moves
        for depth in range(2):
            all_moves = list(state.all_plays())
            # The empty play (no letters, no points) is the only possible play
            if len(all_moves) == 1 and all_moves[0].letters == '':
                break
            best_moves = sorted(all_moves, key=lambda play: state.score(play))
            move = heuristics.heavy_playout(state, best_moves[max(-len(best_moves), -50):])
            # move = random.choice(all_moves)  # light playout
            # move = heuristics.heavy_playout(state)  # heavy playout
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
        # p = state.players[node.current_player]
        # print(f'=> {p.score} | {state.get_result(p)}', end=', ')
        while node is not None:
            # state is terminal. Update node with result from POV of node.current_player
            player = state.players[node.current_player]
            # print(f'=> {player.score} | {state.get_result(player)}', end='')
            node.update_node(state.get_result(player))
            node = node.parent
        # print('... BACKPROPAGATION DONE ...')

        # print('children: ', len(root_node.child_nodes))
        # for c in root_node.child_nodes:
        #     print(c.visits, end=' ')
        # print()

    # racks = [p.rack for p in initial_state.players]
    # scores = [p.score for p in initial_state.players]
    # print(f'racks: {racks}, scores: {scores}.\n')
    # p = sorted(root_node.child_nodes, key=lambda c: c.visits)[-1].initiating_move
    # print('\n>> END UCT >> best is: \n', p)

    # print(len(root_node.child_nodes))
    # for c in root_node.child_nodes:
    #     print(c.visits, end=' ')
    print()
    # return the move that was most visited
    return sorted(root_node.child_nodes, key=lambda c: c.visits)[-1].initiating_move
