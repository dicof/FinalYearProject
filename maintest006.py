import pandas as pd
import numpy as np
import routing101 as route
import clustering101 as cluster
import time

np.set_printoptions(suppress=True)

path = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\stops_13_April.csv"
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\students_13_April.csv"

bus_stops = pd.read_csv(path)
bus_stops = np.array(bus_stops)
bus_stops = bus_stops[:, 0:]
students = pd.read_csv(path2)
students = np.array(students)
students = students[:, 0:]

walking_matrix = route.student_stop_walking_distances(students, bus_stops)
walking_matrix_np = np.array(walking_matrix['distances'])
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")

distance_matrix = route.graphhopper_matrix(bus_stops)
distance_matrix_np = np.array(distance_matrix['distances'])


for i in range(len(bus_stops)):
    # i represents the index of the bus stop in question, in the distance matrix and in the bus_stops table
    stop_id = bus_stops[i, 0]
    print("Current stop: " + str(stop_id))
    students_at_stop = np.argwhere(students[:, 3] == stop_id)
    number_students_at_stop = len(students_at_stop)
    print(str(len(students_at_stop)) + " students at stop")
    for j in range(len(students_at_stop)):
        # j represents each student at the stop
        current_stop_average_distance = np.average(distance_matrix_np[i])
        current_student = students_at_stop[j][0]
        stops_within_400_metres = np.argwhere(walking_matrix_np[current_student] <= 400)
        for k in range(len(stops_within_400_metres)):
            # k represents the index of each stop that is within 400 metres of the student.
            potential_stop_index = stops_within_400_metres[k][0]
            potential_stop_average_distance = np.average(distance_matrix_np[potential_stop_index])
            if potential_stop_average_distance < current_stop_average_distance:
                # Move the student to this stop.
                old_average_distance = current_stop_average_distance
                current_stop_average_distance = potential_stop_average_distance
                print("student " + str(students[current_student, 0]) + " should be moved to "
                      + str(bus_stops[potential_stop_index, 0]))
                print(str(potential_stop_average_distance) + " < " + str(old_average_distance))
                print("They were walking " + str(walking_matrix_np[current_student, i]))
                print("They would now be walking " + str(walking_matrix_np[current_student, potential_stop_index]))
                number_students_at_stop = number_students_at_stop - 1
                if number_students_at_stop == 0:
                    print("This would leave stop " + str(bus_stops[i, 0]) + " empty")



