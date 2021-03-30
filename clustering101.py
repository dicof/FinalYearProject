# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 12:40:56 2021

@author: Diarmuid
"""

"""
The aim of this file is to reform the clustering methods into a single file,
with the clustering methods written as functions.
"""

from sklearn.cluster import KMeans
from kneed import KneeLocator
import geopy.distance
import numpy as np
import busStopCheck as bsc
import time
import matplotlib.pyplot as plt
import routing101 as routing


def kmeans_constrained_cluster(students):
    """ Takes in students, returns busStops and students with y_kmeans appended """
    # \\TODO: Add a unique stop id column
    # This method takes in the students addresses, and returns distance constrained clusters
    # That follow the distances provided by the school board for different grades' permissible
    # walking distances
    # In this particular example, grade 8 and above are allowed walk max 400 metres
    MAXDIST = 400
    coords = students[:, [1, 2]]
    noStudents = len(students)

    kmeans_kwargs = {
        "init": "random",
        "n_init": 10,
        "max_iter": 300,
        "random_state": 17,  # Set to produce replicable pseudorandom data
    }
    # storing the sses
    sse = []
    for k in range(1, 30):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(coords)
        sse.append(kmeans.inertia_)

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
    noClusters = kl.elbow

    # Investigate opt clusters to see if it agrees with max walking constraints

    # Check each point to its cluster centre
    # If its greater than the distance, add a cluster
    # Keep going until satisfied

    solutionFound = False
    satisfied = True  # \\TODO: why is this unused?
    while not solutionFound:
        satisfied = True

        kmeans = KMeans(n_clusters=noClusters, **kmeans_kwargs)
        kmeans.fit(coords)
        y_kmeans = kmeans.predict(coords)
        centers = kmeans.cluster_centers_
        i = 0
        while satisfied:
            # Get cluster center for specific student
            clusterMean = centers[y_kmeans[i]]
            # Calculate distance between student and centre
            dst = geopy.distance.distance(coords[i], clusterMean).m
            # Using 400metres in this particular one
            if dst > MAXDIST:
                # Not permissible, add another cluster
                satisfied = False
                noClusters += 1
            else:
                i += 1
                if i == noStudents:
                    # Solution satisfies constraints
                    satisfied = False
                    solutionFound = True

    # Change centers into bus stops and add the number of students at each
    unique, counts = np.unique(y_kmeans, return_counts=True)
    busStops = np.insert(centers, 2, counts, axis=1)
    # Adding unique stop id so stops can be referred to without their row index, which allows safer dropping of
    # stops
    # \\TODO: Run this by Simon. For now, stops start at 101
    stopIDs = range(101, (len(busStops) + 101))
    busStops = np.insert(busStops, 0, stopIDs, axis=1)
    # Things that need to be returned: array of busStops, students
    # with y_kmeans appended
    # Now stop IDs have been added, students should use that
    students = np.insert(students, 3, (y_kmeans + 101), axis=1)
    return busStops, students


def main():
    path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
    # These addresses are stored in 'dataset'
    dataset = np.genfromtxt(path, delimiter=',', skip_header=1)
    students = dataset[:, [1, 2, 3]]
    busStops, students = kmeans_constrained_cluster(students)
    print(busStops)


def snap_stops_to_roads(busStops):
    # Takes in bus stops that have been formed by latitude/longitude clustering
    # and returns stops that have been snapped to suitable roads using busStopCheck.return_suitable_location2
    # WARNING: method takes about 10 minutes for 227 stops

    start = time.time()
    fixedCoords = []
    for i in range(0, len(busStops)):
        testCoords = busStops[i, [1, 2]]
        fix = bsc.return_suitable_location2(testCoords)
        fixedCoords.append(fix)

        print(i)
    end = time.time()
    print(str(end - start) + " seconds to complete stop relocation.")
    newStops = np.array(fixedCoords)
    newStops = np.insert(newStops, 0, busStops[:, 0], axis=1)
    # busStops now has lat, lon, distance moved, type road moved to
    # Drop any stops with none as road #\\TODO: Check this
    newStops = newStops[newStops[:, 4] != 'none']
    return newStops


def stop_amalgamation(busStops, distance_matrix):
    """
    This function will take the distance matrix, and combine any stops together that are within 100 metres,
    choosing the one that's closest to every other stop by averaging the distance in the distance matrix
    :param busStops:
    :param distance_matrix:
    :return:
    """
    bigtestnp = np.array(distance_matrix['distances'])
    #suitableStops = []
    keptStops = [0] * len(busStops)  # a -1 in this means the stop has been dropped
    movableDistance = 100
    for i in range(0, len(bigtestnp)):
        # row
        for j in range((i + 1), len(bigtestnp)):
            # column
            if bigtestnp[i, j] < movableDistance:
                # append the result
                #suitableStops.append((i, j))
                print("Stop " + str(i) + " and " + str(j) + " are " + str(bigtestnp[i, j]) + "m apart")
                # average the distances between each stop and every other stop in the distance matrix
                avgLengthi = np.average(bigtestnp[i])
                avgLengthj = np.average(bigtestnp[j])
                if avgLengthj < avgLengthi:
                    # choose i
                    keptStops[i] = -1
                    print("Stop " + str(j) + " has been kept")
                else:
                    # either i is smaller or they're equal, keep i
                    keptStops[j] = -1
                    print("Stop " + str(i) + " has been kept")
    # busStops = np.insert(busStops, 2, range(0, len(busStops)), axis=1) # This is the ID of the bus stop
    busStops = np.insert(busStops, 6, keptStops, axis=1)
    busStops = busStops[busStops[:, 6] != '-1']
    busStops = busStops[:, 0:6]
    return busStops


def student_reassignment(busStops, students):
    """
    This method will take in stops and students, and reassign students to their closest bus stop
    It should be used several times, as the solution will be honed in on.
    Number of students at each stop will be stored, as will the students' stops
    """
    newStops = []
    newDistances = []
    # If students have been through this process already, then there is no need to insert sometimes, and instead,
    # certain columns should be replaced
    noCols = np.shape(students)[1]
    #\\TODO: Make sure this still works
    newColumnsNeeded = False
    studentsAtStop = [0] * len(busStops)
    if noCols <= 4:
        # Need to add the new columns
        newColumnsNeeded = True
        print("Columns being added")
        busStops = np.insert(busStops, 5, studentsAtStop, axis=1)
    else:
        print("No columns being added, columns being replaced")
        busStops[:, 5] = studentsAtStop


    # newStops[i] and newDistances[i] represent the new information for students[i]
    for i in range(0, len(students)):
        studentAddress = students[i, [1, 2]]  # Maybe?
        closestStopID = -1
        closestDistance = -1
        for j in range(0, len(busStops)):
            currentStop = busStops[j, [1, 2]]
            if busStops[j, 4] != 'none':
                currentDist = geopy.distance.distance(studentAddress, currentStop).m
                if closestDistance == -1:
                    closestDistance = currentDist
                    closestStopID = busStops[j, 0]
                elif currentDist < closestDistance:
                    closestDistance = currentDist
                    closestStopID = busStops[j, 0]
        newStops.append(closestStopID)
        newDistances.append(closestDistance)
        busStopIndex = np.argwhere(busStops[:, 0] == closestStopID)
        busStops[busStopIndex, 5] = int(busStops[busStopIndex, 5]) + 1

    if newColumnsNeeded:
        students[:, 3] = newStops
        students = np.insert(students, 4, newDistances, axis=1)
    else:
        students[:, 3] = newStops
        students[:, 4] = newDistances
    # Certain stops will have no students assigned

    busStops = busStops[busStops[:, 5] != '0']
    # This analytics bit might go somewhere else
    maxWalkingDistance = max(newDistances)
    averageWalkingDistance = np.average(newDistances)

    def condition(x):
        return x > 400

    count = sum(condition(x) for x in newDistances)
    print("Number of bus Stops = " + str(len(busStops)))
    print("Max student walking distance = " + str(maxWalkingDistance))
    print("Average walking distance = " + str(averageWalkingDistance))
    print("Number of students walking over 400m = " + str(count))

    """
    plt.hist(newDistances, bins=200)
    plt.show()
    """
    return busStops, students
