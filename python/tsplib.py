import pandas
import numpy
import sys

import tslib_so_interface as tslib
import json

# tuple names
cost_matrix_name = "cost_matrix"
start_tuple_name = "start"
global_minimum_name = "global_min"
best_tour_name = "best_tour"
effective_calcs_name = "effective_calcs"
node_prefix = "tsp_node"
finished_node_prefix = "finished_node"

# global variables
t_global_minimum = sys.maxsize
local_minimum = sys.maxsize

cost_matrix = None


def calculate_cost_between_nodes(start_node: int, destination_node: int):
    if not cost_matrix:
        print("ERROR: tried referencing cost_matrix before it was initialized")
        sys.exit(1)
    return cost_matrix[start_node][destination_node]


# TODO: investigate replacing this with some builtin python class like a queue?
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
        if tsp_node is not isinstance(tsp_node, TspTour):
            return False
        if self.empty():
            self.__search_tree_list = tsp_node
        else:
            tsp_node.next_node = self.__search_tree_list
            self.__search_tree_list = tsp_node
        self.__node_count += 1
        return True

    def dequeue(self):
        if self.empty():
            return None
        else:
            temp_node = self.__search_tree_list
            self.__search_tree_list = temp_node.next_node
            self.__node_count -= 1
            return temp_node


class TspTour:
    max_vertices = None

    def __init__(self, num_nodes, cost, order: [int]):
        # the total number of nodes in the problem
        self.num_nodes = num_nodes
        # in case None or some non-existant order is passed in, make an empty array
        if order is None or not order:
            self.order = []
        else:
            self.order = order
        self.cost = cost

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def is_complete(self, num_vertices):
        return self.num_nodes == num_vertices

    def add_node_to_tour(self, node_to_add: int):
        self.order.append(node_to_add)
        self.num_nodes += 1
        self.cost += calculate_cost_between_nodes(cost_matrix, self.order[-1], node_to_add)

    def tour_contains_node(self, node_to_check):
        # TODO: potentially add a set object to prevent linear lookup for larger problems?
        for node_in_tour in self.order:
            if node_to_check == node_in_tour:
                return True
        return False

    @staticmethod
    def from_json_string(json_string):
        print(json_string)
        real_json = json.loads(json_string)
        num_nodes = real_json['num_nodes']
        cost = real_json['cost']
        order = real_json['order']
        return TspTour(num_nodes, cost, order)

    @staticmethod
    def set_max_vertices(max_vertices):
        TspTour.max_vertices = max_vertices

    @staticmethod
    def get_max_vertices():
        if not TspTour.max_vertices:
            print("ERROR: tried to determine node info without setting max vertices")
            sys.exit(1)
        return TspTour.max_vertices

    @staticmethod
    def get_max_tour_size():
        if not TspTour.max_vertices:
            print("ERROR: tried to determine node info without setting max vertices")
            sys.exit(1)
        return sys.getsizeof(TspTour(TspTour.max_vertices, sys.maxsize, [0]*TspTour.max_vertices).to_json())


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


def get_cost_matrix_and_vertices_from_file(cost_matrix_file_location):
    read_cost_matrix = pandas.read_csv(cost_matrix_file_location, delimiter=",", header=None)
    matrix_shape = cost_matrix.shape
    if matrix_shape[0] != matrix_shape[1]:
        print('Given matrix shape: {} was not square, terminating tspclnt.py!'.format(str(matrix_shape)))
        sys.exit(1)
    num_vertices = matrix_shape[0]
    return read_cost_matrix, num_vertices


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


def put_tour(tour, tour_identifier):
    tour_as_json = tour.to_json()
    tour_as_json_size = TspTour.get_max_tour_size()
    return_value = tslib.tsput(tour_identifier, tour_as_json, tour_as_json_size)
    if return_value == 1:
        return 1
    else:
        return 0


def read_tour(tour_identifier):
    # of note, this does not currently support regex getting of nodes, only direct naming
    tour_size = TspTour.get_max_tour_size()
    retrieved_tour_as_json, retrieved_tour_identifier = tslib.tsread(tour_identifier, tour_size)
    print("retrieved node as json is: {}".format(retrieved_tour_as_json))
    node = TspTour.from_json_string(retrieved_tour_as_json)
    return node


def get_tour(tour_identifier):
    # of note, this does not currently support regex getting of nodes, only direct naming
    tour_size = TspTour.get_max_tour_size()
    retrieved_node_as_json, retrieved_node_identifier = tslib.tsget(tour_identifier, tour_size)
    print("retrieved node as json is: {}".format(retrieved_node_as_json))
    node = TspTour.from_json_string(retrieved_node_as_json)
    return node


# not 100% sure i need functions specifically for finished nodes or not?
def put_finished_node(finished_node, node_identifier):
    return


def read_finished_node(node_identifier):
    return


def get_finished_node(node_identifier):
    return


def add_node_to_tour(base_tour: TspTour, node_num: int, ):
    """
    returns either None, or a tsp tour if the branch being investigated is 'good'
    """
    found = False





    if False:
        return None
    return child
