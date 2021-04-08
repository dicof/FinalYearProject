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


def graphhopper_matrix_depot(busStops):
    """ Takes in bus stops and depot (school), and returns distance matrix """
    depot = [44.72048, -63.69856]
    coords = np.insert(busStops[:, [1, 2]].astype(float), 0, depot, axis=0)
    Long = pd.core.series.Series(coords[:, 1])
    Lat = pd.core.series.Series(coords[:, 0])
    locationArray = list(zip(Long, Lat))
    curbsides = ["right"] * len(locationArray)
    URL = "https://graphhopper.com/api/1/matrix?key=4e2c94b1-14ff-4eb5-8122-cacf2e34043d&ch.disable=true"

    payload = {"points": locationArray,
               "vehicle": "car",
               # "curbsides": curbsides,
               "out_arrays": ["times", "distances"]}

    start = time.time()

    r = requests.post(URL, json=payload)

    end = time.time()

    print(end - start)

    json_data = json.loads(r.text)

    return json_data


def student_stop_walking_distances(students, busStops):
    """The aim of this function is to get the walking distance and time for each student to their bus stop"""
    studentCoords = students[:, [1, 2]]
    Long = pd.core.series.Series(studentCoords[:, 1])
    Lat = pd.core.series.Series(studentCoords[:, 0])
    studentsArray = list(zip(Long, Lat))

    # Need to get the location of the stop that that student is going to

    stopCoords = busStops[:, [1, 2]]
    Long = pd.core.series.Series(stopCoords[:, 1])
    Lat = pd.core.series.Series(stopCoords[:, 0])
    stopArray = list(zip(Long, Lat))
    URL = "https://graphhopper.com/api/1/matrix?key=4e2c94b1-14ff-4eb5-8122-cacf2e34043d&ch.disable=true"

    payload = {"from_points": studentsArray,
               "to_points": stopArray,
               "vehicle": "foot",
               "out_arrays": ["times", "distances"]}

    start = time.time()

    r = requests.post(URL, json=payload)

    end = time.time()

    print(end - start)

    json_data = json.loads(r.text)

    # print(json_data)
    return json_data


def check_walking_distances(students, busStops, walking_matrix):
    """Checks walking distances from the graphhopper matrix"""
    walkingDistances = []
    for i in range(len(students)):
        # Get id for stop that student is assigned to
        stopID = students[i, 3]
        stopIndex = np.argwhere(busStops[:, 0] == stopID)[0][0]
        walkingDistance = walking_matrix['distances'][i][stopIndex]
        print("student walking distance = " + str(walkingDistance) + ". Crow = " + str(students[i, 4]))
        walkingDistances.append(walkingDistance)

    print("Average walking distance = " + str(np.average(walkingDistances)))
    return walkingDistances


def graphhopper_matrix(busStops):
    """ takes in just the bus stops and returns a distance matrix"""
    coords = busStops[:, [1, 2]]
    Long = pd.core.series.Series(coords[:, 1])
    Lat = pd.core.series.Series(coords[:, 0])
    locationArray = list(zip(Long, Lat))
    curbsides = ["right"] * len(busStops)
    URL = "https://graphhopper.com/api/1/matrix?key=4e2c94b1-14ff-4eb5-8122-cacf2e34043d&ch.disable=true"

    payload = {"points": locationArray,
               "vehicle": "car",
               # "curbsides": curbsides,
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
    depot = [44.72048, -63.69856]
    # graphhopperJson = graphhopper_matrix_depot(busStops, depot)
    data = create_data_model(graphhopperJson, busStops)
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

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
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


def create_data_model(graphhopperJson, busStops):
    """Stores the data for the problem."""
    NUMBERVEHICLES = 20  # This is where you change the maximum number of vehicles
    VEHICLECAPACITY = 70  # This is the maximum number of students that the buses can fit.
    data = {}
    data['distance_matrix'] = graphhopperJson['distances']
    data['time_matrix'] = graphhopperJson['times']
    data['num_vehicles'] = NUMBERVEHICLES
    data['depot'] = 0  # Index of the depot in the distance matrix

    # students at each stop: also demand at each stop
    data['students'] = np.insert(busStops[:, 5].astype(int), 0, 0, axis=0)
    data['vehicle_capacities'] = [VEHICLECAPACITY] * NUMBERVEHICLES

    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    # \\TODO: Change row ID to stop ID [or store row ID's]
    max_index = len(data['time_matrix'])
    total_distance = 0
    total_load = 0
    solutionSet = [[(0, 0, 0)] for i in range(data['num_vehicles'])]
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        length = routing.IsVehicleUsed(solution, vehicle_id)
        if length:
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_distance = 0
            route_load = 0
            route_time = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_load += data['students'][node_index]
                plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
                print(str(previous_index) + ", " + str(index))
                if previous_index >= max_index:
                    # Replace with depot
                    route_time += data['time_matrix'][0][index]
                    solutionSet[vehicle_id].append((index, route_distance, route_time))
                elif index >= max_index:
                    # Replace with depot
                    route_time += data['time_matrix'][previous_index][0]
                    solutionSet[vehicle_id].append((0, route_distance, route_time))
                else:
                    route_time += data['time_matrix'][previous_index][index]
                    solutionSet[vehicle_id].append((index, route_distance, route_time))
            plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                     route_load)
            plan_output += 'Distance of the route: {}m\n'.format(route_distance)
            plan_output += 'Load of the route: {}\n'.format(route_load)
            print(plan_output)
            total_distance += route_distance
            total_load += route_load
        else:
            print("Vehicle {} is unused".format(vehicle_id))

    print('Total distance of all routes: {}m'.format(total_distance))
    print('Total load of all routes: {}'.format(total_load))
    # print(solutionSet)
    return solutionSet


def turn_indexes_to_stops(solution_set, bus_stops):
    """
    This [hopefully temporary] method aims to turn the solution sets, which refer to row indexes, into
    routes of stop IDs.
    """
    solution_set_stop_ids = []
    for i in range(len(solution_set)):
        # i refers to the route
        if solution_set[i] != (0, 0, 0):
            route_numpy = np.array(solution_set[i], dtype=object)
            for j in range(len(route_numpy)):
                if route_numpy[j, 0] == 0:
                    route_numpy[j, 0] = "depot"
                else:
                    route_numpy[j, 0] = bus_stops[int(route_numpy[j, 0] - 1), 0]
        solution_set_stop_ids.append(route_numpy)
    return solution_set_stop_ids


def calculate_student_travel_time(routes, bus_stops, students, walking_matrix):
    """
    Calculates each student's travel time to the school
    :param routes:
    :param bus_stops:
    :param students:
    :return: students
    """
    students_total_travel_time = []
    for i in range(len(students)):
        # For each student, get walking time to their stop
        students_assigned_stop = students[i, 3]
        student_walking_distance = students[i, 4]
        walking_matrix_index = np.argwhere(walking_matrix['distances'][i] == student_walking_distance)[0][0]
        walking_time_to_stop = walking_matrix['times'][i][walking_matrix_index]  # in minutes
        # Now have to get the distance travelled on the bus
        # This is: time at end of journey - time when students got on bus
        found = False
        j = 0
        bus_travel_time = 0
        while not found:
            # Check each route for the students' assigned stop
            if j == len(routes): print("Error: gone past the number of routes")
            current_route = routes[j]
            stops_on_route = len(current_route)
            placeholder = np.argwhere(current_route[:, 0] == students_assigned_stop)
            if placeholder.size > 0:
                # This means the stop is in this particular route
                index_of_stop_on_route = placeholder[0][0]
                found = True
                # Take the time at end and time at stop when student gets on
                when_student_gets_on = current_route[index_of_stop_on_route, 2]
                when_student_gets_to_school = current_route[(stops_on_route - 1), 2]
                bus_travel_time = when_student_gets_to_school - when_student_gets_on
            else:
                # stop is not on this route, try another
                j = j + 1
        total_travel_time = bus_travel_time + walking_time_to_stop
        students_total_travel_time.append(total_travel_time)
    students = np.insert(students, 5, students_total_travel_time, axis=1)
    return students


"""
for i in range(len(students_reassigned)):
    # For each student, get walking time to their stop
    students_assigned_stop = students_reassigned[i, 3]
    student_walking_distance = students_reassigned[i, 4]
    walking_matrix_index = np.argwhere(walking_matrix['distances'][i] == student_walking_distance)[0][0]
    walking_time_to_stop = walking_matrix['times'][i][walking_matrix_index]  # in minutes
    # Now have to get the distance travelled on the bus
    print("Student " + str(i) + " walking " + str(walking_time_to_stop) + " seconds to cover " + 
    str(student_walking_distance) + "m")
"""
