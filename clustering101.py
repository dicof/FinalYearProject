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


def add_extra_stops(students, max_stop_ID):
    """
    This method takes in any students that are still walking above 400 metres, and re-clusters them, with
    the aim of introducing new stops that will bring their walking distance below 400 metres.
    :param max_stop_ID:
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


def add_final_stops(students, max_stop_ID):
    """
    In this final method, any remaining students are assigned a stop directly on their co-ordinates which is
    snapped to the nearest road
    :param students:
    :param max_stop_ID:
    :return:
    """
    # Create dummy stops with just one student at them
    stop_IDs = range(int(max_stop_ID) + 1, (len(students) + int(max_stop_ID) + 1))
    bus_stops = np.insert(students[:, [1, 2]], 0, stop_IDs, axis=1)
    counts = [1] * len(students)
    bus_stops = np.insert(bus_stops, 3, counts, axis=1)

    # Send final stops to iterative search
    bus_stops = snap_stops_to_roads(bus_stops)
    return bus_stops


def snap_stops_to_roads(new_stops):
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


def stop_amalgamation(students, bus_stops, distance_matrix, walking_matrix):
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
    pre_avg_walking_distance = np.average(students[:, 4])
    for i in range(len(bus_stops)):
        # i represents the index of the bus stop in question, in the distance matrix and in the bus_stops table
        stop_id = bus_stops[i, 0]

        students_at_stop = np.argwhere(students[:, 3] == stop_id)
        number_students_at_stop = len(students_at_stop)
        student_moved_list = []
        for j in range(len(students_at_stop)):
            # j represents each student at the stop
            current_stop_average_distance = np.average(distance_matrix_np[i])
            current_student = students_at_stop[j][0]
            stops_within_400_metres = np.argwhere(walking_matrix_np[current_student] <= 400)
            student_moved = False
            for k in range(len(stops_within_400_metres)):
                # k represents the index of each stop that is within 400 metres of the student.
                potential_stop_index = stops_within_400_metres[k][0]
                potential_stop_average_distance = np.average(distance_matrix_np[potential_stop_index])
                if potential_stop_average_distance < current_stop_average_distance:
                    # Move the student to this stop.
                    student_moved = True
                    old_average_distance = current_stop_average_distance
                    current_stop_average_distance = potential_stop_average_distance
            student_moved_list.append(student_moved)
        # Check whether all the students can be migrated from the stop: otherwise it's not worth doing it
        if all(student_moved_list):
            # all students can be moved: proceed with the moving.
            # This isn't elegant but I can't think of another way to do this
            # other than going through again and reassigning
            for j in range(len(students_at_stop)):
                # j represents each student at the stop
                current_stop_average_distance = np.average(distance_matrix_np[i])
                current_student = students_at_stop[j][0]
                stops_within_400_metres = np.argwhere(walking_matrix_np[current_student] <= 400)
                for k in range(len(stops_within_400_metres)):
                    # k represents the index of each stop that is within 400 metres of the student.
                    potential_stop_index = stops_within_400_metres[k][0]
                    potential_stop_average_distance = np.average(distance_matrix_np[potential_stop_index])
                    if potential_stop_average_distance < current_stop_average_distance:
                        # Move the student to this stop.
                        old_average_distance = current_stop_average_distance
                        current_stop_average_distance = potential_stop_average_distance
                        print("Current stop: " + str(stop_id))
                        # print(str(len(students_at_stop)) + " students at stop")
                        print("student " + str(students[current_student, 0]) + " should be moved to "
                              + str(bus_stops[potential_stop_index, 0]))
                        print(str(potential_stop_average_distance) + " < " + str(old_average_distance))
                        print("They were walking " + str(walking_matrix_np[current_student, i]))
                        print("They would now be walking " + str(
                            walking_matrix_np[current_student, potential_stop_index]))
                        students[current_student, 3] = bus_stops[potential_stop_index, 0]
                        students[current_student, 4] = walking_matrix_np[current_student, potential_stop_index]
            print("Stop " + str(stop_id) + " is now going to be empty hopefully")
        # else:
        # its not worth moving all these students, as the bus still has to go there for one student.
        # print("Current stop: " + str(stop_id) + ", " + str(number_students_at_stop) + " students at stop.")
        # if sum(student_moved_list) > 0:
        # print("Not worth moving even though " + str(sum(student_moved_list)) + " students can be moved.")

    for i in range(len(bus_stops)):
        stop_id = bus_stops[i, 0]
        students_at_stop = len(np.argwhere(students[:, 3] == stop_id))
        bus_stops[i, 5] = students_at_stop

    bus_stops = bus_stops[bus_stops[:, 5] > 0]
    print("Average student walking distance before: " + str(pre_avg_walking_distance)
          + ". No. bus stops = " + str(np.shape(distance_matrix_np)[0]))
    print("Average student walking distance after: " + str(np.average(students[:, 4]))
          + ". No. bus stops = " + str(len(bus_stops)))
    bus_stops = average_walking_distance_to_stop(bus_stops, students)
    students = students[:, 0:5]
    # Drop columns that are wrong now
    return bus_stops, students


def student_reassignment(bus_stops, students, walking_matrix):
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

    no_columns = np.shape(bus_stops)[1]
    if no_columns == 7:
        bus_stops[:, 6] = average_walking_distance
    else:
        bus_stops = np.insert(bus_stops, 6, average_walking_distance, axis=1)
    return bus_stops


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
    i = 0

    statistics = []  # will contain [no.loop, no. stops, avg walking distance, no. overs, time taken seconds]
    while not convergence:
        start = time.time()
        stat = []
        i = i + 1
        print("iteration " + str(i))
        new_stops = add_extra_stops(students, max_stop_id)
        print("Adding " + str(len(new_stops)) + " stops to solution.")
        new_stops = snap_stops_to_roads(new_stops)
        if previous_bus_stops.size != 0:
            # need to combine new bus stops with previous bus stops
            print("New bus stops being combined with old.")
            new_stops = np.concatenate((previous_bus_stops[:, 0:5], new_stops))

        walking_matrix = route.student_stop_walking_distances(initial_students, new_stops)
        moved_stops_reassigned, students_reassigned = student_reassignment(
            new_stops, initial_students, walking_matrix)
        overs = students_reassigned[students_reassigned[:, 4] >= 400]
        new_number_of_students_over_constraint = len(overs)
        if new_number_of_students_over_constraint == number_of_students_over_constraint or \
                new_number_of_students_over_constraint == 0:
            # convergence: solution is stable OR no students over walking constraint
            convergence = True
            # add final stops
            if new_number_of_students_over_constraint != 0:
                # Need to do the final adding of overs.
                print("Adding final stops on iteration " + str(i))
                max_stop_id = np.max(moved_stops_reassigned[:, 0])
                final_round_stops = add_final_stops(overs, max_stop_id)
                print("Adding " + str(len(final_round_stops)) + " stops to solution.")
                print("New bus stops being combined with old.")
                new_stops = np.concatenate((moved_stops_reassigned[:, 0:5], final_round_stops))
                print("Need to allow the graphhopper matrix time to recover before requesting again")
                time.sleep(60)
                print("Time over")
                walking_matrix = route.student_stop_walking_distances(initial_students, new_stops)
                moved_stops_reassigned, students_reassigned = student_reassignment(
                    new_stops, initial_students, walking_matrix)

            end = time.time()
            stat.append(i)
            stat.append(len(moved_stops_reassigned))
            stat.append(np.average(students_reassigned[:, 4]))
            stat.append(len(students_reassigned[students_reassigned[:, 4] >= 400]))
            stat.append((end - start))
            statistics.append(stat)
            final_stops = moved_stops_reassigned
            final_students = students_reassigned
        else:
            # solution might benefit from going again
            max_stop_id = np.max(moved_stops_reassigned[:, 0])
            previous_bus_stops = moved_stops_reassigned
            students = overs
            number_of_students_over_constraint = new_number_of_students_over_constraint
            end = time.time()
            stat.append(i)
            stat.append(len(moved_stops_reassigned))
            stat.append(np.average(students_reassigned[:, 4]))
            stat.append(len(overs))
            stat.append((end - start))
            statistics.append(stat)

    statistics = np.array(statistics)
    return final_stops, final_students, statistics
