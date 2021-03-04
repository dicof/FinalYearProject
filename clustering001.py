
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 13:30:34 2020

@author: Diarmuid
"""
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from kneed import KneeLocator
import requests
import time


path = "C:\\Users\\Diarmuid\\Documents\\College\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = np.genfromtxt(path, delimiter=',', skip_header=1)

#These are the coordinates of the students' addresses
coords = dataset[0:500,[2,3]]
#Running multiple kmeans to find best number of clusters with lowest sse
kmeans_kwargs = {
    "init": "random",
    "n_init": 10,
    "max_iter": 300,
}
#storing the sses
sse = []
for k in range(1,30):
    kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
    kmeans.fit(coords)
    sse.append(kmeans.inertia_)

#This code graphs the SSE for investigation
plt.style.use("fivethirtyeight")
plt.plot(range(1,30), sse)
plt.xticks(range(1, 30))
plt.xlabel("Number of Clusters")
plt.ylabel("SSE")
plt.show()

kl = KneeLocator(range(1,30), sse, curve="convex", direction="decreasing")
optClusters = kl.elbow
#For now, elbow at 4 clusters so investigate that
kmeans = KMeans(n_clusters=optClusters, **kmeans_kwargs)
kmeans.fit(coords)
y_kmeans = kmeans.predict(coords)
plt.scatter(coords[:,1], coords[:,0], c=y_kmeans, s=10, cmap='viridis')
centers = kmeans.cluster_centers_
plt.scatter(centers[:,1], centers[:,0], c='black', s=200, alpha = 0.5)
plt.suptitle('K Means')
plt.show()
print(centers)


