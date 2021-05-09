import tslib_so_interface as tslib
import argparse

import tsplib as tsp


# arg parser that has api-key, mutually exclusive indicator to load either cost matrix/coords
def parse_args():
    parser = argparse.ArgumentParser(prog='tspclnt')

    parser.add_argument('-n', '--num_vertices', dest='num_vertices', help='The number of vertices')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-m', '--matrix', dest='matrix_file_location', help='an input file of a raw cost matrix, mutually exclusive with --coord/--store_tuple_space')
    group.add_argument('-s', '--store_tuple_space', action='stored_tuple_name', help='store the cost matrix in the tuple space, mutually e')

    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_args()

    if arguments.matrix_file_location:
        cost_matrix, num_vertices = tsp.get_cost_matrix_and_vertices_from_file(arguments.matrix_file_location)
    elif arguments.store_tuple_space:

    # basic structure
        # load cost matrix from somewhere, OR if neither -m/-s is used, generate a random one?

        # load a real csv of gps coordinates and generate a cost matrix using google maps api?

        # then just effectively copy his tspwrkr.c code into python?