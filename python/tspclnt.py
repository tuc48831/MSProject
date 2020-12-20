import sys
import argparse

import googlemaps

import tslib_so_interface as tslib


API_KEY = None
# arg parser that has api-key, mutually exclusive indicator to load either cost matrix/coords
def parse_args(arguments):
    parser = argparse.ArgumentParser(prog='tspclnt')
    parser.add_argument('-s', '--store_tuple_space', action='stored_tuple_name', help='store the cost matrix in the tuple space')
    parser.add_argument('-a', '--api_key', dest='api_key', help='The google maps API key for turning coords into a cost matrix, unncessary for --matrix')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--matrix', dest='matrix_file_location', help='an input file of a raw cost matrix, mutually exclusive with --coord')
    group.add_argument('-c', '--coord', dest='coord_file_location', help='an input file of raw gps coordinates to be turned into a cost matrix, mutually exclusive with --matrix')

    return parser.parse_args(arguments)


def convert_coords_to_cost_matrix(address_file_location, api_key):
    # open address file, convert each line to an entry in an array
    address_file = open(address_file_location, 'r')
    lines = address_file.read().splitlines()
    # use google maps api stuff
        # call fx that does google api chunking for me and returns a matrix

    # write matrix to file

    # return file name

if __name__ == '__main__':
    arguments = parse_args(sys.argv)
    if arguments.api_key is None and arguments.coord_file_location:
        print("API key is required to run with ")

    cost_matrix_file_location = None
    #i f we are using coords
    if arguments.coord_file_location:
        cost_matrix_file_location = convert_coords_to_cost_matrix(arguments.coord_file_location, arguments.api_key)
        if arguments.store_tuple_space:
            # call tsput
        else:
            # write calculated cost matrix to a file and remember file name
            cost_matrix_file_location = arguments.matrix_file_location
    # either have raw file cost matrix OR file that we just generated
    #

    print('Hello world!')
    # basic structure
        # load cost matrix from somewhere
        # load a real csv of gps coordinates and generate a cost matrix using google maps api?

        # then just effectively copy his tspwrkr.c code into python?