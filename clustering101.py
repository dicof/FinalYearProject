# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 11:38:49 2021

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


def kmeans_constrained_cluster(students):
    # This method takes in the students addresses, and returns distance constrained clusters
    # That follow the distances provided by the school board for different grades' permissible
    # walking distances
    # In this particular example, grade 8 and above are allowed walk max 400 metres
    global centers
    MAXDIST = 400
    coords = students[:, [2, 3]]
    noStudents = len(students)

    kmeans_kwargs = {
        "init": "random",
        "n_init": 10,
        "max_iter": 300,
        "random_state": 17,  # Set to produce replicable pseudorandom data
    }

    # This section of code graphs the SSEs
    '''
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
    '''

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

    # Things that need to be returned: array of busStops, y_kmeans
    # append y_kmeans to students
    students = np.insert(students, 3, y_kmeans, axis=1)
    return busStops

def main():

