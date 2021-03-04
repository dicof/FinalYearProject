# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 12:04:52 2021

@author: Diarmuid
"""
from ortools.linear_solver import pywraplp

from ortools.constraint_solver import routing_enums_pb2

from ortools.constraint_solver import pywrapcp

import json

#Clustering004: takes bus stops, performs vehicle routing problem (first attempt)

import clustering003

import distanceMat001





busStops = clustering003.busStops

depot = (44.65163190605642, -63.61516155604698)
graphhopperJson = distanceMat001.graphhopperMatrix(busStops[:,[0,1]], depot)

distance_matrix = graphhopperJson['distances']

times_matrix    = graphhopperJson['times']

#Number of vehicles: arbitrary test value
NUMBERVEHICLES = 10


def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = NUMBERVEHICLES
    data['depot'] = 0
    
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}m'.format(max_route_distance))


def store_solution(data, manager, routing, solution):
    """Stores solution in dict of lists, showing vehicle routes"""
    solutionDict = {}

    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        solutionDict[vehicle_id] = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            solutionDict[vehicle_id].append(node_index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
    return solutionDict        
    


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    
    data = create_data_model()
    #print(data['distance_matrix'])
    #print(type(data['distance_matrix']))
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),data['num_vehicles'], data['depot'])
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        1000000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    if solution:    
        print_solution(data, manager, routing, solution)
        solutionSet = store_solution(data, manager, routing, solution)


if __name__ == '__main__':
    main()


