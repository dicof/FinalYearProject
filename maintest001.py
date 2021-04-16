import numpy as np
import pandas as pd
import clustering101 as cluster
import routing101 as route
import time

path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = pd.read_csv(path)
dataset_np = np.array(dataset)
students = dataset_np[:, [1, 2, 3]]

#bus_stops, students, stats = cluster.stop_creation_loop(students)

print("lets go")
max_stop_id = 100
previous_bus_stops = np.array([])
initial_students = students
number_of_students_over_constraint = -1
convergence = False
final_stops = []
final_students = []
i = 0

# Get Rid Of This After Test
walking_matrix = []

statistics = []  # will contain [no.loop, no. stops, avg walking distance, no. overs, time taken seconds]
while not convergence:
    start = time.time()
    i = i + 1
    print("iteration " + str(i))
    new_stops = cluster.add_extra_stops(students, max_stop_id)
    print("Adding " + str(len(new_stops)) + " stops to solution.")
    new_stops = cluster.snap_stops_to_roads_iterative_search(new_stops)
    if previous_bus_stops.size != 0:
        # need to combine new bus stops with previous bus stops
        print("New bus stops being combined with old.")
        new_stops = np.concatenate((previous_bus_stops[:, 0:5], new_stops))

    walking_matrix = route.student_stop_walking_distances(students, new_stops)
    moved_stops_reassigned, students_reassigned = cluster.student_reassignment_walking_matrix(
        new_stops, initial_students, walking_matrix)
    overs = students_reassigned[students_reassigned[:, 4] >= 400]
    new_number_of_students_over_constraint = len(overs)
    if new_number_of_students_over_constraint == number_of_students_over_constraint or \
            new_number_of_students_over_constraint == 0:
        # convergence: solution is stable OR no students over walking constraint
        convergence = True
        # add final stops
        max_stop_id = np.max(moved_stops_reassigned[:, 0])
        final_round_stops = cluster.add_final_stops(overs, max_stop_id)
        print("Adding " + str(len(final_round_stops)) + " stops to solution.")
        print("New bus stops being combined with old.")
        new_stops = np.concatenate((moved_stops_reassigned[:, 0:5], final_round_stops))
        walking_matrix = route.student_stop_walking_distances(students, new_stops)
        moved_stops_reassigned, students_reassigned = cluster.student_reassignment_walking_matrix(
            new_stops, initial_students, walking_matrix)
        end = time.time()
        statistics.append(i)
        statistics.append(len(moved_stops_reassigned))
        statistics.append(np.average(students_reassigned[:, 4] >= 400))
        statistics.append(len(overs))
        statistics.append((end - start))
        final_stops = moved_stops_reassigned
        final_students = students_reassigned
    else:
        # solution might benefit from going again
        max_stop_id = np.max(moved_stops_reassigned[:, 0])
        previous_bus_stops = moved_stops_reassigned
        students = overs
        number_of_students_over_constraint = new_number_of_students_over_constraint
        end = time.time()
        statistics.append(i)
        statistics.append(len(moved_stops_reassigned))
        statistics.append(np.average(students_reassigned[:, 4] >= 400))
        statistics.append(len(overs))
        statistics.append((end - start))

