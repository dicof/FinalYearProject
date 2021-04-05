"""
This file will contain the code to create the different states that will be evaluated

States:
1. Prioritise Primary > Secondary > Tertiary > Residential
2. Residential Only
3. Tertiary Only
4. Secondary Only
5. Primary Only (Don't think this will work)
6. Strict sidewalk check (Don't think this will work either)
7. Technique 1 but with hard 400m constraint



"""



import numpy as np
import pandas as pd
import clustering101 as clustering
import routing101 as routing


path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = np.genfromtxt(path, delimiter=',', skip_header=1)
students = dataset[:, [1, 2, 3]]
busStops, students = clustering.kmeans_constrained_cluster(students) # These bus Stops are independent of roads

"""State 1"""
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\movedStops29MarchPostAmalg.csv"
# These addresses are stored in 'dataset'
dataset3 = pd.read_csv(path2)
datasetnp = dataset3.to_numpy()
movedStops = datasetnp[:, 1:]

busStops, students = clustering.student_reassignment(movedStops, students)






