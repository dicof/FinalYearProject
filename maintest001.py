"""
Tests the 101 files


"""
import numpy as np
import clustering101 as clustering
import routing101 as routing

path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = np.genfromtxt(path, delimiter=',', skip_header=1)
students = dataset[:, [1, 2, 3]]
# busStops, students = clustering.kmeans_constrained_cluster(students) # These bus Stops are independent of roads, snap to roads

path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\movedStops4.csv"
# These addresses are stored in 'dataset'
dataset2 = np.genfromtxt(path2, delimiter=',', skip_header=1)
movedStops = dataset2[:, [1, 2, 3]]
movedStops = movedStops[movedStops[:, 2] != -1]
distance_matrix = routing.graphhopper_matrix(movedStops)
bigtestnp = np.array(distance_matrix['distances'])
suitableStops = []
keptStops = [0] * len(movedStops)  # a -1 in this means the stop has been dropped
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

# Some stops are 0metres apart, they need to be combined before students are moved
# Also, anything that is pretty close needs to come together
# Within 75 metres (arbitrary), choose the stop that has the lower average distance to all other stops

# drop stops with -1 as moved Distance
movedStops = np.insert(movedStops, 3, keptStops, axis=1)

students2 = clustering.student_reassignment(movedStops, students)

# Drop anything with -1 in keptStops

movedStops = movedStops[movedStops[:, 3] != -1]

students3 = clustering.student_reassignment(movedStops, students2)
