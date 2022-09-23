import random
from node import Node
import heuristics


############################################
## The greedy algo: highest scoring move  ##
############################################

def greedy(state):
    return max(state.all_plays(), key=lambda play: state.score(play))


##############################
## Monte Carlo Tree Search  ##
##############################

MAX_ITERATIONS = 300


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
            node = node.select_child()
            state.make_one_play(node.initiating_move)
        # print(f'... SELECTION: depth reached: {len(node.ancestors)}')
        # print('... SELECTION DONE ...')

        # II. Expand stage:
        # if we can expand (i.e. state/node is non-terminal)
        if node.remaining_moves:
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
            # move = random.choice(all_moves)  # light playout
            # move = heuristics.heavy_playout(state)  # heavy playout
            move = max(all_moves, key=lambda play: state.score(play))
            state.make_one_play(move, verbose=False)
        # print('... SIMULATION DONE ...')

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

    return best.initiating_move
