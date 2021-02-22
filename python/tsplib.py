import pandas
import numpy
import sys

import tslib_so_interface as tslib

# tuple names
cost_matrix_name = "cost_matrix"
start_tuple_name = "start"
global_minimum_name = "global_min"


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
    def __init__(self, num_nodes, cost, tour, next_node):
        # the total number of nodes in the problem
        self.nodes = num_nodes
        # total cost of the tour
        self.cost = cost
        # tour is an array of int indicating node order in the tour
        self.tour = tour
        self.next_node = next_node


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
    return_value = tslib.tsput(global_minimum_name, global_min, sys.getsizeof(global_min))
    if return_value == 1:
        return 1
    else:
        return 0


def read_global_minimum():
    global_min = -1
    retrieved_global_min, retrieved_tuple_name = tslib.tsread(start_tuple_name, sys.getsizeof(global_min))
    return int(retrieved_global_min)


def get_global_minimum():
    global_min = -1
    retrieved_global_min, retrieved_tuple_name = tslib.tsget(start_tuple_name, sys.getsizeof(global_min))
    return int(retrieved_global_min)


def put_best_tour():
    return


def read_best_tour():
    return


def get_best_tour():
    return


def put_effective_calcs():
    return


def read_effective_calcs():
    return


def get_effective_calcs():
    return


def put_node():
    return


def get_node():
    return


def put_finished_node():
    return


def get_finished_node():
    return


def make_child():
    return

