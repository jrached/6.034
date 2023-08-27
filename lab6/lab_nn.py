# MIT 6.034 Neural Nets Lab
# Written by 6.034 Staff

from xml.dom.expatbuilder import theDOMImplementation
from nn_problems import *
from math import e
INF = float('inf')


#### Part 1: Wiring a Neural Net ###############################################

nn_half = [1]

nn_angle = [2,1]

nn_cross = [2,2,1]

nn_stripe = [3,1]

nn_hexagon = [6,1]

nn_grid = [4,2,1]


#### Part 2: Coding Warmup #####################################################

# Threshold functions
def stairstep(x, threshold=0):
    "Computes stairstep(x) using the given threshold (T)"
    return int(x>=threshold)

def sigmoid(x, steepness=1, midpoint=0):
    "Computes sigmoid(x) using the given steepness (S) and midpoint (M)"
    return 1/(1+e**(-steepness*(x-midpoint)))

def ReLU(x):
    "Computes the threshold of an input using a rectified linear unit."
    return max(0, x)

# Accuracy function
def accuracy(desired_output, actual_output):
    "Computes accuracy. If output is binary, accuracy ranges from -0.5 to 0."
    return -0.5*(desired_output-actual_output)**2


#### Part 3: Forward Propagation ###############################################

def node_value(node, input_values, neuron_outputs):  # PROVIDED BY THE STAFF
    """
    Given
     * a node (as an input or as a neuron),
     * a dictionary mapping input names to their values, and
     * a dictionary mapping neuron names to their outputs
    returns the output value of the node.
    This function does NOT do any computation; it simply looks up
    values in the provided dictionaries.
    """
    if isinstance(node, str):
        # A string node (either an input or a neuron)
        if node in input_values:
            return input_values[node]
        if node in neuron_outputs:
            return neuron_outputs[node]
        raise KeyError("Node '{}' not found in either the input values or neuron outputs dictionary.".format(node))

    if isinstance(node, (int, float)):
        # A constant input, such as -1
        return node

    raise TypeError("Node argument is {}; should be either a string or a number.".format(node))

def forward_prop(net, input_values, threshold_fn=stairstep):
    """Given a neural net and dictionary of input values, performs forward
    propagation with the given threshold function to compute binary output.
    This function should not modify the input net.  Returns a tuple containing:
    (1) the final output of the neural net
    (2) a dictionary mapping neurons to their immediate outputs"""
    node_outputs = {}
    nodes = net.topological_sort()
    for node in nodes:
        wires = net.get_wires(endNode=node)
        sum_ = sum([wire.get_weight()*node_value(wire.startNode, input_values, node_outputs) for wire in wires])
        output = threshold_fn(sum_)
        node_outputs[node] = output
    return (node_value(net.get_output_neuron(), input_values, node_outputs), node_outputs)


#### Part 4: Backward Propagation ##############################################
def gradient_ascent_step(func, inputs, step_size):
    """Given an unknown function of three variables and a list of three values
    representing the current inputs into the function, increments each variable
    by +/- step_size or 0, with the goal of maximizing the function output.
    After trying all possible variable assignments, returns a tuple containing:
    (1) the maximum function output found, and
    (2) the list of inputs that yielded the highest function output."""
    permutations = []
    steps = [-step_size, 0, step_size]
    for step1 in steps:
        for step2 in steps:
            for step3 in steps:
                permutations.append([inputs[0]+step1, inputs[1]+step2, inputs[2]+step3])

    max_perm = max(permutations, key=lambda x: func(*x))
    
    return (func(*max_perm), max_perm)


def get_back_prop_dependencies(net, wire):
    """Given a wire in a neural network, returns a set of inputs, neurons, and
    Wires whose outputs/values are required to update this wire's weight."""
    previous_node = wire.startNode
    current_node = wire.endNode
        
    result = set([previous_node, current_node, wire])
    for new_wire in net.get_wires(startNode=current_node):
        result.add(new_wire)
        result = result.union(get_back_prop_dependencies(net, new_wire))
    return result

def calculate_deltas(net, desired_output, neuron_outputs):
    """Given a neural net and a dictionary of neuron outputs from forward-
    propagation, computes the update coefficient (delta_B) for each
    neuron in the net. Uses the sigmoid function to compute neuron output.
    Returns a dictionary mapping neuron names to update coefficient (the
    delta_B values). """
    neuron_updates = {}
    nodes = net.topological_sort()
    last = nodes[-1]
    final_output = neuron_outputs[last]
    neuron_updates[last] = final_output*(1-final_output)*(desired_output-final_output)
    nodes.reverse()
    for node in nodes[1:]:
        outgoing = sum([wire.get_weight()*neuron_updates[wire.endNode] for wire in net.get_wires(startNode=node)])
        neuron_output = neuron_outputs[node]
        neuron_updates[node] = neuron_output*(1-neuron_output)*outgoing

    return neuron_updates



def update_weights(net, input_values, desired_output, neuron_outputs, r=1):
    """Performs a single step of back-propagation.  Computes delta_B values and
    weight updates for entire neural net, then updates all weights.  Uses the
    sigmoid function to compute neuron output.  Returns the modified neural net,
    with the updated weights."""
    deltas = calculate_deltas(net, desired_output, neuron_outputs)
    for wire in net.get_wires():
            wire.set_weight(wire.get_weight() + r*node_value(wire.startNode, input_values, neuron_outputs)*deltas[wire.endNode])
    return net

def back_prop(net, input_values, desired_output, r=1, minimum_accuracy=-0.001):
    """Updates weights until accuracy surpasses minimum_accuracy.  Uses the
    sigmoid function to compute neuron output.  Returns a tuple containing:
    (1) the modified neural net, with trained weights
    (2) the number of iterations (that is, the number of weight updates)"""
    counter = 0 
    while True:
        final_output, neuron_outputs = forward_prop(net, input_values, threshold_fn=sigmoid)
        if accuracy(desired_output, final_output) > minimum_accuracy:
            return net, counter
        net = update_weights(net, input_values, desired_output, neuron_outputs, r=r)
        counter += 1 



#### Part 5: Training a Neural Net #############################################

ANSWER_1 = 11
ANSWER_2 = 21
ANSWER_3 = 5
ANSWER_4 = 200
ANSWER_5 = 47

ANSWER_6 = 1
ANSWER_7 = 'checkerboard'
ANSWER_8 = ['small', 'medium', 'large']
ANSWER_9 = 'B'

ANSWER_10 = 'D'
ANSWER_11 = ['A', 'C']
ANSWER_12 = ['A', 'E']


#### SURVEY ####################################################################

NAME = 'Juan Rached'
COLLABORATORS = ''
HOW_MANY_HOURS_THIS_LAB_TOOK = 5
WHAT_I_FOUND_INTERESTING = "Backpropagation"
WHAT_I_FOUND_BORING = "Nothing really"
SUGGESTIONS = ''


#########TESTING####################################

