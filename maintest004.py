import pandas as pd
import numpy as np

np.set_printoptions(suppress=True)
path1 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\19_April_post_students.csv"
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\19_April_post_stops.csv"

bus_stops = pd.read_csv(path2)
bus_stops = np.array(bus_stops)
bus_stops = bus_stops[:, 0:]

students = pd.read_csv(path1)
students = np.array(students)
students = students[:, 0:]