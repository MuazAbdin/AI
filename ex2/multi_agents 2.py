import math

import numpy as np
import abc
import util
from game import Agent, Action


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def get_action(self, game_state):
        """
        You do not need to change this method, but you're welcome to.

        get_action chooses among the best options according to the evaluation function.

        get_action takes a game_state and returns some Action.X for some X in the set
        {UP, DOWN, LEFT, RIGHT, STOP}
        """

        # Collect legal moves and successor states
        legal_moves = game_state.get_agent_legal_actions()

        # Choose one of the best actions
        scores = [self.evaluation_function(game_state, action) for action in legal_moves]
        best_score = max(scores)
        best_indices = [index for index in range(len(scores)) if scores[index] == best_score]
        chosen_index = np.random.choice(best_indices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legal_moves[chosen_index]

    def evaluation_function(self, current_game_state, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (GameState.py) and returns a number, where higher numbers are better.

        """

        # Useful information you can extract from a GameState (game_state.py)

        successor_game_state = current_game_state.generate_successor(action=action)
        board = successor_game_state.board
        size = len(board)
        max_tile = successor_game_state.max_tile
        score = successor_game_state.score
        empty_tiles = successor_game_state.get_empty_tiles()[0].size

        # uniformity is number of tiles with uniform value
        uniformity = 0
        uniform_tiles = [0] * 15
        for tile in np.nditer(board):
            if tile > 0:
                idx = int(math.log(tile, 2)) - 1
                uniform_tiles[idx] += 1
        for num in uniform_tiles:
            uniformity += 1 if num != 0 else 0

        # max_corners is number of corners with highest values
        corners = [board[0][0], board[0][size-1], board[size-1][0], board[size-1][size-1]]
        max_corners = 0
        for i in range(15, 0, -1):
            if max_corners == 4:
                break
            max_corners += 1 if 2**i in corners else 0

        # cluster of different adjacent tiles
        cluster = 0
        for i in range(size):
            for j in range(size-1):
                cluster += abs(board[i][j]-board[i][j+1])
        for j in range(size):
            for i in range(size-1):
                cluster += abs(board[i][j]-board[i+1][j])

        monotonicity = -1
        # board_copy = board.copy()
        for rotate in range(4):
            current = 0
            for i in range(size):
                for j in range(size-1):
                    if board[i][j] >= board[i][j+1]:
                        current += 1
            for j in range(size):
                for i in range(size-1):
                    if board[i][j] >= board[i+1][j]:
                        current += 1
            monotonicity = max(current, monotonicity)
            np.rot90(board)

        # try if there better weight matrix
        weights = np.array([[2**15, 2**14, 2**13, 2**12],
                            [2**8, 2**9, 2**10, 2**11],
                            [2**7, 2**6, 2**5, 2**4],
                            [2**0, 2**1, 2**2, 2**3]])
        weight_monotone = np.sum(weights*board)

        h1 = score
        h2 = max_tile
        h3 = empty_tiles
        h4 = max_corners
        h5 = cluster
        h6 = monotonicity
        h7 = uniformity
        h8 = weight_monotone
        # return h1 - h5 + h8 + h3
        return h1 - h5 + h6 + h3 + h4 + h7


def score_evaluation_function(current_game_state):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return current_game_state.score


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinmaxAgent, AlphaBetaAgent & ExpectimaxAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evaluation_function='scoreEvaluationFunction', depth=2):
        self.evaluation_function = util.lookup(evaluation_function, globals())
        self.depth = depth

    @abc.abstractmethod
    def get_action(self, game_state):
        return


class MinmaxAgent(MultiAgentSearchAgent):
    def get_action(self, game_state):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        game_state.get_legal_actions(agent_index):
            Returns a list of legal actions for an agent
            agent_index=0 means our agent, the opponent is agent_index=1

        Action.STOP:
            The stop direction, which is always legal

        game_state.generate_successor(agent_index, action):
            Returns the successor game state after an agent takes an action
        """
        """*** YOUR CODE HERE ***"""
        action = self.get_max_action(game_state, self.depth)[2]
        if action is None:
            return Action.STOP
        else:
            return action

    def get_max_action(self, game_state, depth):
        legal_actions = game_state.get_legal_actions(0)
        if depth == 0 or not legal_actions:
            return self.evaluation_function(game_state), None, None
        else:
            chosen_successor = None
            chosen_successor_score = 0
            chosen_action = None
            for action in legal_actions:
                successor = game_state.generate_successor(action=action)
                if chosen_action is None:
                    chosen_successor, chosen_successor_score, chosen_action = \
                        successor, self.get_min_action(successor, depth)[0], action
                else:
                    successor_score = self.get_min_action(successor, depth)[0]
                    if successor_score > chosen_successor_score:
                        chosen_successor, chosen_successor_score, chosen_action = successor, successor_score, action
            return chosen_successor_score, chosen_successor, chosen_action

    def get_min_action(self, game_state, depth):
        legal_actions = game_state.get_legal_actions(1)
        if not legal_actions:
            return self.evaluation_function(game_state), None, None
        else:
            depth -= 1
            chosen_action = None
            chosen_successor = None
            chosen_successor_score = 0
            for action in legal_actions:
                successor = game_state.generate_successor(agent_index=1, action=action)
                if chosen_action is None:
                    chosen_successor, chosen_successor_score, chosen_action = \
                        successor, self.get_max_action(successor, depth)[0], action
                else:
                    successor_score = self.get_max_action(successor, depth)[0]
                    if successor_score < chosen_successor_score:
                        chosen_successor, chosen_successor_score, chosen_action = successor, successor_score, action
            return chosen_successor_score, chosen_successor, chosen_action


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """
    AGENT, OPPONENT = 0, 1

    def get_action(self, game_state):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        """*** YOUR CODE HERE ***"""
        # The first turn is agent's (MAXIMIZER)
        return self._alpha_beta(game_state, self.depth, -np.inf, np.inf, self.AGENT)[0]

    def _alpha_beta(self, state, depth, alpha, beta, ply):
        # I. The agent (Maximizer) turn
        if ply == self.AGENT:
            # check terminal states
            if depth == 0:
                return Action.STOP, self.evaluation_function(state)
            legal_actions = state.get_legal_actions(self.AGENT)
            if not legal_actions:
                return Action.STOP, self.evaluation_function(state)
            # choose maximum candidate
            max_score = -np.inf
            best_action = Action.STOP
            for action in legal_actions:
                opponent = state.generate_successor(self.AGENT, action)
                opponent_score = self._alpha_beta(opponent, depth-1, alpha, beta, self.OPPONENT)[1]
                if opponent_score > max_score:
                    max_score = opponent_score
                    best_action = action
                # prune off non promising branches
                if max_score >= beta:
                    return best_action, max_score
                alpha = max(alpha, max_score)
            return best_action, max_score

        # II. The opponent (Minimizer) turn
        if ply == self.OPPONENT:
            # No need to check if terminal according to exercise's notes
            # No need to return action, because we interested in the agent with
            # the first turn, which is the MAXIMIZER
            legal_actions = state.get_legal_actions(self.OPPONENT)
            min_score = np.inf
            for action in legal_actions:
                successor = state.generate_successor(self.OPPONENT, action)
                min_score = min(min_score,
                                self._alpha_beta(successor, depth, alpha, beta, self.AGENT)[1])
                # pruning off
                if min_score <= alpha:
                    return None, min_score
                beta = min(beta, min_score)
            return None, min_score


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
    Your expectimax agent (question 4)
    """
    AGENT, OPPONENT = 0, 1

    def get_action(self, game_state):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        The opponent should be modeled as choosing uniformly at random from their
        legal moves.
        """
        """*** YOUR CODE HERE ***"""
        # The first turn is agent's (MAXIMIZER)
        return self._expectimax(game_state, self.depth, self.AGENT)[0]

    def _expectimax(self, state, depth, ply):
        # I. The agent (Maximizer) turn
        if ply == self.AGENT:
            # check terminal states
            if depth == 0:
                return Action.STOP, self.evaluation_function(state)
            legal_actions = state.get_legal_actions(self.AGENT)
            if not legal_actions:
                return Action.STOP, self.evaluation_function(state)
            # choose maximum candidate
            max_score = -np.inf
            best_action = Action.STOP
            for action in legal_actions:
                opponent_state = state.generate_successor(self.AGENT, action)
                opponent_score = self._expectimax(opponent_state, depth - 1, self.OPPONENT)[1]
                if opponent_score > max_score:
                    max_score = opponent_score
                    best_action = action
            return best_action, max_score
        # II. The opponent (CHANCE NODES) turn
        if ply == self.OPPONENT:
            # No need to check if terminal according to exercise's notes
            # No need to return action, because we interested in the agent with
            # the first turn, which is the MAXIMIZER
            legal_actions = state.get_legal_actions(self.OPPONENT)
            expected_score = 0
            for action in legal_actions:
                successor = state.generate_successor(self.OPPONENT, action)
                expected_score += self._expectimax(successor, depth, self.AGENT)[1]
            # for simplicity assume a uniform probability
            expected_score /= len(legal_actions)
            return None, expected_score


def better_evaluation_function(current_game_state):
    """
    Your extreme 2048 evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviation
better = better_evaluation_function
