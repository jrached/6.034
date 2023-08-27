# MIT 6.034 Constraints Lab
# Written by 6.034 staff

from hashlib import new
from os import unlink, unsetenv
from tabnanny import check
from constraint_api import *
from test_problems import get_pokemon_problem

#### Part 1: Warmup ############################################################

class Counter():
    def __init__(self):
        self.val = 0

    def count(self):
        self.val +=1

    def get_count(self):
        return self.val

def has_empty_domains(csp) :
    """Returns True if the problem has one or more empty domains, otherwise False"""
    for domain in csp.domains.values():
        if domain == []:
            return True
    return False

def check_all_constraints(csp) :
    """Return False if the problem's assigned values violate some constraint,
    otherwise True"""
    for var1 in csp.assignments:
        for var2 in csp.assignments:
            for constraint in csp.constraints_between(var1, var2):
                if not constraint.check(csp.assignments[var1], csp.assignments[var2]):
                    return False
    return True


#### Part 2: Depth-First Constraint Solver #####################################

def solve_constraint_dfs(problem) :
    """
    Solves the problem using depth-first search.  Returns a tuple containing:
    1. the solution (a dictionary mapping variables to assigned values)
    2. the number of extensions made (the number of problems popped off the agenda).
    If no solution was found, return None as the first element of the tuple.
    """
    agenda = [problem]
    extensions = Counter()

    while agenda:
        #Dfs so you pop from the front and prepend new problems to the list.
        current_problem = agenda.pop(0) 
        extensions.count()

        #Problem is unsolvable with current assignments so backtrack.
        if has_empty_domains(current_problem) or not check_all_constraints(current_problem):
            continue

        #If no constraints are violated and all values have an assignment
        #then the problem is solved, solve the next variables domain.
        if current_problem.unassigned_vars == []:
            return (current_problem.assignments, extensions.get_count())

        #For every value in the unassigned variable's domain, create a
        #new problem. Prepend all the new problems to the agenda.
        new_problems = []
        unassigned_var = current_problem.pop_next_unassigned_var()
        for value in current_problem.domains[unassigned_var]:
            new_problem = current_problem.copy()
            new_problem.set_assignment(unassigned_var, value)
            new_problems.append(new_problem)

        agenda = new_problems + agenda

    return (None, extensions.get_count())

    

# QUESTION 1: How many extensions does it take to solve the Pokemon problem
#    with DFS?

# Hint: Use get_pokemon_problem() to get a new copy of the Pokemon problem
#    each time you want to solve it with a different search method.

ANSWER_1 = 20


#### Part 3: Forward Checking ##################################################

def conflict_helper(csp, var, neighbor, val2):
    """Helper function for forward check. Helps identify values in neighbor's domains
       that conflict with all values in current variable's domain.
    """
    #Check every value in neighbor against every value in var. 
    #If for some value in neighbor conflicts with every value in var, remove that value.
    for val1 in csp.get_domain(var):
        conflict = False
        for constraint in csp.constraints_between(var, neighbor):
            if not constraint.check(val1, val2):
                conflict = True
        if not conflict:
            return True
    return False

def eliminate_from_neighbors(csp, var) :
    """
    Eliminates incompatible values from var's neighbors' domains, modifying
    the original csp. Returns an alphabetically sorted list of the neighboring
    variables whose domains were reduced, with each variable appearing at most
    once.  If no domains were reduced, returns empty list.
    If a domain is reduced to size 0, quits immediately and returns None.
    """
    removed = set()
    for neighbor in csp.get_neighbors(var):
        to_remove = []
        #Check every value in neighbor against every value in var. 
        #If for some value in neighbor conflicts with every value in var, remove that value.
        for val2 in csp.get_domain(neighbor):
            if not conflict_helper(csp, var, neighbor, val2):
                to_remove.append(val2)
                removed.add(neighbor)

        #After iterating through neighbors domain eliminate all conflicting values
        for val in to_remove:
            csp.eliminate(neighbor, val)

        #If a domain is reduced to size zero
        if csp.get_domain(neighbor) == []:
            return None

    return sorted(list(removed))


# Because names give us power over things (you're free to use this alias)
forward_check = eliminate_from_neighbors

def solve_constraint_forward_checking(problem) :
    """
    Solves the problem using depth-first search with forward checking.
    Same return type as solve_constraint_dfs.
    """
    agenda = [problem]
    extensions = Counter()

    while agenda:
        #Dfs so you pop from the front and prepend new problems to the list.
        current_problem = agenda.pop(0) 
        extensions.count()

        #Problem is unsolvable with current assignments so backtrack.
        if has_empty_domains(current_problem) or not check_all_constraints(current_problem):
            continue

        #If no constraints are violated and all values have an assignment
        #then the problem is solved, solve the next variables domain.
        if current_problem.unassigned_vars == []:
            return (current_problem.assignments, extensions.get_count())

        #For every value in the unassigned variable's domain, create a
        #new problem. Prepend all the new problems to the agenda.
        else:
            new_problems = []
            unassigned_var = current_problem.pop_next_unassigned_var()
            for value in current_problem.domains[unassigned_var]:
                new_problem = current_problem.copy()
                new_problem = new_problem.set_assignment(unassigned_var, value)
                forward_check(new_problem, unassigned_var)
                new_problems.append(new_problem)

            agenda = new_problems + agenda

    return (None, extensions.get_count())


# QUESTION 2: How many extensions does it take to solve the Pokemon problem
#    with DFS and forward checking?

ANSWER_2 = 9


#### Part 4: Domain Reduction ##################################################

def domain_reduction(csp, queue=None) :
    """
    Uses constraints to reduce domains, propagating the domain reduction
    to all neighbors whose domains are reduced during the process.
    If queue is None, initializes propagation queue by adding all variables in
    their default order. 
    Returns a list of all variables that were dequeued, in the order they
    were removed from the queue.  Variables may appear in the list multiple times.
    If a domain is reduced to size 0, quits immediately and returns None.
    This function modifies the original csp.
    """
    if queue is None: 
        queue = csp.get_all_variables()
    
    dequeued = []
    #Propagate until queue is empty
    while queue:
        #In dfs fashion pop from queue
        var = queue.pop(0)
        dequeued.append(var)

        #Get neighbors with reduced domains from forward check
        to_append = forward_check(csp, var)

        #Check whether a neighbor's domain was reduced to zero
        if to_append is None:
            return None

        #If reduced neighbor is not in queue yet, prepend it (dfs)
        for neighbor in to_append:
            if neighbor not in set(queue):
                queue.append(neighbor)

    return dequeued

# QUESTION 3: How many extensions does it take to solve the Pokemon problem
#    with DFS (no forward checking) if you do domain reduction before solving it?

ANSWER_3 = 6


def solve_constraint_propagate_reduced_domains(problem) :
    """
    Solves the problem using depth-first search with forward checking and
    propagation through all reduced domains.  Same return type as
    solve_constraint_dfs.
    """
    agenda = [problem]
    extensions = Counter()

    while agenda:
        #Dfs so you pop from the front and prepend new problems to the list.
        current_problem = agenda.pop(0) 
        extensions.count()

        #Problem is unsolvable with current assignments so backtrack.
        if has_empty_domains(current_problem) or not check_all_constraints(current_problem):
            continue

        #If no constraints are violated and all values have an assignment
        #then the problem is solved, solve the next variables domain.
        if current_problem.unassigned_vars == []:
            return (current_problem.assignments, extensions.get_count())

        #For every value in the unassigned variable's domain, create a
        #new problem. Prepend all the new problems to the agenda.
        else:
            new_problems = []
            unassigned_var = current_problem.pop_next_unassigned_var()
            for value in current_problem.domains[unassigned_var]:
                new_problem = current_problem.copy()
                new_problem = new_problem.set_assignment(unassigned_var, value)
                domain_reduction(new_problem, [unassigned_var])
                new_problems.append(new_problem)

            agenda = new_problems + agenda

    return (None, extensions.get_count())


# QUESTION 4: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through reduced domains?

ANSWER_4 = 7



#### Part 5A: Generic Domain Reduction #########################################

def propagate(enqueue_condition_fn, csp, queue=None) :
    """
    Uses constraints to reduce domains, modifying the original csp.
    Uses enqueue_condition_fn to determine whether to enqueue a variable whose
    domain has been reduced. Same return type as domain_reduction.
    """
    if queue is None: 
        queue = csp.get_all_variables()
    
    dequeued = []
    #Propagate until queue is empty
    while queue:
        #In dfs fashion pop from queue
        var = queue.pop(0)
        dequeued.append(var)

        #Get neighbors with reduced domains from forward check
        to_append = forward_check(csp, var)

        #Check whether a neighbor's domain was reduced to zero
        if to_append is None:
            return None

        new_append = []
        for variable in to_append:
            if enqueue_condition_fn(csp, variable):
                new_append.append(variable)        

        #If reduced neighbor is not in queue yet, prepend it (dfs)
        for neighbor in new_append:
            if neighbor not in set(queue):
                queue.append(neighbor)

    return dequeued

def condition_domain_reduction(csp, var) :
    """Returns True if var should be enqueued under the all-reduced-domains
    condition, otherwise False"""
    return True

def condition_singleton(csp, var) :
    """Returns True if var should be enqueued under the singleton-domains
    condition, otherwise False"""
    return len(csp.get_domain(var)) == 1

def condition_forward_checking(csp, var) :
    """Returns True if var should be enqueued under the forward-checking
    condition, otherwise False"""
    return False


#### Part 5B: Generic Constraint Solver ########################################

def solve_constraint_generic(problem, enqueue_condition=None) :
    """
    Solves the problem, calling propagate with the specified enqueue
    condition (a function). If enqueue_condition is None, uses DFS only.
    Same return type as solve_constraint_dfs.
    """
    if enqueue_condition is None:
        #Call dfs
        return solve_constraint_dfs(problem)
    else:
        agenda = [problem]
        extensions = Counter()

        while agenda:
            #Dfs so you pop from the front and prepend new problems to the list.
            current_problem = agenda.pop(0) 
            extensions.count()

            #Problem is unsolvable with current assignments so backtrack.
            if has_empty_domains(current_problem) or not check_all_constraints(current_problem):
                continue

            #If no constraints are violated and all values have an assignment
            #then the problem is solved, solve the next variables domain.
            if current_problem.unassigned_vars == []:
                return (current_problem.assignments, extensions.get_count())

            #For every value in the unassigned variable's domain, create a
            #new problem. Prepend all the new problems to the agenda.
            else:
                new_problems = []
                unassigned_var = current_problem.pop_next_unassigned_var()
                for value in current_problem.domains[unassigned_var]:
                    new_problem = current_problem.copy()
                    new_problem = new_problem.set_assignment(unassigned_var, value)
                    propagate(enqueue_condition, new_problem, [unassigned_var])
                    new_problems.append(new_problem)

                agenda = new_problems + agenda

        return (None, extensions.get_count())
        

# QUESTION 5: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through singleton domains? (Don't
#    use domain reduction before solving it.)

ANSWER_5 = 8

# print(solve_constraint_generic(get_pokemon_problem(),enqueue_condition=condition_singleton))



#### Part 6: Defining Custom Constraints #######################################

def constraint_adjacent(m, n) :
    """Returns True if m and n are adjacent, otherwise False.
    Assume m and n are ints."""
    return abs(m-n) == 1

def constraint_not_adjacent(m, n) :
    """Returns True if m and n are NOT adjacent, otherwise False.
    Assume m and n are ints."""
    return abs(m-n) != 1

def all_different(variables) :
    """Returns a list of constraints, with one difference constraint between
    each pair of variables."""
    result = []
    done = set()
    for var1 in variables:
        for var2 in variables:
            if var1 is not var2 and (var1, var2) not in done and (var2, var1) not in done:
                result.append(Constraint(var1, var2, constraint_different))
                done.add((var1, var2))
    return result



#### SURVEY ####################################################################

NAME = "Juan Rached"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = "6"
WHAT_I_FOUND_INTERESTING = "Trade-off between optimality and speed when choosing enqueue_condition_fn for propagate"
WHAT_I_FOUND_BORING = "Nothing"
SUGGESTIONS = ""
