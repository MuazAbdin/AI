"""
In search.py, you will implement generic search algorithms
"""

import util


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def get_start_state(self):
        """
        Returns the start state for the search problem
        """
        util.raiseNotDefined()

    def is_goal_state(self, state):
        """
        state: Search state

        Returns True if and only if the state is a valid goal state
        """
        util.raiseNotDefined()

    def get_successors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples,
        (successor, action, stepCost), where 'successor' is a
        successor to the current state, 'action' is the action
        required to get there, and 'stepCost' is the incremental
        cost of expanding to that successor
        """
        util.raiseNotDefined()

    def get_cost_of_actions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        util.raiseNotDefined()


def get_actions(visited, goal):
    actions = list()
    predecessor, action = visited[goal]
    while predecessor:
        actions.append(action)
        predecessor, action = visited[predecessor]
    actions.reverse()
    return actions


def depth_first_search(problem):
    """
    Search the deepest nodes in the search tree first,
    implementing a graph search algorithm.
    returns a list of actions that reaches the goal.
    """
    # Fringe is a stack (LIFO)
    fringe = util.Stack()
    start_state = problem.get_start_state()
    fringe.push(start_state)
    # Predecessors map: state -> (pre, action)
    visited = {start_state: (None, None)}

    while not fringe.isEmpty():
        current = fringe.pop()
        if problem.is_goal_state(current):
            return get_actions(visited, current)
        for state, action, cost in problem.get_successors(current):
            if state not in visited:
                visited[state] = (current, action)
                fringe.push(state)
    return list()


def breadth_first_search(problem):
    """
    Search the shallowest nodes in the search tree first.
    """
    # Fringe is a Queue (FIFO)
    fringe = util.Queue()
    start_state = problem.get_start_state()
    fringe.push(start_state)
    # Predecessors map: state -> (pre, action)
    visited = {start_state: (None, None)}

    while not fringe.isEmpty():
        current = fringe.pop()
        if problem.is_goal_state(current):
            return get_actions(visited, current)
        for state, action, cost in problem.get_successors(current):
            if state not in visited:
                visited[state] = (current, action)
                fringe.push(state)
    return list()


def uniform_cost_search(problem):
    """
    Search the node of least total cost first.
    """
    start_state = problem.get_start_state()
    frontier = util.PriorityQueue()
    frontier.push(start_state, 0)
    explored = set()
    pre = {start_state: (None, None)}
    costs = {start_state: 0}

    while not frontier.isEmpty():
        current = frontier.pop()
        if problem.is_goal_state(current):
            return get_actions(pre, current)
        explored.add(current)
        for state, action, cost in problem.get_successors(current):
            if state not in explored:
                pre[state] = (current, action)
                costs[state] = costs[current] + cost
                frontier.push(state, costs[state])

    return list()

    # # Fringe is a PriorityQueue
    # fringe = util.PriorityQueue()
    # start_state = problem.get_start_state()
    # fringe.push(start_state, 0)
    # # Predecessors map: state -> (pre, action)
    # visited = {start_state: (None, None)}
    # # Accumulated cost map: state -> cost from start
    # costs = {start_state: 0}
    #
    # while not fringe.isEmpty():
    #     current = fringe.pop()
    #     if problem.is_goal_state(current):
    #         return get_actions(visited, current)
    #     for state, action, cost in problem.get_successors(current):
    #         if state not in visited:
    #             visited[state] = (current, action)
    #             costs[state] = costs[current] + cost
    #             fringe.push(state, costs[state])
    # return list()


def null_heuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def a_star_search(problem, heuristic=null_heuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """
    # Fringe is a PriorityQueueWithFunction
    fringe = util.PriorityQueueWithFunction(lambda x: costs[x] + heuristic(x, problem))
    start_state = problem.get_start_state()
    # Predecessors map: state -> (pre, action)
    visited = {start_state: (None, None)}
    # Accumulated cost map: state -> cost from start
    costs = {start_state: 0}
    fringe.push(start_state)

    while not fringe.isEmpty():
        current = fringe.pop()
        if problem.is_goal_state(current):
            return get_actions(visited, current)
        for state, action, cost in problem.get_successors(current):
            if state not in visited:
                visited[state] = (current, action)
                costs[state] = costs[current] + cost
                fringe.push(state)
    return list()


# Abbreviations
bfs = breadth_first_search
dfs = depth_first_search
astar = a_star_search
ucs = uniform_cost_search
