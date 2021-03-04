# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 12:46:04 2021

@author: Diarmuid
"""
import pandas as pd
import numpy as np
import time

import clustering003
import busStopCheck

# clustering005: Attempting to integrate busStopChecks into the loop
busStops = clustering003.busStops
students = clustering003.students
y_kmeans = clustering003.y_kmeans
# write bus stops to excel file
busStopsDF = pd.DataFrame(busStops)
busStopsDF.to_csv("test2.csv")

'''Add a column to students with the index of the bus stop theyve been assigned to'''
studentsDF = pd.DataFrame(students)
studentsDF[3] = y_kmeans
studentsDF.rename(columns={0: "studentNumber", 1: "lat", 2: "long", 3: "busStop"})

'''This may take a while'''
# So each bus stop coordinates will be passed in, moved to a suitable situation
# Test with stops in similar area
start = time.time()
#testIndicesList = [9, 131, 220, 47, 68, 61, 63]
fixedCoords = []

# If there's no suitable location, bus stop won't be moved
# And moved distance will be set to 0
# Or should I do -1 just in case something happens to be
# exactly on a suitable road?
# -1 for now

for i in range(0, len(busStops)):
    testCoords = busStops[i, 0:2]
    fix = busStopCheck.return_suitable_location(testCoords)
    if fix == [0]:
        # No location found; send a 0 for distance moved
        testCoordsList = [testCoords[0], testCoords[1]]
        # Stop not moved, -1
        testCoordsList.append(-1)
        fixedCoords.append(testCoordsList)
    else:
        fixedCoords.append(fix)

    print(i)
end = time.time()
print(end - start)
movedStopsDF = pd.DataFrame(fixedCoords)
movedStopsDF.to_csv("movedStops1.csv")
