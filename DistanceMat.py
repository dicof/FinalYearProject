# -*- coding: utf-8 -*-

"""

Created on Thu Nov 12 10:49:58 2020



@author: d

"""



from __future__ import print_function

from ortools.constraint_solver import routing_enums_pb2

from ortools.constraint_solver import pywrapcp

import numpy as np

import pandas as pd

from six.moves import xrange

from itertools                 import chain

import datetime          as dt

from scipy.spatial import distance as euc

import csv

import sys

import configparser

import requests

import json

import getopt

import time

import datetime

import urllib

from collections import Counter

import math

import json

import getopt

import folium

from scipy.cluster.hierarchy import dendrogram, linkage

from scipy.spatial.distance import squareform

from sklearn.cluster import AgglomerativeClustering, MeanShift, estimate_bandwidth

import matplotlib.pyplot as plt

df = pd.read_csv("C:\\Users\\Diarmuid\\Documents\\College\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv")

#Limit to 500 for API

Long = df['Long']

Lat  = df['Lat']

locationArray = list(zip(Long[0:500], Lat[0:500]))

URL = "https://graphhopper.com/api/1/matrix?key=4e2c94b1-14ff-4eb5-8122-cacf2e34043d&ch.disable=true"

payload = {"points":locationArray,
           "vehicle":"foot",
           "out_arrays":["times","distances"]}

start = time.time()

r = requests.post(URL, json = payload)

end = time.time()

print(end - start)

json_data = json.loads(r.text)

json_data

## Extract distance matrix and time matrix

#print(json_data)

distance_matrix = json_data['distances']

times_matrix    = json_data['times']

#Dendrogram
distance_matrix = np.array(distance_matrix)
#Can't square form because sometimes distance A to B /= B to A
for i in range(500):
    for j in range(i+1,500):
        distance_matrix[j,i] = distance_matrix[i,j]
        
testSquare = squareform(distance_matrix)

#Agglomerative Clustering
clustering = AgglomerativeClustering(4, affinity = 'precomputed',linkage = 'complete').fit(distance_matrix)
plt.style.use("ggplot")
plt.scatter(Long[0:500], Lat[0:500], c=clustering.labels_, s=10, cmap='viridis')
plt.suptitle('Agglomerative Clustering')
plt.show()

#Get center of each cluster


linked = linkage(testSquare, 'ward')
plt.style.use("ggplot")
dendrogram(linked,
            orientation='top',
            labels=range(500),
            distance_sort='descending',
            show_leaf_counts=True)
plt.title('Dendrogram')
plt.show()


#Attempting to visualise on map ///TODO 
#BBox = (Long[0:500].min(), Long[0:500].max(), Lat[0:500].min(), Lat[0:500].max())


#Mean Shift clustering

#Estimate bandwith
bandwidth = estimate_bandwidth(locationArray, quantile=0.2, n_samples=500)

meanshift = MeanShift(bandwidth=bandwidth)
meanshift.fit(locationArray)
meanshift_labels = meanshift.labels_
n_clusters_ = len(np.unique(meanshift_labels))

plt.style.use("ggplot")
plt.scatter(Long[0:500], Lat[0:500], c=meanshift.labels_, s=10, cmap='viridis')
plt.title('Meanshift Clustering')
plt.show()







