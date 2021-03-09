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
movedStopsDF.to_csv("movedStops4.csv")


#Take any stops that have been successfully moved,
# and reassign the students to their closest stops
studentsDF = pd.DataFrame(students)
studentsDF.insert(3, "Stop", y_kmeans)



# Reassign students to closest stop
# Get distance from student to each stop
# save closest stop, and distance
# using students, fixedCoords
newStops = []
newDistances = []
#newStops[i] and newDistances[i] represent the new information for students[i]
for i in range(0,len(students)):
    studentAddress = students[i, 1:3] #Maybe?
    closestStopIndex = -1
    closestDistance = -1
    for j in range(0, len(fixedCoords)):
        currentStop = fixedCoords[j][0:2]
        if fixedCoords[j][2] != -1:
            currentDist = geopy.distance.distance(studentAddress, currentStop).m
            if closestDistance == -1:
                closestDistance = currentDist
                closestStopIndex = j
            elif currentDist < closestDistance:
                closestDistance = currentDist
                closestStopIndex = j

    newStops.append(closestStopIndex)
    newDistances.append(closestDistance)

maxWalkingDistance = max(newDistances)
total = 0
for i in range(0, len(newDistances)):
    total = total + newDistances[i]
averageWalkingDistance = total/len(newDistances)

# Drop any bus stop that has -1 in distance moved column
movedStopsDF = movedStopsDF[movedStopsDF[2] != -1]

# ready to send to routing
movedStopsCoords = movedStopsDF.values