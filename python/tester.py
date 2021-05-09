import sys
import argparse
import pandas
import datetime

import tsplib as tsp

API_KEY = None
search_tree_list = None


# arg parser that has api-key, mutually exclusive indicator to load either cost matrix/coords
def parse_args():
    parser = argparse.ArgumentParser(prog='tspclnt')
    parser.add_argument('-s', '--store_tuple_space', dest='stored_tuple_name', help='store the cost matrix in the tuple space')
    parser.add_argument('-a', '--api_key', dest='api_key', help='The google maps API key for turning coords into a cost matrix, unncessary for --matrix')
    # args with defaults
    parser.add_argument('-n', '--nodes', dest='num_nodes', default=20, help='The maximum number of nodes')
    parser.add_argument('-l', '--load_balance', dest='load_balancing_constant', default=100, help='The load balancing constant')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--matrix', dest='matrix_file_location', help='an input file of a raw cost matrix, mutually exclusive with --coord')
    group.add_argument('-c', '--coord', dest='coord_file_location', help='an input file of raw gps coordinates to be turned into a cost matrix, mutually exclusive with --matrix')

    args = parser.parse_args()
    if args.api_key and not args.coord_file_location:
        print("API key is required to run with coordinates file option")
        sys.exit(1)
    return args


def convert_coords_to_cost_matrix(address_file_location, api_key):
    # open address file, convert each line to an entry in an array
    address_file = open(address_file_location, 'r')
    lines = address_file.read().splitlines()
    # use google maps api stuff
        # call fx that does google api chunking for me and returns a matrix

    # write matrix as numpy matrix to file

    # return file name
    return "cost_file_matrix_location"


def write_output_file(global_min, best_found_tour, effective_calculations, elapsed_time):
    file = open('tsp_out.txt', 'a+')
    result_string = 'global_minimum: ' + str(global_min) + ' best_tour: ' + str(best_found_tour) + \
                    ' effective_calcs: ' + str(effective_calculations) + ' elapsed_time: ' + str(elapsed_time)
    file.write(str(datetime.datetime.now()) + ' -- results = ' + result_string + '\n')
    file.close()


if __name__ == '__main__':
    arguments = parse_args()

    cost_matrix_file_location = None
    # if we are using coords
    if arguments.coord_file_location:
        cost_matrix_file_location = convert_coords_to_cost_matrix(arguments.coord_file_location, arguments.api_key)
    else:
        # write calculated cost matrix to a file and remember file name
        cost_matrix_file_location = arguments.matrix_file_location

    # load file into a matrix
    matrix = pandas.read_csv(cost_matrix_file_location, delimiter=",", header=None)
    # TODO: # double check matrix squareness and place dimension into tuple space???
        # its the start tuple lmao
    # call tsput on matrix
    tsp.put_cost_matrix_in_tuple_space("tsp_matrix", matrix)
    retrieved_matrix = tsp.get_cost_matrix_from_tuple_space("tsp_matrix", 6)

    best_tour = [6, 5, 4, 3, 2, 1]
    tsp.put_best_tour(best_tour, 6)
    retrieved_best_tour = tsp.get_best_tour(6)
    print('retrieved best_tour is: ' + str(retrieved_best_tour))

    effective_calcs = 1234509876
    print("effective calcs is: {}".format(effective_calcs))
    tsp.put_effective_calcs(effective_calcs)
    retrieved_effective_calcs = tsp.get_effective_calcs()
    print("retrieved effective calcs is: {}".format(retrieved_effective_calcs))

    tsp.TspTour.set_max_vertices(10)
    node = tsp.TspTour(10, 1122334455, "1,3,2,4,6,8,5,7,9,10")
    node_name = tsp.node_prefix + "_001"
    print("node name is: {} and value is: {}".format(node_name, node.to_json()))
    tsp.put_tour(node, node_name)
    retrieved_node = tsp.get_tour(node_name)
    print("retrieved node name is: {} and retrieved value is: {}".format(node_name, retrieved_node.to_json()))

    sys.exit(0)
