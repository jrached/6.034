# MIT 6.034 Boosting (Adaboost) Lab
# Written by 6.034 staff

from math import log as ln
from utils import *


#### Part 1: Helper functions ##################################################

def initialize_weights(training_points):
    """Assigns every training point a weight equal to 1/N, where N is the number
    of training points.  Returns a dictionary mapping points to weights."""
    weights = {}
    n = len(training_points)
    for point in training_points:
        weights[point] = make_fraction(1,n)
    return weights

def calculate_error_rates(point_to_weight, classifier_to_misclassified):
    """Given a dictionary mapping training points to their weights, and another
    dictionary mapping classifiers to the training points they misclassify,
    returns a dictionary mapping classifiers to their error rates."""
    error_rates = {}
    for classifier, points in classifier_to_misclassified.items():
        error = 0
        for point in points:
            error += point_to_weight[point]
        error_rates[classifier] = error
    return error_rates

def pick_best_classifier(classifier_to_error_rate, use_smallest_error=True):
    """Given a dictionary mapping classifiers to their error rates, returns the
    best* classifier, or raises NoGoodClassifiersError if best* classifier has
    error rate 1/2.  best* means 'smallest error rate' if use_smallest_error
    is True, otherwise 'error rate furthest from 1/2'."""
    if use_smallest_error:
        best = min(classifier_to_error_rate.items(), key = lambda x: x[1])
    else:
        best = max(classifier_to_error_rate.items(), key = lambda x: abs(make_fraction(1,2) - x[1]))

    if best[1] == make_fraction(1,2):
        raise NoGoodClassifiersError
    else:
        return best[0]

def calculate_voting_power(error_rate):
    """Given a classifier's error rate (a number), returns the voting power
    (aka alpha, or coefficient) for that classifier."""
    if error_rate > 0 and error_rate < 1:
        return make_fraction(1,2)*ln((1-error_rate)/error_rate)
    elif error_rate == 0:
        return INF
    elif error_rate == 1:
        return -INF

def get_overall_misclassifications(H, training_points, classifier_to_misclassified):
    """Given an overall classifier H, a list of all training points, and a
    dictionary mapping classifiers to the training points they misclassify,
    returns a set containing the training points that H misclassifies.
    H is represented as a list of (classifier, voting_power) tuples."""
    H_misclasified = set()
    for point in training_points:
        classification = 0
        for classifier, power in H:
            if point not in classifier_to_misclassified[classifier]:
                k = 1
            else:
                k = -1
            classification += k*power

        if classification <= 0:
            H_misclasified.add(point)

    return H_misclasified

def is_good_enough(H, training_points, classifier_to_misclassified, mistake_tolerance=0):
    """Given an overall classifier H, a list of all training points, a
    dictionary mapping classifiers to the training points they misclassify, and
    a mistake tolerance (the maximum number of allowed misclassifications),
    returns False if H misclassifies more points than the tolerance allows,
    otherwise True.  H is represented as a list of (classifier, voting_power)
    tuples."""
    return len(get_overall_misclassifications(H, training_points, classifier_to_misclassified)) <= mistake_tolerance

def update_weights(point_to_weight, misclassified_points, error_rate):
    """Given a dictionary mapping training points to their old weights, a list
    of training points misclassified by the current weak classifier, and the
    error rate of the current weak classifier, returns a dictionary mapping
    training points to their new weights.  This function is allowed (but not
    required) to modify the input dictionary point_to_weight."""
    for point in point_to_weight.keys():
        if point not in misclassified_points:
            point_to_weight[point] *= make_fraction(1,2)*make_fraction(1, 1 - error_rate)
        else:
            point_to_weight[point] *= make_fraction(1,2)*make_fraction(1, error_rate)
    
    return point_to_weight

#### Part 2: Adaboost ##########################################################

def adaboost(training_points, classifier_to_misclassified,
             use_smallest_error=True, mistake_tolerance=0, max_rounds=INF):
    """Performs the Adaboost algorithm for up to max_rounds rounds.
    Returns the resulting overall classifier H, represented as a list of
    (classifier, voting_power) tuples."""
    counter, H, weights = 0, [], initialize_weights(training_points)
    while counter < max_rounds:
        weak_classifier_error = calculate_error_rates(weights, classifier_to_misclassified)

        try: 
            h = pick_best_classifier(weak_classifier_error, use_smallest_error)
        except:
            return H

        power = calculate_voting_power(weak_classifier_error[h])
        H.append((h, power))

        weights = update_weights(weights, classifier_to_misclassified[h], weak_classifier_error[h])

        if is_good_enough(H, training_points, classifier_to_misclassified, mistake_tolerance):
            return H
        
        counter += 1

    return H


#### SURVEY ####################################################################

NAME = "Juan Rached"
COLLABORATORS = ""
HOW_MANY_HOURS_THIS_LAB_TOOK = "2"
WHAT_I_FOUND_INTERESTING = "That intuitively I think I had thought of something similar to adaboosting to improve ML before being formally introduced to it."
WHAT_I_FOUND_BORING = ""
SUGGESTIONS = ""
