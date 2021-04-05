"""
Tests the 101 files


"""
import numpy as np
import pandas as pd
import clustering101 as clustering
import routing101 as routing

path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = np.genfromtxt(path, delimiter=',', skip_header=1)
students = dataset[:, [1, 2, 3]]
"""
To save time, stops will be read in
"""
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\movedStops29MarchPostAmalg.csv"
# These addresses are stored in 'dataset'
dataset3 = pd.read_csv(path2)
datasetnp = dataset3.to_numpy()
movedStops = datasetnp[:, 1:]

busStops, students = clustering.student_reassignment(movedStops, students)
distance_matrix = routing.graphhopper_matrix(busStops)

solution = routing.ortools_routing(busStops, distance_matrix)

walking_matrix = routing.student_stop_walking_distances(students, busStops)
busStops, students = clustering.new_student_reassignment(busStops, students, walking_matrix)




"""
busStops, students = clustering.kmeans_constrained_cluster(students) # These bus Stops are independent of roads,
# snap to roads
busStops2 = clustering.snap_stops_to_roads(busStops) # this method takes a long time, write to csv after

# Assign students to stops
busStops3, students2 = clustering.student_reassignment(busStops2, students)

#Amalgamate stops
distance_matrix = routing.graphhopper_matrix(busStops3)
busStops4 = clustering.stop_amalgamation(busStops3, distance_matrix)
# reassign students
busStops5, students3 = clustering.student_reassignment(busStops4, students2)
"""







# For test, read in roads stored to save time
"""
movedStopsDF = pd.DataFrame(busStops)
movedStopsDF.to_csv("movedStops26MarchPreAmalg.csv")

busStops, students = clustering.student_reassignment(busStops, students) # this is done 
# before stop amalgamation just to have statistics
distance_matrix = routing.graphhopper_matrix(busStops)
busStops = clustering.stop_amalgamation(busStops, distance_matrix)
busStops, students = clustering.student_reassignment(busStops, students)

movedStopsDF = pd.DataFrame(busStops)
movedStopsDF.to_csv("movedStops26MarchPostAmalg.csv") # This is post amalgamation, written to csv. Write students too

studentsDF = pd.DataFrame(students)
studentsDF.to_csv("students26March.csv")
"""




"""
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\movedStops4.csv"
# These addresses are stored in 'dataset'
dataset2 = np.genfromtxt(path2, delimiter=',', skip_header=1)
movedStops = dataset2[:, [1, 2, 3]]
movedStops = movedStops[movedStops[:, 2] != -1]
distance_matrix = routing.graphhopper_matrix(movedStops)
# try using the method
movedStops = clustering.stop_amalgamation(movedStops, distance_matrix)

movedStops, students = clustering.student_reassignment(movedStops, students)
"""