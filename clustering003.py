# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 13:44:09 2021

@author: Diarmuid
"""

#clustering 3 : Constraint based clustering
#Constraint based clustering: k means, then evaluate max length of each student to their respective bus stop
#Compare this to grade and max walking distance
#If walking distance > max permissable, add another cluster
#keep evaluating till constraint is satisfied

##Distance to grade constraints
#Grades: 10, 11, 12, 13
#Grade 10: 15/16 year olds
#Grade 11: 16/17 year olds
#Grade 12: 17/18 year olds
#Grade 13: 18/19 year olds
#Study bookmarked states 2 kilometers is suitable walking distance for 17/18 year olds,
#but thats for entire journey
STARTDIST10 = 1000
WALKINGINCREMENT = 250

#Gone with 400metres for grades 8 and above, and 250 metres for below
MAXDIST = 400
#These are arbitrary numbers for proof of concept

#Some APIs can only take certain max inputs, so limit goes here
#For graphhopper its 500
LIMIT = 1000


import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from kneed import KneeLocator
import geopy.distance


path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = np.genfromtxt(path, delimiter=',', skip_header=1)
if (len(dataset < LIMIT)):
    LIMIT = len(dataset) - 1
#These are the coordinates of the students' addresses
students = dataset[0:LIMIT, [1,2,3]]
coords = dataset[0:LIMIT,[2,3]]
noStudents = len(coords)
#Running multiple kmeans to find best number of clusters with lowest sse
kmeans_kwargs = {
    "init": "random",
    "n_init": 10,
    "max_iter": 300,
    "random_state": 17,
}
#storing the sses
sse = []
for k in range(1,30):
    kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
    kmeans.fit(coords)
    sse.append(kmeans.inertia_)
    
#This code graphs the SSE for investigation

"""
plt.style.use("fivethirtyeight")
plt.plot(range(1,30), sse)
plt.xticks(range(1, 30))
plt.xlabel("Number of Clusters")
plt.ylabel("SSE")
plt.show()
"""


kl = KneeLocator(range(1,30), sse, curve="convex", direction="decreasing")
noClusters = kl.elbow

#Investigate opt clusters to see if it agrees with max walking constraints

#Check each point to its cluster centre
#If its greater than the distance, add a cluster
#Keep going until satisfied


solutionFound = False
satisfied = True
while solutionFound == False:
    satisfied = True
    
    kmeans = KMeans(n_clusters=noClusters, **kmeans_kwargs)
    kmeans.fit(coords)
    y_kmeans = kmeans.predict(coords)
    centers = kmeans.cluster_centers_
    i = 0
    while satisfied == True:
        #Get cluster center for specific student
        clusterMean = centers[y_kmeans[i]]
        #Calculate distance between student and centre
        dst = geopy.distance.distance(coords[i], clusterMean).m
        #Using 400metres in this particular one
        if dst > MAXDIST:
            #Not permissable, add another cluster
            satisfied = False
            noClusters += 1
        else:
            i += 1
            if i == noStudents:
                #Solution satisfies constraints
                satisfied = False
                solutionFound = True



"""
plt.scatter(coords[:,1], coords[:,0], c=y_kmeans, s=10, cmap='viridis')
centers = kmeans.cluster_centers_
plt.scatter(centers[:,1], centers[:,0], c='grey', s=50, alpha = 0.5)
plt.scatter(-63.6994861, 44.7207799, c='blue', s=200, alpha = 0.25)
plt.suptitle('K Means')
plt.show()
"""
#Change centers into bus stops and add the number of students at each
unique, counts = np.unique(y_kmeans, return_counts=True)
descriptionStops = list(zip(unique, counts))
busStops = np.concatenate([centers, descriptionStops], axis=1)

#Clean this array up: drop redundant column at [,2]
busStops = np.delete(busStops, 2, axis=1)      
#Index = bus stop id
#column 1 = lats
#column 2 = longs
#column 3 = number students at stop

minStop = min(busStops[:,2])
maxStop = max(busStops[:,2])
"""
plt.scatter(busStops[:,1], busStops[:,0], c='red', s=30)
centers = kmeans.cluster_centers_
plt.scatter(centers[:,1], centers[:,0], c='blue', s=10)
plt.scatter(-63.6994861, 44.7207799, c='green', s=200, alpha = 0.25)
plt.show()
"""










