from board import Board
from search import SearchProblem, ucs, astar
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


def find_diagonal_tiles_needed(xy1, xy2):
    """
    :param xy1: coordinates set 1
    :param xy2: coordinates set 1
    :return: the minimal amount of tiles required to get from xy1 to xy2
    """
    return max(abs(xy1[0] - xy2[0]), abs(xy1[1] - xy2[1]))


def find_distance_from_goals(state, problem, goals):
    """
    returns a list of distances for the corespondent goals.
    distances are calculated from the tile occupied by the player
    """
    # only if the problem is solved already
    if problem.is_goal_state(state):
        return [0] * len(goals)
    # maximum distance on the board
    max_distance = max(state.board_w, state.board_h)
    distance_from_goals = [max_distance] * len(goals)
    for j in range(len(goals)):
        if state.get_position(goals[j][0], goals[j][1]) == problem.PLAYER_ID:
            distance_from_goals[j] = 0
    for x in range(state.board_w):
        for y in range(state.board_h):
            if state.check_tile_legal(problem.PLAYER_ID, x, y):
                # only for tiles that are occupied by the player
                for i in range(len(goals)):
                    distance_from_goal_i = find_diagonal_tiles_needed([x, y],
                                                                      [goals[i][0], goals[i][1]])
                    if distance_from_goal_i + 1 < distance_from_goals[i]:
                        # check if the distance is lesser, if so updates
                        distance_from_goals[i] = distance_from_goal_i + 1
    return distance_from_goals


def find_distance_from_corners(state, problem):
    """
    returns a list of distances for the corespondent corners
    """
    return find_distance_from_goals(state, problem, problem.corners)


def blokus_corners_heuristic(state, problem):
    """
    Your heuristic for the BlokusCornersProblem goes here.

    This heuristic must be consistent to ensure correctness.  First, try to come up
    with an admissible heuristic; almost all admissible heuristics will be consistent
    as well.

    If using A* ever finds a solution that is worse uniform cost search finds,
    your heuristic is *not* consistent, and probably not admissible!  On the other hand,
    inadmissible or inconsistent heuristics may find optimal solutions, so be careful.
    """
    # IDEA: distance from placed pieces to the vacant corners
    # TODO assure it is admissible and consistent
    # cost is the sum of min dist from the placed pieces to each of vacant corners
    cost = 0
    vacant_corners = [corner for corner in problem.corners
                      if state.get_position(corner[0], corner[1]) == -1]
    # print(vacant_corners)
    occupied_tiles = []
    for x in range(state.board_w):
        for y in range(state.board_h):
            if state.get_position(x, y) == 0:
                occupied_tiles.append((x, y))
    # print(occupied_tiles)
    for corner in vacant_corners:
        if occupied_tiles:
            occupied_tiles.sort(key=lambda tile: util.manhattanDistance(corner, tile))
        # min_dist = max(state.board_w, state.board_h)
        # for tile in occupied_tiles:
        #     # for move in diagonal_moves(*tile):
        #     #     if state.check_tile_legal(0, *move) and state.check_tile_attached(0, *move):
        #     min_dist = min(min_dist, find_diagonal_tiles_needed(corner, tile) + 1)
        #     # manhattanDistance is better, but is it admissible for our problem?
        #     # min_dist = min(min_dist, util.manhattanDistance(corner, tile) + 1)
            cost += util.manhattanDistance(corner, occupied_tiles[0])
    # print(cost)
    return cost


# def diagonal_moves(x, y):
#     return [(x + 1, y + 1), (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1)]


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
    cost = 0
    vacant_targets = [target for target in problem.targets
                      if state.get_position(target[0], target[1]) == -1]
    # print(vacant_targets)
    occupied_tiles = []
    for x in range(state.board_w):
        for y in range(state.board_h):
            if state.get_position(x, y) == 0:
                occupied_tiles.append((x, y))
    # print(occupied_tiles)
    for target in vacant_targets:
        # if occupied_tiles:
        #     occupied_tiles.sort(key=lambda tile: util.manhattanDistance(target, tile))
        #     cost += util.manhattanDistance(target, occupied_tiles[0])
        min_dist = max(state.board_w, state.board_h)
        for tile in occupied_tiles:
            # for move in diagonal_moves(*tile):
            #     if state.check_tile_legal(0, *move) and state.check_tile_attached(0, *move):
            min_dist = min(min_dist, find_diagonal_tiles_needed(target, tile))
            # manhattanDistance is better, but is it admissible for our problem?
            # min_dist = min(min_dist, util.manhattanDistance(target, tile))
        cost += min_dist
    # print(cost)
    return cost


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
        This method should return a sequence of actions that covers all target locations on the board.
        This time we trade optimality for speed.
        Therefore, your agent should try and cover one target location at a time. Each time,
        aiming for the closest uncovered location.
        You may define helpful functions as you wish.

        Probably a good way to start, would be something like this --

        current_state = self.board.__copy__()
        backtrace = []

        while ....

            actions = set of actions that covers the closets uncovered target location
            add actions to backtrace

        return backtrace
        """

        def get_closest_target(state):
            # establishing base distance
            distance_to_beat = max(state.board_w, state.board_h)
            closest = self.targets[0]
            for target in self.targets:
                t_x, t_y = target
                for x in range(state.board_w):
                    for y in range(state.board_h):
                        # only for tiles that are occupied by the player
                        if state.check_tile_legal(self.PLAYER_ID, x, y):
                            distance = find_diagonal_tiles_needed([x, y], [t_x, t_y])
                            if distance + 1 < distance_to_beat:
                                closest = target
                                distance_to_beat = distance + 1
            return closest

        current_state = self.board.__copy__()
        backtrace = []
        # iterate over targets
        while self.targets:
            closest_target = get_closest_target(current_state)
            self.targets.remove(closest_target)
            # initialize a problem that is exactly the current state
            # problem = BlokusCoverProblem(current_state.board_w, current_state.board_h,
            #                              current_state.piece_list, self.starting_point,
            #                              [closest_target])
            # problem.change_board(current_state)
            # get list of actions from current_state to target
            actions = astar(self, blokus_cover_heuristic)
            # self.expanded += problem.expanded
            # update the backtrace and the board
            for action in actions:
                backtrace.append(action)
                current_state.do_move(0, action)

        return backtrace


class MiniContestSearch:
    """
    Implement your contest entry here
    """

    def __init__(self, board_w, board_h, piece_list, starting_point=(0, 0), targets=(0, 0)):
        self.targets = targets.copy()
        "*** YOUR CODE HERE ***"

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        return self.board

    def solve(self):
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()
