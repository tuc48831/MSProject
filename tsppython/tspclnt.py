import sys
import argparse
import numpy

import googlemaps

from tslib_python import tslib

API_KEY = None


# arg parser that has api-key, mutually exclusive indicator to load either cost matrix/coords
def parse_args(args):
    parser = argparse.ArgumentParser(prog='tspclnt')
    parser.add_argument('-s', '--store_tuple_space', action='stored_tuple_name', help='store the cost matrix in the tuple space')
    parser.add_argument('-a', '--api_key', dest='api_key', help='The google maps API key for turning coords into a cost matrix, unncessary for --matrix')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--matrix', dest='matrix_file_location', help='an input file of a raw cost matrix, mutually exclusive with --coord')
    group.add_argument('-c', '--coord', dest='coord_file_location', help='an input file of raw gps coordinates to be turned into a cost matrix, mutually exclusive with --matrix')

    return parser.parse_args(args)


def convert_coords_to_cost_matrix(address_file_location, api_key):
    # open address file, convert each line to an entry in an array
    address_file = open(address_file_location, 'r')
    lines = address_file.read().splitlines()
    # use google maps api stuff
        # call fx that does google api chunking for me and returns a matrix

    # write matrix as numpy matrix to file

    # return file name
    return "cost_file_matrix_location"


if __name__ == '__main__':
    arguments = parse_args(sys.argv)
    if arguments.api_key is None and arguments.coord_file_location:
        print("API key is required to run with ")

    cost_matrix_file_location = None
    # if we are using coords
    if arguments.coord_file_location:
        cost_matrix_file_location = convert_coords_to_cost_matrix(arguments.coord_file_location, arguments.api_key)
    else:
        # write calculated cost matrix to a file and remember file name
        cost_matrix_file_location = arguments.matrix_file_location

    # either have raw file cost matrix OR file that we just generated
    if arguments.store_tuple_space:
        # load file into a matrix
        matrix = numpy.loadtxt(cost_matrix_file_location, delimiter=",")
        # call tsput on matrix
        print('putting matrix into tuple space: ' + str(matrix))
        tslib.tsput("tsp_matrix", matrix, sys.getsizeof(matrix))

        retrived_matrix = tslib.tsread("tsp_matrix", sys.getsizeof(matrix))
        print('retrieved matrix is: ' + str(retrived_matrix))
        print('raw retrieved matrixs is: ' + retrived_matrix)

    # at this point we have created a raw numpy based cost matrix, and either have the file name or tuple name to pass to workers
        # theoretically the workers should just exist and be waiting for a file/tuple to show up to automatically start working
        # tsp client could receive an arg that tells it to kill the workers after they finish?

    # then just effectively copy his tspwrkr.c code into python?
    sys.exit(0)
