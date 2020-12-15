import tslib_so_interface as tslib
import argparse

# arg parser that has api-key, mutually exclusive indicator to load either cost matrix/coords
def parse_args(arguments):
    parser = argparse.ArgumentParser(prog='tspclnt')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-m', '--matrix', dest='matrix_file_location', help='an input file of a raw cost matrix, mutually exclusive with --coord/--store_tuple_space')
    group.add_argument('-s', '--store_tuple_space', action='stored_tuple_name', help='store the cost matrix in the tuple space, mutually e')

    return parser.parse_args(arguments)


if __name__ == '__main__':
    print('Hello world!')
    # basic structure
        # load cost matrix from somewhere, OR if neither -m/-s is used, generate a random one?
        # load a real csv of gps coordinates and generate a cost matrix using google maps api?

        # then just effectively copy his tspwrkr.c code into python?