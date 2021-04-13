# Test new flow plan
import pandas as pd
import numpy as np
import clustering101 as cluster
import routing101 as route

np.set_printoptions(suppress=True)

path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
students = pd.read_csv(path)
students = np.array(students)
students = students[:, 1:4]

bus_stops, students = cluster.distance_constrained_cluster(students)
moved_stops = cluster.snap_new_stops_to_roads_new_around_system(bus_stops)
# This is gonna take quite some time
walking_matrix = route.student_stop_walking_distances(students, moved_stops)
moved_stops_2, students_2 = cluster.new_student_reassignment(moved_stops, students, walking_matrix)
# Attempt to send the overs to the clustering algorithm again for new stops and see what that does for the answer
overs = students_2[students_2[:, 4] >= 400]
max_id = np.max(moved_stops_2[:, 0])
new_stops, overs = cluster.add_extra_stops(overs, max_id)
new_stops = cluster.snap_new_stops_to_roads_new_around_system(new_stops)
all_stops = np.concatenate((moved_stops_2[:, 0:5], new_stops))
walking_matrix = route.student_stop_walking_distances(students, all_stops)
