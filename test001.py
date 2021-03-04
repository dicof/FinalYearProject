import busStopCheck as bsc
import clustering003
import requests
import time
import pandas as pd
import numpy as np
import geopy.distance
busStops = clustering003.busStops
students = clustering003.students
y_kmeans = clustering003.y_kmeans


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
    fix = bsc.return_suitable_location2(testCoords)
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
movedStopsDF.to_csv("movedStops2.csv")


#Take any stops that have been successfully moved,
# and reassign the students to their closest stops
studentsDF = pd.DataFrame(students)
studentsDF.insert(3, "Stop", y_kmeans)

# Probably should create a matrix of distance from
# each student to each bus stop
# Graphhopper?
# For now, coordinates
# Across rows, busStops
# across column, students
#\\TODO: Clean this up to only use DFs or nps
studentsToStops = np.empty((len(studentsDF), len(movedStopsDF)), dtype=int)
# index in these lists = index in students
closestStopForStudent = []
studentCommute = []
for i in range(0, len(studentsDF)):
    # For each student, compute distance between student
    # and each stop
    minDist = -1
    closestStop = -1
    for j in range(0, len(movedStopsDF)):
        if fixedCoords[0][2] != -1:
            currentDist = geopy.distance.distance(students[i, 1:3], fixedCoords[j][0:2]).m
            studentsToStops[i, j] = int(currentDist)
            if minDist == -1:
                minDist = currentDist
                closestStop = j

            if currentDist < minDist:
                minDist = currentDist
                closestStop = j
        else:
            # Stop is not on road network
            studentsToStops[i,j] = -1

    closestStopForStudent.append(closestStop)
    studentCommute.append(minDist)