import pandas
import numpy
import sys

import tslib_so_interface as tslib
from collections import namedtuple
import json
from json import JSONEncoder

# tuple names
cost_matrix_name = "cost_matrix"
start_tuple_name = "start"
global_minimum_name = "global_min"
best_tour_name = "best_tour"
effective_calcs_name = "effective_calcs"
node_prefix = "tn"


class TspSearchTreeList:
    __instance = None
    __search_tree_list = None
    __node_count = 0

    @staticmethod
    def get_instance():
        if TspSearchTreeList.__instance is None:
            TspSearchTreeList()
        return TspSearchTreeList.__instance

    def __init__(self):
        if TspSearchTreeList.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TspSearchTreeList.__instance = self

    def empty(self):
        return self.__search_tree_list is None

    def get_node_count(self):
        return self.__node_count

    def enqueue(self, tsp_node):
        if tsp_node is not isinstance(tsp_node, TspNode):
            return
        self.__node_count += 1
        return

    def dequeue(self):
        if self.empty():
            return None
        self.__node_count -= 1
        return


class TspNode:
    def __init__(self, num_nodes, cost, order, next_node=None):
        # the total number of nodes in the problem
        self.num_nodes = num_nodes
        # tour is an array of int indicating node order in the tour
        self.cost = cost
        self.order = order
        self.next_node = next_node

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    @staticmethod
    def from_json_string(json_string):
        real_json = json.loads(json_string)
        num_nodes = real_json['num_nodes']
        cost = real_json['cost']
        order = real_json['order']
        if 'next_node' in real_json:
            return TspNode(num_nodes, cost, order, real_json['next_node'])
        else:
            return TspNode(num_nodes, cost, order)


example_node_for_size = TspNode(sys.maxsize, sys.maxsize, sys.maxsize, None)


def get_num_processors():
    return tslib.uvr_cores()


def put_cost_matrix_in_tuple_space(matrix_name, matrix):
    matrix_as_json_string = matrix.to_json()
    size = len(matrix_as_json_string)
    return_value = tslib.tsput(matrix_name, matrix_as_json_string, size)
    if return_value == 1:
        return 1
    else:
        return 0


# the most abstract form of this function is simply the name, and the number of vertices.
# one needs to know the number of bytes they are retrieving from the tuple space so they can create a string buffer
# large enough to hold it, but not so large as to be unworkable, and from the number of vertices we can create an
# empty pandas dataframe of the same square of number of vertices to get the size we need
def read_cost_matrix_from_tuple_space(matrix_name, num_vertices):
    dataframe_for_size = pandas.DataFrame(numpy.zeros([num_vertices, num_vertices])*numpy.nan)
    size = len(dataframe_for_size.to_json())
    retrieved_matrix, retrieved_tuple_name = tslib.tsread(matrix_name, size)
    return pandas.read_json(retrieved_matrix)


def get_cost_matrix_from_tuple_space(matrix_name, num_vertices):
    dataframe_for_size = pandas.DataFrame(numpy.zeros([num_vertices, num_vertices])*numpy.nan)
    size = len(dataframe_for_size.to_json())
    retrieved_matrix, retrieved_tuple_name = tslib.tsget(matrix_name, size)
    return pandas.read_json(retrieved_matrix)


def put_start(num_dimensions):
    return_value = tslib.tsput(start_tuple_name, num_dimensions, sys.getsizeof(num_dimensions))
    if return_value == 1:
        return 1
    else:
        return 0


def read_start():
    num_dimensions = -1
    retrieved_num_dimensions, retrieved_tuple_name = tslib.tsread(start_tuple_name, sys.getsizeof(num_dimensions))
    return int(retrieved_num_dimensions)


def get_start():
    num_dimensions = -1
    retrieved_num_dimensions, retrieved_tuple_name = tslib.tsget(start_tuple_name, sys.getsizeof(num_dimensions))
    return int(retrieved_num_dimensions)


def put_global_minimum(global_min):
    return_value = tslib.tsput(global_minimum_name, str(global_min), sys.getsizeof(str(global_min)))
    if return_value == 1:
        return 1
    else:
        return 0


def read_global_minimum():
    global_min = sys.maxsize
    retrieved_global_min, retrieved_tuple_name = tslib.tsread(global_minimum_name, sys.getsizeof(str(global_min)))
    return int(retrieved_global_min)


def get_global_minimum():
    global_min = sys.maxsize
    retrieved_global_min, retrieved_tuple_name = tslib.tsget(global_minimum_name, sys.getsizeof(str(global_min)))
    return int(retrieved_global_min)


def put_best_tour(best_tour, num_vertices):
    # use matrix size * size of int, which should be enough
    return_value = tslib.tsput(best_tour_name, str(best_tour), sys.getsizeof(int()) * num_vertices)
    if return_value == 1:
        return 1
    else:
        return 0


def read_best_tour(num_vertices):
    best_tour_size = sys.getsizeof(int()) * num_vertices
    retrieved_best_tour, retrieved_tuple_name = tslib.tsread(best_tour_name, best_tour_size)
    # this slice and split is to convert "[1, 2, 3]" to a list of strings e.g. ["1", "2", "3"]
    return [int(i) for i in retrieved_best_tour[1:-1].split(", ")]


def get_best_tour(num_vertices):
    best_tour_size = sys.getsizeof(int()) * num_vertices
    retrieved_best_tour, retrieved_tuple_name = tslib.tsget(best_tour_name, best_tour_size)
    # this slice and split is to convert "[1, 2, 3]" to a list of strings e.g. ["1", "2", "3"]
    return [int(i) for i in retrieved_best_tour[1:-1].split(", ")]


def put_effective_calcs(effective_calcs):
    return_value = tslib.tsput(effective_calcs_name, str(effective_calcs), sys.getsizeof(str(effective_calcs)))
    if return_value == 1:
        return 1
    else:
        return 0


def read_effective_calcs():
    effective_calcs = -1
    retrieved_effective_calcs, retrieved_tuple_name = tslib.tsread(effective_calcs_name,
                                                                   sys.getsizeof(str(effective_calcs)))
    return int(retrieved_effective_calcs)


def get_effective_calcs():
    effective_calcs = sys.maxsize
    retrieved_effective_calcs, retrieved_tuple_name = tslib.tsget(effective_calcs_name,
                                                                  sys.getsizeof(str(effective_calcs)))
    return int(retrieved_effective_calcs)


def put_node(node, node_identifier):
    node_as_json = node.to_json()
    node_as_json_size = len(node_as_json)
    # store the size of the tuple in its
    node_size_identifier = node_identifier + "_size"
    return_value = tslib.tsput(node_size_identifier, str(node_as_json_size), sys.getsizeof(str(int())))
    if return_value == 1:
        return 1
    return_value = tslib.tsput(node_identifier, node_as_json, node_as_json_size)
    if return_value == 1:
        return 1
    else:
        return 0


def read_node(node_identifier):
    # of note, this does not currently support regex getting of nodes, only direct naming
    node_size_identifier = node_identifier + "_size"
    retrieved_node_size = read_node_size(node_size_identifier)
    print("retrieved node size is: {}".format(retrieved_node_size))
    retrieved_node_as_json, retrieved_node_identifier = tslib.tsread(node_identifier, retrieved_node_size)
    print("retrieved node as json is: {}".format(retrieved_node_as_json))
    node = TspNode.from_json_string(retrieved_node_as_json)
    return node


def get_node(node_identifier):
    # of note, this does not currently support regex getting of nodes, only direct naming
    node_size_identifier = node_identifier + "_size"
    retrieved_node_size = get_node_size(node_size_identifier)
    print("retrieved node size is: {}".format(retrieved_node_size))
    retrieved_node_as_json, retrieved_node_identifier = tslib.tsget(node_identifier, retrieved_node_size)
    print("retrieved node as json is: {}".format(retrieved_node_as_json))
    node = TspNode.from_json_string(retrieved_node_as_json)
    return node


def read_node_size(node_size_identifier):
    retrieved_node_size, retrieved_node_size_identifier = tslib.tsread(node_size_identifier, sys.getsizeof(str(int())))
    return int(retrieved_node_size)


def get_node_size(node_size_identifier):
    retrieved_node_size, retrieved_node_size_identifier = tslib.tsget(node_size_identifier, sys.getsizeof(str(int())))
    return int(retrieved_node_size)


def put_finished_node(finished_node, node_identifier):
    return


def read_finished_node(node_identifier):
    return


def get_finished_node(node_identifier):
    return


def make_child():
    return

