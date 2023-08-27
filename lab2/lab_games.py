# MIT 6.034 Games Lab
# Written by 6.034 staff

from hashlib import new
from game_api import *
from boards import *
from toytree import GAME1

INF = float('inf')

# Please see wiki lab page for full description of functions and API.


###TODO: 1. Done
#        2. Done
#        3. Progressive deepening.
#        4. Refactor code.

#### Part 1: Utility Functions #################################################

class Counter():
    def __init__(self):
        self.val = 0
    
    def count(self):
        self.val += 1

    def get_val(self):
        return self.val


def did_someone_win(board):
    chains = sorted(board.get_all_chains(), key = lambda x : -len(x))
    return chains != [] and len(chains[0]) >= 4

def is_game_over_connectfour(board):
    """Returns True if game is over, otherwise False."""
    if did_someone_win(board):
        return True

    for elem in board.board_array[0]:
        if elem is None:
            
            return False

    return True

def next_boards_connectfour(board):
    """Returns a list of ConnectFourBoard objects that could result from the
    next move, or an empty list if no moves can be made."""

    if is_game_over_connectfour(board):
        return []

    next_moves = [] #List pf ConnectFourBoard objects

    #Cols
    for j in range(7):
        #Rows
        for i in range(5, -1, -1):
            if board.board_array[i][j] == None:
                #Insert element at [i,j]
                new_board = board.add_piece(j)

                #Update current player
                new_board.set_current_player_name(board.get_other_player_name())

                #Append to next_moves list
                next_moves.append(new_board)

                #Break out (move to next column) if already made a move on this column
                break

    return next_moves

def endgame_score_connectfour(board, is_current_player_maximizer):
    """Given an endgame board, returns 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie."""
    if did_someone_win(board):
        return 1000*(-1)**(int(is_current_player_maximizer))
    else:
        return 0

def endgame_score_connectfour_faster(board, is_current_player_maximizer):
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""
    #Win faster 
    if did_someone_win(board):
        return (1000 + 30*(42-board.count_pieces()))*(-1)**(int(is_current_player_maximizer))
    else:
        return 0

def heuristic_connectfour(board, is_current_player_maximizer):
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""
    current_sum = sum([len(chain)**len(chain) for chain in board.get_all_chains(current_player=True)])
    other_sum = sum([len(chain)**len(chain) for chain in board.get_all_chains(current_player=False)])

    advantage = current_sum - other_sum

    return (-5*advantage)*(-1)**(int(is_current_player_maximizer))


# Now we can create AbstractGameState objects for Connect Four, using some of
# the functions you implemented above.  You can use the following examples to
# test your dfs and minimax implementations in Part 2.

# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


#### Part 2: Searching a Game Tree #############################################

# Note: Functions in Part 2 use the AbstractGameState API, not ConnectFourBoard.
def in_extended(child, extended_list):
    """Using this helper function instead of a set to check extended set
       because it says the state object is not hashable :(
    """
    for elem in extended_list:
        if child == elem:
            return True
    return False

def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score.
    Returns a tuple containing:
     0. the best path (a list of AbstractGameState objects),
     1. the score of the leaf node (a number), and
     2. the number of static evaluations performed (a number)"""

    stack = [[state]]
    end_game_paths = []
    counter = 1
    extended = [] 

    while stack:
        #Pop top of stack (end of list)
        current_path = stack.pop(-1)
        current_state = current_path[-1]

        if current_state.is_game_over():
            counter += 1
            end_game_paths.append(current_path)

        extended.append(current_state)

        #Get children
        next_states = current_state.generate_next_states()
        next_states.reverse()
        for child in next_states:
            #Check if children is end game state append to list 
            if in_extended(child, extended):
                continue
            else:
                new_path = current_path.copy()
                new_path.append(child)
                stack.append(new_path)
            #Else if child is not in extended set, add to extended set, add to stack and continue 

    #Get state with max score from end_game_set and return it with the other required info.
    max_path = max(end_game_paths, key=lambda x: abs(x[-1].get_endgame_score()))
    scores = sorted([path[-1].get_endgame_score() for path in end_game_paths])
    return (max_path, max_path[-1].get_endgame_score(), counter)


# Uncomment the line below to try your dfs_maximizing on an
# AbstractGameState representing the games tree "GAME1" from toytree.py:

# pretty_print_dfs_type(dfs_maximizing(GAME1))

def minimax(state, evals, maximize=True):
    #Base case: Leaf node.
    if state.is_game_over(): 
        evals.count()
        return ([state], state.get_endgame_score(is_current_player_maximizer=maximize), evals)
    
    ###Recursive step: 
    #If max's turn
    if maximize:
        max_child_path, score, evals = max([minimax(child, evals, maximize=False) for child in state.generate_next_states()], key=lambda x: x[1])
        new_path = [state] 
        new_path += max_child_path
        return (new_path, score, evals)
    #else if min's turn
    else:
        min_child_path, score, evals = min([minimax(child, evals, maximize=True) for child in state.generate_next_states()], key=lambda x: x[1])
        new_path = [state] 
        new_path += min_child_path
        return (new_path, score, evals)
        
def minimax_endgame_search(state, maximize=True) :
    """Performs minimax search, searching all leaf nodes and statically
    evaluating all endgame scores.  Same return type as dfs_maximizing."""
    evals = Counter()
    result = minimax(state, evals, maximize)
    return (result[0], result[1], result[2].get_val())
    

# Uncomment the line below to try your minimax_endgame_search on an
# AbstractGameState representing the ConnectFourBoard "NEARLY_OVER" from boards.py:

# pretty_print_dfs_type(minimax_endgame_search(state_NEARLY_OVER))

def minimax_heuristic(state, evals, maximize=True, depth=0, depth_limit=INF, heuristic_fn=always_zero):
    #Base case: Either leaf node or max_depth reached.
    
    if state.is_game_over() or depth >= depth_limit: 
        evals.count()
        if state.is_game_over():
            score = state.get_endgame_score(is_current_player_maximizer=maximize)
        else:
            score = heuristic_fn(state.snapshot, maximize)
        return ([state], score, evals)

    
    ###Recursive step: 
    depth += 1
    #If max's turn
    if maximize:
        max_child_path, score, evals = max([minimax_heuristic(child, evals, maximize=False, depth= depth, depth_limit=depth_limit, heuristic_fn=heuristic_fn) for child in state.generate_next_states()], key=lambda x: x[1])
        new_path = [state] 
        new_path += max_child_path
        return (new_path, score, evals)
    #else if min's turn
    else:
        min_child_path, score, evals = min([minimax_heuristic(child, evals, maximize=True, depth=depth, depth_limit=depth_limit, heuristic_fn=heuristic_fn) for child in state.generate_next_states()], key=lambda x: x[1])
        new_path = [state] 
        new_path += min_child_path
        return (new_path, score, evals)
        

def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    """Performs standard minimax search. Same return type as dfs_maximizing."""
    evals = Counter()
    result = minimax_heuristic(state, evals, depth_limit=depth_limit, maximize=maximize, heuristic_fn=heuristic_fn)
    return (result[0], result[1], result[2].get_val())

# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1. Try increasing the value of depth_limit to see what happens:

# pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))

def minimax_alphabeta(state, alpha, beta, evals, maximize=True, depth=0, depth_limit=INF, heuristic_fn=always_zero):
    #Base case: Either leaf node or max_depth reached.
    if state.is_game_over() or depth >= depth_limit: 
        evals.count()
        if state.is_game_over():
            score = state.get_endgame_score(is_current_player_maximizer=maximize)
        else:
            score = heuristic_fn(state.snapshot, maximize)
        return ([state], score, evals)
    
    ###Recursive step:
    depth += 1 
    #If max's turn
    if maximize:
        for child in state.generate_next_states():
            child_path = minimax_alphabeta(child, alpha, beta, evals, maximize=False, depth=depth, depth_limit=depth_limit, heuristic_fn=heuristic_fn)
            new_path = ([state] + child_path[0], child_path[1], child_path[2])
            alpha = max(alpha, new_path, key=lambda x: x[1])

            #Pruning step
            if alpha[1] >= beta[1]:
                break
        return alpha
    #else if min's turn
    else:
        for child in state.generate_next_states():
            child_path = minimax_alphabeta(child, alpha, beta, evals, maximize=True, depth=depth, depth_limit=depth_limit, heuristic_fn=heuristic_fn)
            new_path = ([state] + child_path[0], child_path[1], child_path[2])
            beta = min(beta, new_path, key=lambda x: x[1])

            #Pruning step
            if alpha[1] >= beta[1]:
                break
        return beta
            

def minimax_search_alphabeta(state, alpha=-INF, beta=INF, heuristic_fn=always_zero,
                             depth_limit=INF, maximize=True) :
    """"Performs minimax with alpha-beta pruning. Same return type 
    as dfs_maximizing."""
    alpha = ([state], alpha, 0)
    beta = ([state], beta, 0)
    evals = Counter()
    result =  minimax_alphabeta(state, alpha, beta, evals, maximize=maximize, depth_limit=depth_limit, heuristic_fn=heuristic_fn)
    return (result[0], result[1], result[2].get_val())

# Uncomment the line below to try minimax_search_alphabeta with "BOARD_UHOH" and
# depth_limit=4. Compare with the number of evaluations from minimax_search for
# different values of depth_limit.

# pretty_print_dfs_type(minimax_search_alphabeta(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=5))

def progressive_deepening(state, heuristic_fn=always_zero, depth_limit=INF,
                          maximize=True):
    """Runs minimax with alpha-beta pruning. At each level, updates anytime_value
    with the tuple returned from minimax_search_alphabeta. Returns anytime_value."""
    i = 0
    anytime = AnytimeValue()
    while i < depth_limit:
        result = minimax_search_alphabeta(state, heuristic_fn=heuristic_fn,
                             depth_limit=i+1, maximize=maximize)
        anytime.set_value(result)
        i += 1

    return anytime

    


# Uncomment the line below to try progressive_deepening with "BOARD_UHOH" and
# depth_limit=4. Compare the total number of evaluations with the number of
# evaluations from minimax_search or minimax_search_alphabeta.

# progressive_deepening(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4).pretty_print()


# Progressive deepening is NOT optional. However, you may find that 
#  the tests for progressive deepening take a long time. If you would
#  like to temporarily bypass them, set this variable False. You will,
#  of course, need to set this back to True to pass all of the local
#  and online tests.
TEST_PROGRESSIVE_DEEPENING = True
if not TEST_PROGRESSIVE_DEEPENING:
    def not_implemented(*args): raise NotImplementedError
    progressive_deepening = not_implemented


#### Part 3: Multiple Choice ###################################################

ANSWER_1 = '4'

ANSWER_2 = '1'

ANSWER_3 = '4'

ANSWER_4 = '5'


#### SURVEY ###################################################

NAME = "Juan Rached"
COLLABORATORS = "Nobody"
HOW_MANY_HOURS_THIS_LAB_TOOK = "About 5"
WHAT_I_FOUND_INTERESTING = "The idea of adversary games in general. Playing against my own AI was pretty cool too"
WHAT_I_FOUND_BORING = "Debugging"
SUGGESTIONS = "Nothing"



####################################### TESTING ############################################
# BOARD_EMPTY = ConnectFourBoard(board_array =
#                                   ( ( 0,0,0,0,0,0,0 ),
#                                     ( 0,0,0,0,0,0,0 ),
#                                     ( 0,0,0,0,0,0,0 ),
#                                     ( 0,0,0,0,0,0,0 ),
#                                     ( 0,0,0,0,0,0,0 ),
#                                     ( 0,0,0,0,0,0,0 ),
#                                     ),
#                                   players = ['Luke', 'Leia'],
#                                   whose_turn = 'Luke')

# abstract_state = AbstractGameState(BOARD_EMPTY, 
#                                    is_game_over_connectfour, 
#                                    next_boards_connectfour, 
#                                    endgame_score_connectfour_faster)

# result = dfs_maximizing(abstract_state)
# # result = minimax_endgame_search(abstract_state)
# pretty_print_dfs_type(result)