import pandas
import numpy
import sys

import tslib_so_interface as tslib


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
def get_cost_matrix_from_tuple_space(matrix_name, num_vertices):
    dataframe_for_size = pandas.DataFrame(numpy.zeros([num_vertices, num_vertices])*numpy.nan)
    size = len(dataframe_for_size.to_json())
    retrieved_matrix, retrieved_tuple_name = tslib.tsread(matrix_name, size)
    return pandas.read_json(retrieved_matrix)
