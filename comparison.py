import pandas as pd
import numpy as np

import clustering101 as cluster
import routing101 as route

np.set_printoptions(suppress=True, linewidth=10000)

path = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\stops_13_April.csv"
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\students_13_April.csv"
bus_stops = pd.read_csv(path)
bus_stops = np.array(bus_stops)
pre_bus_stops = bus_stops[:, 0:]
students = pd.read_csv(path2)
students = np.array(students)
pre_students = students[:, 0:]

path = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\amalgamated_stops_15_April.csv"
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\amalgamated_students_15_April.csv"

bus_stops = pd.read_csv(path)
bus_stops = np.array(bus_stops)
post_bus_stops = bus_stops[:, 0:]
students = pd.read_csv(path2)
students = np.array(students)
post_students = students[:, 0:]

overs = post_students[post_students[:, 4] > 400]
max_ID = np.max(post_bus_stops[:, 0])

walking_matrix = route.student_stop_walking_distances(students, bus_stops)
test_stops, test_students = cluster.student_reassignment(pre_bus_stops, students, walking_matrix)


