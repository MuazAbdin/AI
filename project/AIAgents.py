from node import Node
# import board as b
import random


############################################
## The greedy algo: highest scoring move  ##
############################################

def greedy(state):
    # rack = state.current_player.rack
    return max(state.all_plays(), key=lambda play: state.score(play))


##############################
## Monte Carlo Tree Search  ##
##############################

MAX_ITERATIONS = 100


def UCT(initial_state):
    root_node = Node(game_state=initial_state)

    for i in range(MAX_ITERATIONS):
        print(f'### ITERATION {i} ###')
        node = root_node
        state = initial_state.clone()

        # I. Select stage:
        # node is fully expanded and non-terminal
        while (not node.remaining_moves) and node.child_nodes:
            node = node.select_child()
            state.make_one_play(node.initiating_move)
        print('... SELECTION DONE ...')

        # II. Expand stage:
        # if we can expand (i.e. state/node is non-terminal)
        if node.remaining_moves:
            move = random.choice(node.remaining_moves)
            state.make_one_play(move)
            node = node.add_child(move, state)  # add child and descend tree
        print('... EXPANSION DONE ...')

        # III. Rollout (Simulation) stage:
        # while state is non-terminal
        # print('all moves', len(list(state.all_plays())))
        while list(state.all_plays()):
            """
            This is done as a typical Monte Carlo simulation, either purely random or 
            with some simple weighting heuristics if a light playout is desired, or by 
            using some computationally expensive heuristics and evaluations for a 
            heavy playout. For games with a lower branching factor, a light playout can 
            give good results
            """
            lst = list(state.all_plays())
            # print('BEFORE >>', len(lst))
            # if (len(lst)) == 1: print(lst)
            # The empty play (no letters, no points) is the only possible play
            if len(lst) == 1 and lst[0].letters == '':
                break
            idx = random.randint(0, len(lst) - 1)
            # print(idx)
            move = list(state.all_plays())[idx]
            # move = random.choice(list(state.all_plays())[:1])  # light playout
            # move = state.heavy_playout()  # heavy playout
            state.make_one_play(move, verbose=False)
            # if (len(lst)) <= 5: print(lst)
            print('AFTER >>', len(lst))
        print('... SIMULATION DONE ...')

        # IV. Backpropagation stage:
        # backpropagate from the expanded node and work back to the root node
        while node is not None:
            # state is terminal. Update node with result from POV of node.current_player
            node.update_node(state.get_result(node.current_player))
            node = node.parent
        print('... BACKPROPAGATION DONE ...')

    # return the move that was most visited
    return sorted(root_node.child_nodes, key=lambda c: c.visits)[-1].move
