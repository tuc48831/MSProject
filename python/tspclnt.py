import sys
import argparse
import pandas
import datetime

import tsplib as tsp

API_KEY = None


# arg parser that has api-key, mutually exclusive indicator to load either cost matrix/coords
def parse_args():
    parser = argparse.ArgumentParser(prog='tspclnt')
    # for now always store matrix in tuple space
    parser.add_argument('-s', '--store_matrix_tuple_space', dest='store_matrix_tuple_space', help='store the cost matrix in the tuple space')
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
    # move coord parsing to here

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


def enqueue(num_nodes, cost, tour):
    pass


def dequeue(num_nodes, cost, tour):
    pass


def write_output_file(global_min, best_found_tour: tsp.TspTour, effective_calculations, elapsed_time):
    file = open('tsp_out.txt', 'a+')
    result_string = 'global_minimum: ' + str(global_min) + ' best_tour: ' + str(best_found_tour.order) + \
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

    cost_matrix, num_vertices = tsp.get_cost_matrix_and_vertices_from_file(cost_matrix_file_location)

    # call tsput on matrix if necessary
    if arguments.store_matrix_tuple_space:
        tsp.put_cost_matrix_in_tuple_space("tsp_matrix", cost_matrix)

    temp_tour, cur_tour = None, None
    node_count = 0
    # start the problem
    start_time = datetime.datetime.now()
    global_minimum = float('inf')
    local_minimum = float('inf')
    processors = tsp.get_num_processors()

    tsp.cost_matrix = cost_matrix
    tsp.TspTour.set_max_vertices(num_vertices)

    # not sure I need this?
    best_tour = [1 * num_vertices]
    tsp.put_best_tour(best_tour)
    best_tour_found = False

    num_processors = tsp.get_num_processors()
    search_tree_list = tsp.TspSearchTreeList.get_instance()

    while search_tree_list.get_node_count() <= num_processors * arguments.load_balancing_constant \
            and not search_tree_list.empty():
        temp_node = search_tree_list.dequeue()
        if temp_node.cost < global_minimum:
            for i in range(num_vertices):
                child = tsp.make_child()
                if child is not None:
                    if child.is_complete(num_vertices):
                        if child.cost < global_minimum:
                            global_minimum = child.cost
                            best_tour = child.order
                            best_tour_found = True
                    else:
                        effective_calcs = tsp.get_effective_calcs()
                        effective_calcs += 1
                        tsp.put_effective_calcs(effective_calcs)
                        search_tree_list.enqueue(child)

    i = 0

    if not best_tour_found:
        while not search_tree_list.empty():
            temp_node = search_tree_list.dequeue()
            i += 1
            node_identifier = "node{}".format(str(i).zfill(5))
            tsp.put_tour(temp_node, node_identifier)

        tuples_sent = i

        tuples_processed = 0
        while tuples_processed < tuples_sent:
            finished_name = "ff*"
            tsp.get_tour(finished_name)
            tuples_processed += 1
    # else best tour already found above
    else:
        term_node = tsp.TspTour(-1, -1, -1)
        tsp.put_tour(term_node, "node{}".format(str("").zfill(5)))

    end_time = datetime.datetime.now()
    running_time = end_time - start_time
    best_tour = tsp.get_best_tour(num_vertices)
    effective_calcs = tsp.get_effective_calcs()
    write_output_file(global_minimum, best_tour, effective_calcs, running_time)

    sys.exit(0)
