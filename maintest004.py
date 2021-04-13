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
test_students = students
test_stops, test_students_2 = cluster.stop_creation_loop(test_students)
