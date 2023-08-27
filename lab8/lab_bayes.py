# MIT 6.034 Bayesian Inference Lab
# Written by 6.034 staff

from xml.etree.ElementPath import get_parent_map
from nets import *


#### Part 1: Warm-up; Ancestors, Descendents, and Non-descendents ##############

def get_ancestors(net, var):
    "Return a set containing the ancestors of var"
    ancestors = set()
    parents = net.get_parents(var)
    for parent in parents:
        ancestors.add(parent)
        ancestors |= get_ancestors(net, parent)
       
    return ancestors

def get_descendants(net, var):
    "Returns a set containing the descendants of var"
    descendants = set()
    children = net.get_children(var)
    for child in children:
        descendants.add(child)
        descendants |= get_descendants(net, child)
       
    return descendants

def get_nondescendants(net, var):
    "Returns a set containing the non-descendants of var"
    descendants = get_descendants(net, var)
    all_vars = net.get_variables()
    all_vars.remove(var)
    for var in list(descendants):
        all_vars.remove(var)
    
    return set(all_vars)


#### Part 2: Computing Probability #############################################

def simplify_givens(net, var, givens):
    """
    If givens include every parent of var and no descendants, returns a
    simplified list of givens, keeping only parents.  Does not modify original
    givens.  Otherwise, if not all parents are given, or if a descendant is
    given, returns original givens.
    """
    givens_keys = set(givens.keys())
    parents = net.get_parents(var) 
    descendants = get_descendants(net, var)
    if parents.issubset(givens_keys) and descendants.intersection(givens_keys) == set():
        givens_copy = givens.copy()
        nondescendants = get_nondescendants(net, var)
        for elem in nondescendants:
            if elem in set(givens_copy.keys()):
                del givens_copy[elem]
        for parent in parents:
            givens_copy[parent] = givens[parent]
        return givens_copy
    else:
        return givens
    
def probability_lookup(net, hypothesis, givens=None):
    "Looks up a probability in the Bayes net, or raises LookupError"
    if len(hypothesis) > 1:
        raise LookupError
    if givens is not None:
        var = list(hypothesis.keys())[0]
        givens = simplify_givens(net, var, givens)
    try: 
        return net.get_probability(hypothesis, givens)
    except: 
        raise LookupError

def probability_joint(net, hypothesis):
    "Uses the chain rule to compute a joint probability"
    prob = 1
    for var in hypothesis.keys():
        givens = {parent: hypothesis[parent] for parent in net.get_parents(var)}
        prob *= probability_lookup(net, {var: hypothesis[var]}, givens)
    return prob
    
def probability_marginal(net, hypothesis):
    "Computes a marginal probability as a sum of joint probabilities"
    probs = 0
    all_vars = net.get_variables()
    for new_hypo in net.combinations(all_vars, hypothesis):
        probs += probability_joint(net, new_hypo)
    return probs

def probability_conditional(net, hypothesis, givens=None):
    "Computes a conditional probability as a ratio of marginal probabilities"
    if givens is None:
        return probability_marginal(net, hypothesis)
    else:
        for key, val in hypothesis.items():
            if key in givens.keys():
                if givens[key] == val:
                    return 1
                else:
                    return 0
        
        return probability_marginal(net, dict(hypothesis, **givens))/probability_marginal(net, givens)

    
def probability(net, hypothesis, givens=None):
    "Calls previous functions to compute any probability"
    return probability_conditional(net, hypothesis, givens)


#### Part 3: Counting Parameters ###############################################

def number_of_parameters(net):
    """
    Computes the minimum number of parameters required for the Bayes net.
    """
    min_params = []
    for var in net.get_variables():
        params = len(net.get_domain(var)) - 1
        for parent in net.get_parents(var):
            params *= len(net.get_domain(parent))
        min_params.append(params)
    return sum(min_params)



#### Part 4: Independence ######################################################

def is_independent(net, var1, var2, givens=None):
    """
    Return True if var1, var2 are conditionally independent given givens,
    otherwise False. Uses numerical independence.
    # """
    if not isinstance(net.get_domain(var1)[0], bool):
        if givens is None:
            prob1 = probability(net, {var1:net.get_domain(var1)[1]})
            prob2 = probability(net, {var1:net.get_domain(var1)[1]}, {var2:net.get_domain(var2)[1]})
        else:
            prob1 = probability(net, {var1:net.get_domain(var1)[1]}, givens)
            prob2 = probability(net, {var1:net.get_domain(var1)[1]}, dict({var2:net.get_domain(var2)[1]}, **givens))
    else:
        if givens is None:
            prob1 = probability(net, {var1:net.get_domain(var1)[0]})
            prob2 = probability(net, {var1:net.get_domain(var1)[0]}, {var2:net.get_domain(var2)[0]})
        else:
            prob1 = probability(net, {var1:net.get_domain(var1)[0]}, givens)
            prob2 = probability(net, {var1:net.get_domain(var1)[0]}, dict({var2:net.get_domain(var2)[0]}, **givens))

    return approx_equal(prob1, prob2) 
    
def is_structurally_independent(net, var1, var2, givens=None):
    """
    Return True if var1, var2 are conditionally independent given givens,
    based on the structure of the Bayes net, otherwise False.
    Uses structural independence only (not numerical independence).
    """
    vars = [var1, var2]
    if givens is not None:
        vars += givens.keys()

    vars_set = set(vars.copy())
    for var in vars:
        vars_set.update(get_ancestors(net, var))
    
    net1, net2 = net.subnet(list(vars_set)), net.subnet(list(vars_set))

    for elem in net1.get_variables():
        parents = net1.get_parents(elem)
        for parent1 in parents:
            for parent2 in parents:
                if parent1 is not parent2:
                    net2 = net2.link(parent1, parent2)

    net2 = net2.make_bidirectional()

    if givens is not None:
        for given in givens.keys():
            net2 = net2.remove_variable(given)

    return net2.find_path(var1, var2) is None


#### SURVEY ####################################################################

NAME = "Juan Rached"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = 6
WHAT_I_FOUND_INTERESTING = "Relationships between different probabilities"
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = ""
