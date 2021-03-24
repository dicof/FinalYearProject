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
import routing101 as routing


def kmeans_constrained_cluster(students):
    """ Takes in students, returns busStops and students with y_kmeans appended """
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

    # Things that need to be returned: array of busStops, students
    # with y_kmeans appended
    students = np.insert(students, 3, y_kmeans, axis=1)
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
        testCoords = busStops[i, 0:2]
        fix = bsc.return_suitable_location2(testCoords)
        if fix == [0, 'none']:
            # No location found; send a 0 for distance moved
            testCoordsList = [testCoords[0], testCoords[1]]
            # Stop not moved, -1
            testCoordsList.append(-1)
            fixedCoords.append(testCoordsList)
        else:
            fixedCoords.append(fix)

        print(i)
    end = time.time()
    print(end - start + " seconds to complete stop relocation.")
    # busStops now has lat, lon, distance moved, type road moved to
    return fixedCoords


def stop_amalgamation(busStops, distance_matrix):
    """
    This function will take the distance matrix, and combine any stops together that are within 100 metres,
    choosing the one that's closest to every other stop by averaging the distance in the distance matrix
    :param busStops:
    :param distance_matrix:
    :return:
    """
    bigtestnp = np.array(distance_matrix['distances'])
    suitableStops = []
    keptStops = [0] * len(busStops)  # a -1 in this means the stop has been dropped
    movableDistance = 100
    for i in range(0, len(bigtestnp)):
        # row
        for j in range((i + 1), len(bigtestnp)):
            # column
            if bigtestnp[i, j] < movableDistance:
                # append the result
                suitableStops.append((i, j))
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

    busStops = np.insert(busStops, 3, keptStops, axis=1)
    busStops = busStops[busStops[:, 3] != -1]

    return busStops



def student_reassignment(busStops, students):
    """
    This method will take in stops and students, and reassign students to their closest bus stop
    It should be used several times, as the solution will be honed in on.
    """
    newStops = []
    newDistances = []
    # newStops[i] and newDistances[i] represent the new information for students[i]
    for i in range(0, len(students)):
        studentAddress = students[i, 1:3]  # Maybe?
        closestStopIndex = -1
        closestDistance = -1
        for j in range(0, len(busStops)):
            currentStop = busStops[j, [0, 1]]
            if busStops[j, 2] != -1:
                currentDist = geopy.distance.distance(studentAddress, currentStop).m
                if closestDistance == -1:
                    closestDistance = currentDist
                    closestStopIndex = j
                elif currentDist < closestDistance:
                    closestDistance = currentDist
                    closestStopIndex = j

        newStops.append(closestStopIndex)
        newDistances.append(closestDistance)
    students = np.insert(students, 3, newStops, axis=1)

    # This analytics bit might go somewhere else
    maxWalkingDistance = max(newDistances)
    total = 0
    count = 0
    for i in range(0, len(newDistances)):
        total = total + newDistances[i]
        if newDistances[i] > 400:
            count += 1
    averageWalkingDistance = total / len(newDistances)
    print("Number of bus Stops = " + str(len(busStops)))
    print("Max student walking distance = " + str(maxWalkingDistance))
    print("Average walking distance = " + str(averageWalkingDistance))
    print("Number of students walking over 400m = " + str(count))
    return students



def distance_matrix_stop_amalgamation(busStops, students, distance_matrix):
    # This method will amalgamate any stops that are close enough that the change in walking distance
    # is minimal.
    # The distance matrix between stops will be used to detect cul-de-sacs as best as possible

    # Ignore first entry in distance matrix, as this is bus stop
    print("Unfinished")

