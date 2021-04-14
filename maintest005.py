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
running_info = []
i = 0
while not convergence:
    i = i + 1
    print("iteration " + str(i))
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
        number_of_students_over_constraint = new_number_of_students_over_constraint
        running_info.append((len(moved_stops_reassigned), len(overs)))



# Stop amalgamation
distance_matrix = route.graphhopper_matrix(final_stops)
distance_matrix_np = np.array(distance_matrix['distances'])
walking_matrix_np = np.array(walking_matrix['distances'])

for i in range(len(final_stops)):
    stop_id = final_stops[i, 0]
    print(stop_id)
    students_at_stop = np.argwhere(final_students[:, 3] == stop_id)
    print("Current average distance at stop = " + str(average_distance_current_stop))
    print(str(len(students_at_stop)) + " students at stop")
    for j in range(len(students_at_stop)):
        # Find the students index in the walking matrix
        average_distance_current_stop = np.average(distance_matrix_np[i])
        print("student " + str(j))
        current_student_index = students_at_stop[j][0]
        # Find all the stops within the permissible walking distance
        suitable_stops_index_in_matrix = np.argwhere(walking_matrix_np[current_student_index] <= 400)
        print(str(len(suitable_stops_index_in_matrix)) + " suitable stops within 400 metres")
        # For each stop, evaluate whether its in a better location
        # id_minimum_distance = -1
        for k in range(len(suitable_stops_index_in_matrix)):
            suitable_stop = suitable_stops_index_in_matrix[k][0]
            average_distance_this_stop = np.average(distance_matrix_np[suitable_stop])
            print("Stop " + str(k) + ", " + str(average_distance_this_stop) + " average distance to other stops")
            if average_distance_this_stop < average_distance_current_stop:
                # this stop is suitable for migration for this student as its closer to every other stop
                average_distance_current_stop = average_distance_this_stop
                final_students[current_student_index, 3] = final_stops[suitable_stop, 0]
                final_students[current_student_index, 4] = walking_matrix_np[current_student_index, suitable_stop]
                print("Student " + str(final_students[current_student_index, 0]) + ", now set to "
                      + str(final_students[current_student_index, [3, 4]]))
        #print(suitable_stops)



