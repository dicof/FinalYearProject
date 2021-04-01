# -*- coding: utf-8 -*-
"""
Created on Tue Mar 9 11:12:32 2021

@author: Diarmuid
"""
import pandas as pd
import numpy as np
import time
import requests
import json
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

"""
Like clustering101, the aim of this file is to reform the routing methods into a single file,
joining together the distanceMatrix and or-tools sections
"""


def graphhopper_matrix_depot(busStops, depot):
    """ Takes in bus stops and depot (school), and returns distance matrix """
    coords = np.insert(busStops[:, [1, 2]].astype(float), 0, depot, axis=0)
    Long = pd.core.series.Series(coords[:, 1])
    Lat = pd.core.series.Series(coords[:, 0])
    locationArray = list(zip(Long, Lat))
    curbsides = ["right"]*len(locationArray)
    URL = "https://graphhopper.com/api/1/matrix?key=4e2c94b1-14ff-4eb5-8122-cacf2e34043d&ch.disable=true"

    payload = {"points": locationArray,
               "vehicle": "car",
               #"curbsides": curbsides,
               "out_arrays": ["times", "distances"]}

    start = time.time()

    r = requests.post(URL, json=payload)

    end = time.time()

    print(end - start)

    json_data = json.loads(r.text)

    return json_data

def graphhopper_matrix(busStops):
    """ takes in just the bus stops and returns a distance matrix"""
    coords = busStops[:, [1, 2]]
    Long = pd.core.series.Series(coords[:, 1])
    Lat = pd.core.series.Series(coords[:, 0])
    locationArray = list(zip(Long, Lat))
    curbsides = ["right"]*len(busStops)
    URL = "https://graphhopper.com/api/1/matrix?key=4e2c94b1-14ff-4eb5-8122-cacf2e34043d&ch.disable=true"

    payload = {"points": locationArray,
               "vehicle": "car",
               #"curbsides": curbsides,
               "out_arrays": ["times", "distances"]}

    start = time.time()

    r = requests.post(URL, json=payload)

    end = time.time()

    print(end - start)

    json_data = json.loads(r.text)

    return json_data


def ortools_routing(busStops, graphhopperJson):
    """ Takes in bus stops and distance matrix and performs OR-Tools routing"""
    # instatiate the data model
    data = create_data_model(graphhopperJson['distances'], busStops)
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

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

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['students'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        solutionSet = print_solution(data, manager, routing, solution)
        return solutionSet

    else:
        print("No solution.")


def create_data_model(distanceMatrix, busStops):
    """Stores the data for the problem."""
    NUMBERVEHICLES = 15 # This is where you change the maximum number of vehicles
    VEHICLECAPACITY = 70 # This is the maximum number of students that the buses can fit.
    data = {}
    data['distance_matrix'] = distanceMatrix
    data['num_vehicles'] = NUMBERVEHICLES
    data['depot'] = 0 # Index of the depot in the distance matrix

    # students at each stop: also demand at each stop
    data['students'] = np.insert(busStops[:, 5].astype(int), 0, 0, axis=0)
    data['vehicle_capacities'] = [VEHICLECAPACITY] * NUMBERVEHICLES

    return data

def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    #\\TODO: Change row ID to stop ID [or store row ID's]
    total_distance = 0
    total_load = 0
    solutionSet = [[] for i in range(data['num_vehicles'])]
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['students'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
            solutionSet[vehicle_id].append(index)
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))
    print(solutionSet)
    return solutionSet


def turn_indexes_to_stops(solutionSet, busStops):
    """
    This [hopefully temporary] method aims to turn the solution sets, which refer to row indexes, into
    routes of stop IDs.
    """
    stopIDSets = [[0] for i in range(len(solutionSet))]
    for i in range(0, len(solutionSet)):
        # i refers to the vehicle route
        if len(solutionSet[i]) != 1:
            # Non empty list = used bus
            for j in range(0, len(solutionSet[i]) - 1):
                # j is the particular stop on the route
                currentStopIndex = solutionSet[i][j]
                currentStopID = busStops[(currentStopIndex - 1), [1,2]].astype(float)
                stopIDSets[i].append(currentStopID)
            stopIDSets[i].append(0)

    return stopIDSets

