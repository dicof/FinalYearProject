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
    # This method will amalgamate any stops that are close enough that the change in walking distance
    # is minimal.
    # The distance matrix between stops will be used to detect cul-de-sacs as best as possible

    # Ignore first entry in distance matrix, as this is bus stop



    print("Unfinished")
