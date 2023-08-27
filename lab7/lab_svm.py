# MIT 6.034 Support Vector Machines Lab
# Written by 6.034 staff

from svm_data import *
from functools import reduce


#### Part 1: Vector Math #######################################################

def dot_product(u, v):
    """Computes the dot product of two vectors u and v, each represented 
    as a tuple or list of coordinates. Assume the two vectors are the
    same length."""
    return sum([x*y for x, y in zip(u, v)])

def norm(v):
    """Computes the norm (length) of a vector v, represented
    as a tuple or list of coords."""
    return (sum([x**2 for x in v]))**0.5


#### Part 2: Using the SVM Boundary Equations ##################################
def positiveness(svm, point):
    """Computes the expression (w dot x + b) for the given Point x."""
    return dot_product(svm.w, point.coords) + svm.b

def classify(svm, point):
    """Uses the given SVM to classify a Point. Assume that the point's true
    classification is unknown.
    Returns +1 or -1, or 0 if point is on boundary."""
    if positiveness(svm, point) > 0:
        return 1
    elif positiveness(svm, point) < 0:
        return -1
    else:
        return 0

def margin_width(svm):
    """Calculate margin width based on the current boundary."""
    return 2/norm(svm.w)

def check_gutter_constraint(svm):
    """Returns the set of training points that violate one or both conditions:
        * gutter constraint (positiveness == classification, for support vectors)
        * training points must not be between the gutters
    Assumes that the SVM has support vectors assigned."""
    violations  = set()
    for point in svm.training_points:
        posi = positiveness(svm, point)
        if abs(posi) < 1:
            violations.add(point)
        elif point in svm.support_vectors and posi != point.classification:
            violations.add(point)
    return violations


#### Part 3: Supportiveness ####################################################

def check_alpha_signs(svm):
    """Returns the set of training points that violate either condition:
        * all non-support-vector training points have alpha = 0
        * all support vectors have alpha > 0
    Assumes that the SVM has support vectors assigned, and that all training
    points have alpha values assigned."""
    violations = set()
    for point in svm.training_points:
        if point in svm.support_vectors and point.alpha <= 0:
            violations.add(point)
        elif point not in svm.support_vectors and point.alpha != 0:
            violations.add(point)
    return violations


def check_alpha_equations(svm):
    """Returns True if both Lagrange-multiplier equations are satisfied,
    otherwise False. Assumes that the SVM has support vectors assigned, and
    that all training points have alpha values assigned."""
    sum_posi = 0
    sum_vec = [0]*len(svm.training_points[0].coords)
    for point in svm.training_points:
        sum_posi += point.alpha*point.classification
        sum_vec = vector_add(scalar_mult(point.alpha*point.classification, point.coords), sum_vec)
    if sum_posi != 0 or sum_vec != svm.w:
        return False
    return True
    



#### Part 4: Evaluating Accuracy ###############################################

def misclassified_training_points(svm):
    """Returns the set of training points that are classified incorrectly
    using the current decision boundary."""
    violations = set()
    for point in svm.training_points:
        if point.classification != classify(svm, point):
            violations.add(point)
    return violations


#### Part 5: Training an SVM ###################################################

def update_svm_from_alphas(svm):
    """Given an SVM with training data and alpha values, use alpha values to
    update the SVM's support vectors, w, and b. Return the updated SVM."""
    svm.support_vectors = []
    svm.w = [0]*len(svm.training_points[0].coords)
    for point in svm.training_points:
        if point.alpha > 0:
            svm.support_vectors.append(point)
        svm.w = vector_add(svm.w, scalar_mult(point.alpha*point.classification, point.coords))

    max_b, min_b = float('-inf'), float('inf')
    for point in svm.support_vectors:
        b = point.classification - dot_product(svm.w, point.coords)
        if point.classification == 1 and b > max_b:
            max_b = b
        elif point.classification == -1 and b < min_b:
            min_b = b
    svm.b = (max_b+min_b)/2

    return svm


#### Part 6: Multiple Choice ###################################################

ANSWER_1 = 11
ANSWER_2 = 6
ANSWER_3 = 3
ANSWER_4 = 2

ANSWER_5 = ['A', 'D']
ANSWER_6 = ['A', 'B', 'D']
ANSWER_7 = ['A', 'B', 'D']
ANSWER_8 = []
ANSWER_9 = ['A', 'B', 'D']
ANSWER_10 = ['A', 'B', 'D']

ANSWER_11 = False
ANSWER_12 = True
ANSWER_13 = False
ANSWER_14 = False
ANSWER_15 = False
ANSWER_16 = True

ANSWER_17 = [1, 3, 6, 8]
ANSWER_18 = [1, 2, 4, 5, 6, 7, 8]
ANSWER_19 = [1, 2, 4, 5, 6, 7, 8]

ANSWER_20 = 6


#### SURVEY ####################################################################

NAME = 'Juan Rached'
COLLABORATORS = ''
HOW_MANY_HOURS_THIS_LAB_TOOK = 5
WHAT_I_FOUND_INTERESTING = 'That support vector machines use quadratic programming'
WHAT_I_FOUND_BORING = 'Nothing'
SUGGESTIONS = ''
