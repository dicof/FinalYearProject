# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 12:04:52 2021

@author: Diarmuid
"""
from ortools.linear_solver import pywraplp

from ortools.constraint_solver import routing_enums_pb2

from ortools.constraint_solver import pywrapcp

import json

import numpy as np
# routing002: Test to remove main()

#import test001

import distanceMat001
import test002
import matplotlib.pyplot as plt

busStops = test002.movedStops  # TODO: need to get people at each stop

# depot = (44.65163190605642, -63.61516155604698) #6670 Bayer's Road, pretty far away
depot = (44.7207799, -63.6994861)  # Charles P Allen High School, from Garry's files
graphhopperJson = distanceMat001.graphhopperMatrix(busStops[:, [0, 1]], depot)

distance_matrix = graphhopperJson['distances']

times_matrix = graphhopperJson['times']

# Number of vehicles: arbitrary test value
NUMBERVEHICLES = 15
VEHICLECAPACITY = 70

"""Solve the CVRP problem."""
# Instantiate the data problem.
data = {}
data['distance_matrix'] = distance_matrix
data['num_vehicles'] = NUMBERVEHICLES
data['depot'] = 0

# students at each stop: also demand at each stop
'''Change this line'''
stopulation = busStops[:, 3]
stopulation = np.insert(stopulation, 0, 0, axis=0)
data['students'] = stopulation
data['vehicle_capacities'] = [VEHICLECAPACITY] * NUMBERVEHICLES

# Create the routing index manager.
manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                       data['num_vehicles'], data['depot'])

# Create Routing Model.
routing = pywrapcp.RoutingModel(manager)


def distance_callback(from_index, to_index):
    """Returns the distance between the two nodes."""
    # Convert from routing variable Index to distance matrix NodeIndex.
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['distance_matrix'][from_node][to_node]


transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


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


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    total_distance = 0
    total_load = 0
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
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))


if solution:
    print_solution(data, manager, routing, solution)
else:
    print("No solution.")

solutionDict = {}

for vehicle_id in range(data['num_vehicles']):
    index = routing.Start(vehicle_id)
    solutionDict[vehicle_id] = []
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        solutionDict[vehicle_id].append(node_index)
        previous_index = index
        index = solution.Value(routing.NextVar(index))

routes = {}
for i in range(len(solutionDict)):
    routes[i] = []
    for j in range(1, len(solutionDict[i])):
        f = (busStops[(solutionDict[i][j] - 1), 0], busStops[(solutionDict[i][j] - 1), 1])
        routes[i].append(f)
    routes[i] = np.array(routes[i])
'''
plt.scatter(-63.6994861, 44.7207799, c='green', s=200, alpha = 0.25)
plt.scatter(routes[4][:,1], routes[4][:,0], c='blue', s=30)
plt.scatter(routes[5][:,1], routes[5][:,0], c='red', s=30)
plt.scatter(routes[6][:,1], routes[6][:,0], c='green', s=30)
plt.scatter(routes[7][:,1], routes[7][:,0], c='yellow', s=30)
plt.scatter(routes[8][:,1], routes[8][:,0], c='orange', s=30)
plt.scatter(routes[9][:,1], routes[9][:,0], c='magenta', s=30)
plt.scatter(routes[10][:,1], routes[10][:,0], c='orange', s=30)
plt.scatter(routes[11][:,1], routes[11][:,0], c='lime', s=30)
plt.scatter(routes[12][:,1], routes[12][:,0], c='indigo', s=30)
plt.scatter(routes[13][:,1], routes[13][:,0], c='olive', s=30)
plt.scatter(routes[14][:,1], routes[14][:,0], c='peru', s=30)
'''

# count mention of each stop
countStopMentions = [0] * (len(busStops))
for vehicle_id in range(data['num_vehicles']):
    index = routing.Start(vehicle_id)
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        if node_index != 0:
            countStopMentions[node_index - 1] += 1
        index = solution.Value(routing.NextVar(index))
