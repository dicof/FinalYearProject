import pandas as pd
import numpy as np
import clustering101 as cluster
import routing101 as route


path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
students = pd.read_csv(path)
students = np.array(students)
students = students[:, 1:4]


max_stop_id = 100
previous_bus_stops = np.array([])
initial_students = students
number_of_students_over_constraint = -1
convergence = False
final_stops = []
final_students = []
walking_matrix = []
temp_stops = []
temp_students = []
while not convergence:
    new_stops = cluster.add_extra_stops(students, max_stop_id)
    new_stops = cluster.snap_stops_to_roads_iterative_search(new_stops)
    if previous_bus_stops.size != 0:
        # need to combine new bus stops with previous bus stops
        print("New bus stops being combined with old.")
        new_stops = np.concatenate((previous_bus_stops[:, 0:5], new_stops))

    walking_matrix = route.student_stop_walking_distances(initial_students, new_stops)
    moved_stops_reassigned, students_reassigned = cluster.student_reassignment_walking_matrix(
        new_stops, initial_students, walking_matrix)
    overs = students_reassigned[students_reassigned[:, 4] >= 400]
    new_number_of_students_over_constraint = len(overs)
    if new_number_of_students_over_constraint == number_of_students_over_constraint or \
            new_number_of_students_over_constraint == 0:
        # convergence: solution is stable OR no students over walking constraint
        convergence = True
        final_stops = moved_stops_reassigned
        final_students = students_reassigned
    else:
        # solution might benefit from going again
        max_stop_id = np.max(moved_stops_reassigned[:, 0])
        previous_bus_stops = moved_stops_reassigned
        students = overs



