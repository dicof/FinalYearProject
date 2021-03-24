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
# try using the method
movedStops = clustering.stop_amalgamation(movedStops, distance_matrix)

movedStops, students = clustering.student_reassignment(movedStops, students)
