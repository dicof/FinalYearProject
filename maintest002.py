"""
This is to test the new busStopCheck.sidewalk_check method
"""

import busStopCheck as bsc
import numpy as np
import pandas as pd


path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\movedStops29MarchPostAmalg.csv"
# These addresses are stored in 'dataset'
dataset2 = np.genfromtxt(path2, delimiter=',', skip_header=1)
movedStops = dataset2[:, [1, 2, 3]]
coords = movedStops[:, [1, 2]]
head_coords = coords[15:45]
for i in range(len(head_coords)):
    print(head_coords[i])
    bsc.check_for_sidewalks(head_coords[i])

