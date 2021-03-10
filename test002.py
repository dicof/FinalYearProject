# import the movedstops to make it quicker
# also import students
import numpy as np
import geopy.distance
import matplotlib.pyplot as plt

LIMIT = 1000

path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = np.genfromtxt(path, delimiter=',', skip_header=1)
if not len(dataset < LIMIT):
    pass
else:
    LIMIT = len(dataset) - 1
# These are the coordinates of the students' addresses
students = dataset[0:LIMIT, [1, 2, 3]]

# C:\Users\diarm\PycharmProjects\FinalYearProject

# moved stops
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\movedStops4.csv"
# These addresses are stored in 'dataset'
dataset2 = np.genfromtxt(path2, delimiter=',', skip_header=1)
movedStops = dataset2[:, [1, 2, 3]]

# drop stops with -1 as moved Distance
movedStops = movedStops[movedStops[:, 2] != -1]

# Assign every student to closest stop
# students and movedStops

newStops = []
newDistances = []
# newStops[i] and newDistances[i] represent the new information for students[i]
for i in range(0, len(students)):
    studentAddress = students[i, 1:3]  # Maybe?
    closestStopIndex = -1
    closestDistance = -1
    for j in range(0, len(movedStops)):
        currentStop = movedStops[j, [0,1]]
        if movedStops[j, 2] != -1:
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
averageWalkingDistance = total / len(newDistances)

# Histogram of distances to closest stop
plt.hist(newDistances, bins=100)
plt.show()

# count number of students walking above 400 metres and number of students at each stop
count = 0
numberStudentsAtStops = [0] * len(movedStops)
for i in range(0, len(newDistances)):
    if newDistances[i] > 400:
        count += 1

    newStop = newStops[i]
    numberStudentsAtStops[newStop] += 1




