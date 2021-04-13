# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 12:40:56 2021

@author: Diarmuid
This file features the methods needed to perform the clustering operations.
"""

from sklearn.cluster import KMeans
from kneed import KneeLocator
import geopy.distance
import numpy as np
import busStopCheck
import time

import routing101 as route


# CLEANED
def distance_constrained_cluster(students):
    """
    This method takes in the addresses of students, and returns the minimum amount of bus stops that obey the given
    distance constraints. These bus stops have been calculated independent of the road network, using only the
    x, y co-ordinates.
    :param students:
    :return: bus_stops, students
    """

    # This method takes in the students addresses, and returns distance constrained clusters
    # That follow the distances provided by the school board for different grades' permissible
    # walking distances
    # In this particular example, grade 8 and above are allowed walk max 400 metres
    MAX_DISTANCE = 400
    coords = students[:, [1, 2]]
    number_students = len(students)

    k_means_kwargs = {
        "init": "random",
        "n_init": 10,
        "max_iter": 300,
        "random_state": 17,  # Set to produce replicable pseudorandom data
    }
    # storing the sums of the squared errors (SSE)
    sse = []
    for k in range(1, 30):
        k_means = KMeans(n_clusters=k, **k_means_kwargs)
        k_means.fit(coords)
        sse.append(k_means.inertia_)

    # This code graphs the SSE for investigation

    """
    plt.style.use("fivethirtyeight")
    plt.plot(range(1,30), sse)
    plt.xticks(range(1, 30))
    plt.xlabel("Number of Clusters")
    plt.ylabel("SSE")
    plt.show()
    """

    kl = KneeLocator(range(1, 30), sse, curve="convex", direction="decreasing")
    number_clusters = kl.elbow

    # Investigate opt clusters to see if it agrees with max walking constraints

    # Check each point to its cluster centre
    # If its greater than the distance, add a cluster
    # Keep going until satisfied

    solution_found = False
    while not solution_found:
        satisfied = True
        k_means = KMeans(n_clusters=number_clusters, **k_means_kwargs)
        k_means.fit(coords)
        y_k_means = k_means.predict(coords)
        centers = k_means.cluster_centers_
        i = 0
        while satisfied:
            # Get cluster center for specific student
            cluster_mean = centers[y_k_means[i]]
            # Calculate distance between student and centre
            dst = geopy.distance.distance(coords[i], cluster_mean).m
            # Using 400metres in this particular one
            if dst > MAX_DISTANCE:
                # Not permissible, add another cluster
                satisfied = False
                number_clusters += 1
            else:
                i += 1
                if i == number_students:
                    # Solution satisfies constraints
                    satisfied = False
                    solution_found = True

    # Change centers into bus stops and add the number of students at each
    unique, counts = np.unique(y_k_means, return_counts=True)
    bus_stops = np.insert(centers, 2, counts, axis=1)
    # Adding unique stop id so stops can be referred to without their row index, which allows safer dropping of
    # stops
    # \\TODO: Run this by Simon for thoughts on stop naming. For now, stops start at 101
    stop_IDs = range(101, (len(bus_stops) + 101))
    bus_stops = np.insert(bus_stops, 0, stop_IDs, axis=1)
    # Things that need to be returned: array of busStops, students
    # with y_k_means appended
    # Now stop IDs have been added, students should use that
    students = np.insert(students, 3, (y_k_means + 101), axis=1)
    return bus_stops, students


def add_extra_stops(students, max_stop_ID):
    """
    This method takes in any students that are still walking above 400 metres, and re-clusters them, with
    the aim of introducing new stops that will bring their walking distance below 400 metres.
    :param students:
    :return:
    """
    MAX_DISTANCE = 400
    coords = students[:, [1, 2]]
    number_students = len(students)

    k_means_kwargs = {
        "init": "random",
        "n_init": 10,
        "max_iter": 300,
        "random_state": 17,  # Set to produce replicable pseudorandom data
    }
    # storing the sums of the squared errors (SSE)
    sse = []
    for k in range(1, 30):
        k_means = KMeans(n_clusters=k, **k_means_kwargs)
        k_means.fit(coords)
        sse.append(k_means.inertia_)

    # This code graphs the SSE for investigation

    """
    plt.style.use("fivethirtyeight")
    plt.plot(range(1,30), sse)
    plt.xticks(range(1, 30))
    plt.xlabel("Number of Clusters")
    plt.ylabel("SSE")
    plt.show()
    """

    kl = KneeLocator(range(1, 30), sse, curve="convex", direction="decreasing")
    number_clusters = kl.elbow

    # Investigate opt clusters to see if it agrees with max walking constraints

    # Check each point to its cluster centre
    # If its greater than the distance, add a cluster
    # Keep going until satisfied

    solution_found = False
    while not solution_found:
        satisfied = True
        k_means = KMeans(n_clusters=number_clusters, **k_means_kwargs)
        k_means.fit(coords)
        y_k_means = k_means.predict(coords)
        centers = k_means.cluster_centers_
        i = 0
        while satisfied:
            # Get cluster center for specific student
            cluster_mean = centers[y_k_means[i]]
            # Calculate distance between student and centre
            dst = geopy.distance.distance(coords[i], cluster_mean).m
            # Using 400metres in this particular one
            if dst > MAX_DISTANCE:
                # Not permissible, add another cluster
                satisfied = False
                number_clusters += 1
            else:
                i += 1
                if i == number_students:
                    # Solution satisfies constraints
                    satisfied = False
                    solution_found = True

    # Change centers into bus stops and add the number of students at each
    unique, counts = np.unique(y_k_means, return_counts=True)
    bus_stops = np.insert(centers, 2, counts, axis=1)
    # Adding unique stop id so stops can be referred to without their row index, which allows safer dropping of
    # stops
    stop_IDs = range(int(max_stop_ID) + 1, (len(bus_stops) + int(max_stop_ID) + 1))
    bus_stops = np.insert(bus_stops, 0, stop_IDs, axis=1)
    # Things that need to be returned: array of busStops, students
    # with y_k_means appended
    # Now stop IDs have been added, students should use that
    # students[:, 3] = (y_k_means + max_stop_ID + 1)

    return bus_stops


def snap_stops_to_roads_iterative_search(new_stops):
    """
    This function snaps the newly created stops to suitable roads. It differs from the other snapping function in that
    it moves the permissible search distance for roads out step by step, aiming to find the closest suitable road to
    the stop location.
    :param new_stops:
    :return: fixed_stops
    """

    start = time.time()
    fixed_coords = []
    for i in range(0, len(new_stops)):
        test_coords = new_stops[i, [1, 2]]
        fix = busStopCheck.return_suitable_location_outSearch(test_coords)  # \\TODO: AGAIN CHANGE NAMING IN BSC
        fixed_coords.append(fix)

        print(i)
    end = time.time()
    print(str(end - start) + " seconds to complete stop relocation.")
    changed_stops = np.array(fixed_coords, dtype=object)
    fixed_stops = np.insert(changed_stops, 0, new_stops[:, 0], axis=1)
    # busStops now has lat, lon, distance moved, type road moved to
    # Drop any stops with none as road #\\TODO: Check this
    length_before_dropping_unmoved = len(fixed_stops)
    fixed_stops = fixed_stops[fixed_stops[:, 4] != 'none']
    length_after_dropping_unmoved = len(fixed_stops)
    print(
        str(length_before_dropping_unmoved - length_after_dropping_unmoved) + " stops unsuccessfully moved. Now " + str(
            length_after_dropping_unmoved) + " stops remaining.")
    unique, counts = np.unique(fixed_stops[:, 4], return_counts=True)
    print("Categories of stops:")
    list_of_stops = list(zip(unique, counts))
    print(np.array(list_of_stops))

    return fixed_stops


# CLEANED, UNUSED \\TODO: EITHER USE OR DELETE
def snap_stops_check_sidewalks(bus_stops):
    """
    Takes in the bus Stops formed by the k_means constrained clustering
    and returns stops that have been snapped to suitable locations NOW CONTAINING SIDEWALKS
    :param bus_stops:
    :return: new_stops
    """
    start = time.time()
    fixed_coords = []
    for i in range(0, len(bus_stops)):
        test_coords = bus_stops[i, [1, 2]]
        fix = busStopCheck.return_suitable_location2(test_coords)  # \\TODO: CHANGE NAME OF FUNCTION IN BUSSTOPCHECK
        fixed_coords.append(fix)

        print(i)
    end = time.time()
    print(str(end - start) + " seconds to complete stop relocation.")
    new_stops = np.array(fixed_coords)
    new_stops = np.insert(new_stops, 0, bus_stops[:, 0], axis=1)
    # busStops now has lat, lon, distance moved, type road moved to
    # Drop any stops with none as road #\\TODO: Check this
    new_stops = new_stops[new_stops[:, 4] != 'none']
    return new_stops


def snap_stops_to_roads(bus_stops):
    """
    Takes in bus stops that have been formed by latitude/longitude clustering
    and returns stops that have been snapped to suitable roads using busStopCheck.return_suitable_location2
    WARNING: method takes about 10 minutes for 227 stops
    :param bus_stops:
    :return: new_stops
    """

    start = time.time()
    fixed_coords = []
    for i in range(0, len(bus_stops)):
        test_coords = bus_stops[i, [1, 2]]
        fix = busStopCheck.return_suitable_location2(test_coords)  # \\TODO: AGAIN CHANGE NAMING IN BSC
        fixed_coords.append(fix)

        print(i)
    end = time.time()
    print(str(end - start) + " seconds to complete stop relocation.")
    new_stops = np.array(fixed_coords, dtype=object)
    new_stops = np.insert(new_stops, 0, bus_stops[:, 0], axis=1)
    # busStops now has lat, lon, distance moved, type road moved to
    # Drop any stops with none as road #\\TODO: Check this
    new_stops = new_stops[new_stops[:, 4] != 'none']
    return new_stops


# CLEANED
def stop_amalgamation(bus_stops, distance_matrix):
    """
    This function will take the distance matrix, and combine any stops together that are within 100 metres,
    choosing the one that's closest to every other stop by averaging the distance in the distance matrix
    :param bus_stops:
    :param distance_matrix:
    :return: bus_stops
    """
    distance_matrix_np = np.array(distance_matrix['distances'])
    # suitableStops = []
    kept_stops = [0] * len(bus_stops)  # a -1 in this means the stop has been dropped
    movable_distance = 100
    for i in range(0, len(distance_matrix_np)):
        # row
        for j in range((i + 1), len(distance_matrix_np)):
            # column
            if distance_matrix_np[i, j] < movable_distance:
                # append the result
                # suitableStops.append((i, j))
                print("Stop " + str(i) + " and " + str(j) + " are " + str(distance_matrix_np[i, j]) + "m apart")
                # average the distances between each stop and every other stop in the distance matrix
                avg_length_i = np.average(distance_matrix_np[i])
                avg_length_j = np.average(distance_matrix_np[j])
                if avg_length_j < avg_length_i:
                    # choose i
                    kept_stops[i] = -1
                    print("Stop " + str(j) + " has been kept")
                else:
                    # either i is smaller or they're equal, keep i
                    kept_stops[j] = -1
                    print("Stop " + str(i) + " has been kept")
    # busStops = np.insert(busStops, 2, range(0, len(busStops)), axis=1) # This is the ID of the bus stop
    bus_stops = np.insert(bus_stops, 6, kept_stops, axis=1)
    bus_stops = bus_stops[bus_stops[:, 6] != '-1']
    bus_stops = bus_stops[:, 0:6]
    return bus_stops


def new_stop_amalgamation(students, bus_stops, distance_matrix, walking_matrix):
    """
    For every stop, this function will
    1) Get students at stop
    2) Check if there are any stops in the vicinity that they can all walk to
    3) Evaluate which stop is better located by distance matrix, and move all students to that stop.
    4) Set students at old stop to zero

    :param students:
    :param bus_stops:
    :param distance_matrix:
    :param walking_matrix:
    :return:
    """
    distance_matrix_np = np.array(distance_matrix['distances'])
    walking_matrix_np = np.array(walking_matrix['distances'])
    for i in len(bus_stops):
        # i = stop
        stop_id = bus_stops[i, 0]
        students_at_stop = students[students[:, 3] == stop_id]
        suitable_stops = []
        for student in len(students_at_stop):
            # For each student, get the index of every stop that is within 400 metres
            print("temp")
        # Check if stop is superceded


def student_reassignment_walking_matrix(bus_stops, students, walking_matrix):
    """
    New method that reassigns students based on the graphhhopper API walking distance matrix. This API has a minutely
    limit that is very easy to violate, so this method must either be used sparingly or be surrounded by a try/catch
    loop that will retry until a suitable response appears (Or the API can be upgraded from the free version).
    This method will also drop any stops that have no students assigned.
    :param bus_stops:
    :param students:
    :param walking_matrix:
    :return: bus_stops, students
    """
    new_stops = []
    new_distances = []
    # If students have been through this process already, then there is no need to insert sometimes, and instead,
    # certain columns should be replaced
    number_columns_students = np.shape(students)[1]
    number_columns_bus_stops = np.shape(bus_stops)[1]
    # \\TODO: Make sure this still works
    new_columns_needed = False
    students_at_stop = [0] * len(bus_stops)
    if number_columns_students <= 4:
        # Need to add the new columns TO STUDENTS, maybe not to stops
        new_columns_needed = True
        print("Columns being added to students")
        if number_columns_bus_stops < 6:
            bus_stops = np.insert(bus_stops, 5, students_at_stop, axis=1)
        else:
            # need to set the students at stops to zero
            bus_stops[:, 5] = students_at_stop
    else:
        print("No columns being added, columns being replaced")
        bus_stops[:, 5] = students_at_stop

    for i in range(len(students)):
        # This method only works as long as no stops have been dropped since the creation of the walking distance matrix
        closest_distance = np.min(walking_matrix['distances'][i])
        stop_index = np.argwhere(walking_matrix['distances'][i] == closest_distance)[0][0]
        stop_ID = bus_stops[stop_index, 0]
        new_stops.append(stop_ID)
        new_distances.append(closest_distance)
        bus_stops[stop_index, 5] = int(bus_stops[stop_index, 5]) + 1

    if new_columns_needed:
        if number_columns_students == 3:
            students = np.insert(students, 3, new_stops, axis=1)
        else:
            students[:, 3] = new_stops
        students = np.insert(students, 4, new_distances, axis=1)
    else:
        students[:, 3] = new_stops
        students[:, 4] = new_distances
    # Certain stops will have no students assigned

    bus_stops = bus_stops[bus_stops[:, 5] != 0]
    # This analytics bit might go somewhere else
    max_walking_distance = max(new_distances)
    average_walking_distance = np.average(new_distances)

    def condition(x):
        return x > 400

    count = sum(condition(x) for x in new_distances)
    print("Number of bus Stops = " + str(len(bus_stops)))
    print("Max student walking distance = " + str(max_walking_distance))
    print("Average walking distance = " + str(average_walking_distance))
    print("Number of students walking over 400m = " + str(count))

    """
    plt.hist(newDistances, bins=200)
    plt.show()
    """
    bus_stops = average_walking_distance_to_stop(bus_stops, students)
    return bus_stops, students


def average_walking_distance_to_stop(bus_stops, students):
    """Computes the average walking distance to each stop"""
    average_walking_distance = []
    for i in range(len(bus_stops)):
        stop_ID = bus_stops[i, 0]
        students_at_stop = students[students[:, 3] == stop_ID]
        avg = np.average(students_at_stop[:, 4])
        average_walking_distance.append(avg)

    bus_stops = np.insert(bus_stops, 6, average_walking_distance, axis=1)
    return bus_stops


def student_reassignment(bus_stops, students):
    """
    This method will take in stops and students, and reassign students to their closest bus stop
    It should be used several times, as the solution will be honed in on.
    Number of students at each stop will be stored, as will the students' stops
    """
    new_stops = []
    new_distances = []
    # If students have been through this process already, then there is no need to insert sometimes, and instead,
    # certain columns should be replaced
    number_columns_students = np.shape(students)[1]
    number_columns_bus_stops = np.shape(bus_stops)[1]
    # \\TODO: Make sure this still works
    new_columns_needed = False
    students_at_stop = [0] * len(bus_stops)
    if number_columns_students <= 4:
        # Need to add the new columns TO STUDENTS, maybe not to stops
        new_columns_needed = True
        print("Columns being added to students")
        if number_columns_bus_stops < 6:
            bus_stops = np.insert(bus_stops, 5, students_at_stop, axis=1)
        else:
            # need to set the students at stops to zero
            bus_stops[:, 5] = students_at_stop
    else:
        print("No columns being added, columns being replaced")
        bus_stops[:, 5] = students_at_stop

    # newStops[i] and newDistances[i] represent the new information for students[i]
    for i in range(0, len(students)):
        student_coords = students[i, [1, 2]]
        closest_stop_ID = -1
        closest_distance = -1
        for j in range(0, len(bus_stops)):
            current_stop_coords = bus_stops[j, [1, 2]]
            if bus_stops[j, 4] != 'none':
                current_distance = geopy.distance.distance(student_coords, current_stop_coords).m
                if closest_distance == -1:
                    closest_distance = current_distance
                    closest_stop_ID = bus_stops[j, 0]
                elif current_distance < closest_distance:
                    closest_distance = current_distance
                    closest_stop_ID = bus_stops[j, 0]
        new_stops.append(closest_stop_ID)
        new_distances.append(closest_distance)
        bus_stop_index = np.argwhere(bus_stops[:, 0] == closest_stop_ID)
        bus_stops[bus_stop_index, 5] = int(bus_stops[bus_stop_index, 5]) + 1

    if new_columns_needed:
        if number_columns_students == 3:
            students = np.insert(students, 3, new_stops, axis=1)
        else:
            students[:, 3] = new_stops
        students = np.insert(students, 4, new_distances, axis=1)
    else:
        students[:, 3] = new_stops
        students[:, 4] = new_distances
    # Certain stops will have no students assigned

    bus_stops = bus_stops[bus_stops[:, 5] != 0]
    # This analytics bit might go somewhere else
    max_walking_distance = max(new_distances)
    average_walking_distance = np.average(new_distances)

    def condition(x):
        return x > 400

    count = sum(condition(x) for x in new_distances)
    print("Number of bus Stops = " + str(len(bus_stops)))
    print("Max student walking distance = " + str(max_walking_distance))
    print("Average walking distance = " + str(average_walking_distance))
    print("Number of students walking over 400m = " + str(count))

    """
    plt.hist(newDistances, bins=200)
    plt.show()
    """
    return bus_stops, students


def stop_creation_loop(students):
    """
    This function maintains the bus stop creation loop. In this loop,
    1) Bus stops, created independent of the road network by the distance constrained clustering method, are snapped
        to the nearest suitable location using the Overpass API (which works on OpenStreetMap data)
    2) A walking matrix is created between each student and every existing stop
    3) This walking matrix is used to assign each student to their closest bus stop
    4) Any students that are still having to walk over 400 metres are sent back to the distance constrained clustering
        method

    This loop is continued until either: all students are walking below 400 metres to get to their nearest bus stop, or
    there is no change between iterations
    :param students:
    :return:
    """
    max_stop_id = 100
    previous_bus_stops = np.array([])
    initial_students = students
    number_of_students_over_constraint = -1
    convergence = False
    final_stops = []
    final_students = []
    while not convergence:
        new_stops = add_extra_stops(students, max_stop_id)
        new_stops = snap_stops_to_roads_iterative_search(new_stops)
        if previous_bus_stops.size != 0:
            # need to combine new bus stops with previous bus stops
            print("New bus stops being combined with old.")
            new_stops = np.concatenate((previous_bus_stops[:, 0:5], new_stops))

        walking_matrix = route.student_stop_walking_distances(students, new_stops)
        moved_stops_reassigned, students_reassigned = student_reassignment_walking_matrix(
            new_stops, initial_students, walking_matrix)
        overs = students_reassigned[students_reassigned[:, 4] >= 400]
        new_number_of_students_over_constraint = len(overs)
        if new_number_of_students_over_constraint == number_of_students_over_constraint or \
                new_number_of_students_over_constraint == 0:
            # convergence: solution is stable OR no students over walking constraint
            convergence = True
            final_stops = moved_stops_reassigned
            final_students = students_reassigned
        else:
            # solution might benefit from going again
            max_stop_id = np.max(moved_stops_reassigned[:, 0])
            previous_bus_stops = moved_stops_reassigned
            students = overs

    return final_stops, final_students
