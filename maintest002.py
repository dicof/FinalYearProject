"""
This is to test the new busStopCheck.sidewalk_check method
"""

import busStopCheck as bsc
import numpy as np
import pandas as pd
import routing101 as routing
import clustering101 as clustering
import time

path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = pd.read_csv(path)
datasetnp = np.array(dataset)
students = datasetnp[:, [1, 2, 3]]
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\bus_stops_snapped_8th_April.csv"
# These addresses are stored in 'dataset'
dataset2 = pd.read_csv(path2)
dataset2np = np.array(dataset2)
moved_stops = dataset2np[:, 1:]

walking_matrix = routing.student_stop_walking_distances(students, moved_stops)
bus_stops_reassigned, students_reassigned = clustering.new_student_reassignment(
    moved_stops, students, walking_matrix)

overs = students_reassigned[students_reassigned[:, 4] >= 400]
maxID = np.max(bus_stops_reassigned[:, 0])
new_stops, over_students = clustering.add_extra_stops(overs, maxID)
fixed_stops = clustering.snap_new_stops_to_roads_new_around_system(new_stops)
full_stops = np.add((bus_stops_reassigned[:, 0:5], fixed_stops))
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")
walking_matrix = routing.student_stop_walking_distances(students, full_stops)
bus_stops_reassigned2, students_reassigned2 = clustering.new_student_reassignment(
    full_stops, students, walking_matrix)
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")
distance_matrix = routing.graphhopper_matrix_depot(bus_stops_reassigned2)
solution = routing.ortools_routing(bus_stops_reassigned2, distance_matrix)


col_names_stops = ["Stop ID",
                   "Lat", "Lon", "Distance Moved", "Road Type", "Students At Stop", "Average Walking Distance"]
col_names_students = ["Student Number", "Lat", "Lon", "Assigned Stop", "Walking Distance"]
