from math import *

TAIL_IDX = 100


class Node:
    def __init__(self, parent=None, game_state=None, initiating_move=None):
        self.ancestors = parent.ancestors + [parent] if parent else [parent]
        self.parent = parent  # parent node
        self.game_state = game_state
        self.initiating_move = initiating_move  # the move that got created the state from parent
        self.current_player = game_state.cur_p_idx

        all_moves = list(game_state.all_plays())
        tail = max(-len(all_moves), -TAIL_IDX)
        self.remaining_moves = sorted(all_moves, key=lambda play: game_state.score(play))[tail:]

        self.child_nodes = []
        self.score = 0
        self.visits = 0

    def select_child(self):
        """
        :return: the highest score child
        """
        return sorted(self.child_nodes,
                      key=lambda f: f.score / f.visits + sqrt(2 * log(self.visits) / f.visits))[-1]

    def add_child(self, move, game_state):
        """
        :param move: the generating move for the child node
        :param game_state: the game state for said child node
        :return: the generated child node
        """
        child_node = Node(self, game_state, move)
        self.remaining_moves.remove(move)
        self.child_nodes.append(child_node)
        return child_node

    def update_node(self, score):
        self.score += score
        self.visits += 1
