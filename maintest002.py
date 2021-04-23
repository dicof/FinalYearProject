"""
This is to test the new busStopCheck.sidewalk_check method
"""

import busStopCheck as bsc
import numpy as np
import pandas as pd
import routing101 as routing
import clustering101 as clustering
import time


np.set_printoptions(suppress=True)

path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
students = pd.read_csv(path)
students = np.array(students)
students = students[:, 1:4]
