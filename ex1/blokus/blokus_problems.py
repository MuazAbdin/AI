from board import Board
from search import SearchProblem, ucs, astar

from math import sqrt
import util


class BlokusFillProblem(SearchProblem):
    """
    A one-player Blokus game as a search problem.
    This problem is implemented for you. You should NOT change it!
    """

    def __init__(self, board_w, board_h, piece_list, starting_point=(0, 0)):
        self.board = Board(board_w, board_h, 1, piece_list, starting_point)
        self.expanded = 0

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        return self.board

    def is_goal_state(self, state):
        """
        state: Search state
        Returns True if and only if the state is a valid goal state
        """
        return not any(state.pieces[0])

    def get_successors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        # Note that for the search problem, there is only one player - #0
        self.expanded = self.expanded + 1
        return [(state.do_move(0, move), move, 1) for move in state.get_legal_moves(0)]

    def get_cost_of_actions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        return len(actions)


#####################################################
# This portion is incomplete.  Time to write code!  #
#####################################################
class BlokusCornersProblem(SearchProblem):
    def __init__(self, board_w, board_h, piece_list, starting_point=(0, 0)):
        self.board = Board(board_w, board_h, 1, piece_list, starting_point)
        self.expanded = 0
        self.PLAYER_ID = 0
        self.corners = [(0, 0), (board_w - 1, 0), (0, board_h - 1), (board_w - 1, board_h - 1)]

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        return self.board

    def is_goal_state(self, state):
        """
        checks if all the corners are occupied by the player, return True if the are False otherwise
        """
        for x, y in self.corners:
            if state.get_position(x, y) != self.PLAYER_ID:
                return False
        return True

    def get_successors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        # Note that for the search problem, there is only one player - #0
        self.expanded = self.expanded + 1
        return [(state.do_move(0, move), move, move.piece.get_num_tiles()) for move in
                state.get_legal_moves(0)]

    def get_cost_of_actions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        total_cost = 0
        for move in actions:
            # sums the total number of tiles covered (given that there is no overlapping)
            total_cost += move.piece.get_num_tiles
        return total_cost


def distance(xy1, xy2):
    """
    returns weighted average of euclidean, manhattan and chebyshev norms.
    """
    manhattan = abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])
    chebyshev = max(abs(xy1[0] - xy2[0]), abs(xy1[1] - xy2[1]))
    euclidean = sqrt((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2)
    # return weighted average
    return (2 * manhattan + 6 * chebyshev + 2 * euclidean) / 10


def blokus_corners_heuristic(state, problem):
    """
    returns the sum of median distance of groups of corners that can be
    reached with the same playing piece, unless the state of the board is
    such that finishing cannot be done, then return the maximum possible.
    """
    # IDEA: distance from placed pieces to the vacant corners
    # cost is the sum of min dist from the placed pieces to each of vacant corners
    cost = 0
    vacant_corners = [corner for corner in problem.corners
                      if state.get_position(corner[0], corner[1]) == -1]
    # at least one unreachable corner, path is not useful
    for corner in vacant_corners:
        if not is_reachable(state, *corner):
            # longest possible path in the board
            return state.board_w * state.board_h

    # get set of closest targets lists
    target_groups = []
    for t_1 in vacant_corners:
        closest_t_1 = []
        for t_2 in vacant_corners:
            # 5 is the maximum possible distance between two tiles of a piece
            # take a look on the blokus pieces on th web
            if distance(t_1, t_2) < 5:
                closest_t_1.append(t_2)
        # sort according to dist from (0,0)
        closest_t_1.sort(key=lambda x: distance(x, (0, 0)))
        if closest_t_1 not in target_groups:
            target_groups.append(closest_t_1)

    occupied_tiles = []
    for x in range(state.board_w):
        for y in range(state.board_h):
            if state.get_position(x, y) == 0:
                occupied_tiles.append((x, y))

    for group in target_groups:
        # get median of the group
        target = group[len(group) // 2]
        min_dist = state.board_w * state.board_h
        for tile in occupied_tiles:
            min_dist = min(min_dist, distance(target, tile))
        cost += min_dist

    return cost


def is_reachable(state, x, y):
    """
    check if any of side adjacents is occupied
    """
    w = state.board_w
    h = state.board_h
    sides = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for adjacent in sides:
        j, i = adjacent
        if (0 <= i < w) and (0 <= j < h):
            if state.get_position(i, j) != -1:
                return False
    return True


class BlokusCoverProblem(SearchProblem):
    def __init__(self, board_w, board_h, piece_list, starting_point=(0, 0), targets=[(0, 0)]):
        self.board = Board(board_w, board_h, 1, piece_list, starting_point)
        self.targets = targets.copy()
        self.expanded = 0
        self.PLAYER_ID = 0

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        return self.board

    def change_board(self, board):
        self.board = board

    def is_goal_state(self, state):
        """
        checks if all the targets are occupied by the player, return True if the are False otherwise
        """
        for target in self.targets:
            if state.get_position(target[1], target[0]) != self.PLAYER_ID:
                return False
        return True

    def get_successors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        # Note that for the search problem, there is only one player - #0
        self.expanded = self.expanded + 1
        return [(state.do_move(0, move), move, move.piece.get_num_tiles()) for move in
                state.get_legal_moves(0)]

    def get_cost_of_actions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        total_cost = 0
        for move in actions:
            # sums the total number of tiles covered (given that there is no overlapping)
            total_cost += move.piece.get_num_tiles()
        return total_cost


def blokus_cover_heuristic(state, problem):
    """
    returns the max of median distance of groups of targets that can be
    reached with the same playing piece.
    score is also considering the amount of targets yet unreached.
    unless the state of the board is such that finishing cannot be done,
    then return the maximum possible.
    """
    # IDEA: distance from placed pieces to the vacant corners
    cost = 0
    vacant_targets = [target for target in problem.targets
                      if state.get_position(target[1], target[0]) == -1]
    # at least one unreachable corner, path is not useful
    for target in vacant_targets:
        if not is_reachable(state, *target):
            # longest path in the board multiply number of vacant targets
            return state.board_w * state.board_h

    # get set of closest targets lists
    target_groups = []
    for t_1 in vacant_targets:
        closest_t_1 = []
        for t_2 in vacant_targets:
            if distance(t_1, t_2) < 5:
                closest_t_1.append(t_2)
        # sort according to dist from (0,0)
        closest_t_1.sort(key=lambda x: distance(x, (0, 0)))
        if closest_t_1 not in target_groups:
            target_groups.append(closest_t_1)

    occupied_tiles = []
    for x in range(state.board_w):
        for y in range(state.board_h):
            if state.get_position(x, y) == 0:
                occupied_tiles.append((x, y))

    for group in target_groups:
        # get median of the group
        target = group[len(group) // 2]
        min_dist = state.board_w * state.board_h
        for tile in occupied_tiles:
            min_dist = min(min_dist, distance(target, tile))
        if cost < min_dist:
            cost = min_dist

    # average of two heuristics: min of dists to left goals, and left goals
    return (cost + len(vacant_targets)) // 2


class ClosestLocationSearch:
    """
    In this problem you have to cover all given positions on the board,
    but the objective is speed, not optimality.
    """
    def __init__(self, board_w, board_h, piece_list, starting_point=(0, 0), targets=(0, 0)):
        self.board = Board(board_w, board_h, 1, piece_list, starting_point)
        self.starting_point = starting_point
        self.expanded = 0
        self.targets = targets.copy()
        # make targets iterable (if there is more than one, it is already list)
        if len(self.targets) == 1:
            self.targets = [self.targets]
        self.PLAYER_ID = 0

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        return self.board

    def solve(self):
        """
        return a sequence of actions that covers the given target in the problem.
        where the method id to cover each time the current closest target available.
        """
        def suboptimal_heuristic(state, problem):
            # IDEA: distance from placed pieces to the vacant corners
            # cost is the sum of min dist from the placed pieces to each of vacant corners
            cost = 0
            vacant_targets = [target for target in problem.targets
                              if state.get_position(target[1], target[0]) == -1]
            # at least one unreachable corner, path is not useful
            for target in vacant_targets:
                if not is_reachable(state, *target):
                    # longest path in the board multiply number of vacant targets
                    return state.board_w * state.board_h

            # get set of closest targets lists
            target_groups = []
            for t_1 in vacant_targets:
                closest_t_1 = []
                for t_2 in vacant_targets:
                    if distance(t_1, t_2) < 5:
                        closest_t_1.append(t_2)
                # sort according to dist from (0,0)
                closest_t_1.sort(key=lambda x: distance(x, (0, 0)))
                if closest_t_1 not in target_groups:
                    target_groups.append(closest_t_1)

            occupied_tiles = []
            for x in range(state.board_w):
                for y in range(state.board_h):
                    if state.get_position(x, y) == 0:
                        occupied_tiles.append((x, y))

            for group in target_groups:
                # get median of the group
                target = group[len(group) // 2]
                min_dist = state.board_w + state.board_h
                for tile in occupied_tiles:
                    min_dist = min(min_dist, distance(target, tile))
                cost += min_dist

            # average of two heuristics: sum of dists to left goals, and left goals
            return (cost + len(vacant_targets)) // 2

        current_state = self.board.__copy__()
        backtrace = []
        # iterate over targets
        targets = self.targets.copy()
        targets.sort(key=lambda tile: distance(self.starting_point, tile))
        while targets:
            # initialize a problem that is exactly the current state
            problem = BlokusCoverProblem(current_state.board_w, current_state.board_h,
                                         current_state.piece_list, self.starting_point,
                                         [targets[0]])
            problem.change_board(current_state)
            # get list of actions from current_state to target
            actions = astar(problem, suboptimal_heuristic)
            self.expanded += problem.expanded
            # update the backtrace and the board
            for action in actions:
                backtrace.append(action)
                current_state = current_state.do_move(0, action)
            targets = targets[1:]

        return backtrace


class MiniContestSearch:
    """
    Implement your contest entry here
    """

    def __init__(self, board_w, board_h, piece_list, starting_point=(0, 0), targets=(0, 0)):
        self.board = Board(board_w, board_h, 1, piece_list, starting_point)
        self.starting_point = starting_point
        self.expanded = 0
        self.targets = targets.copy()
        # make targets iterable (if there is more than one, it is already list)
        if len(self.targets) == 1:
            self.targets = [self.targets]
        self.PLAYER_ID = 0

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        return self.board

    def solve(self):
        """
        return a sequence of actions that covers the given target in the problem. where the method id to cover each
        time the current closest target available.
        """

        def suboptimal_heuristic(state, problem):
            # IDEA: distance from placed pieces to the vacant corners
            # cost is the sum of min dist from the placed pieces to each of vacant corners
            cost = 0
            vacant_targets = [target for target in problem.targets
                              if state.get_position(target[1], target[0]) == -1]
            # at least one unreachable corner, path is not useful
            for target in vacant_targets:
                if not is_reachable(state, *target):
                    # longest path in the board multiply number of vacant targets
                    return state.board_w * state.board_h

            # get set of closest targets lists
            target_groups = []
            for t_1 in vacant_targets:
                closest_t_1 = []
                for t_2 in vacant_targets:
                    if distance(t_1, t_2) < 5:
                        closest_t_1.append(t_2)
                # sort according to dist from (0,0)
                closest_t_1.sort(key=lambda x: distance(x, (0, 0)))
                if closest_t_1 not in target_groups:
                    target_groups.append(closest_t_1)

            occupied_tiles = []
            for x in range(state.board_w):
                for y in range(state.board_h):
                    if state.get_position(x, y) == 0:
                        occupied_tiles.append((x, y))

            for group in target_groups:
                # get median of the group
                target = group[len(group) // 2]
                min_dist = state.board_w + state.board_h
                for tile in occupied_tiles:
                    min_dist = min(min_dist, distance(target, tile))
                cost += min_dist

            # average of two heuristics: sum of dists to left goals, and left goals
            return (cost + len(vacant_targets)) // 2

        current_state = self.board.__copy__()
        backtrace = []
        # iterate over targets
        targets = self.targets.copy()
        targets.sort(key=lambda tile: distance(self.starting_point, tile))
        while targets:
            # initialize a problem that is exactly the current state
            problem = BlokusCoverProblem(current_state.board_w, current_state.board_h,
                                         current_state.piece_list, self.starting_point,
                                         [targets[0]])
            problem.change_board(current_state)
            # get list of actions from current_state to target
            actions = astar(problem, suboptimal_heuristic)
            self.expanded += problem.expanded
            # update the backtrace and the board
            for action in actions:
                backtrace.append(action)
                current_state = current_state.do_move(0, action)
            targets = targets[1:]

        return backtrace