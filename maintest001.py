"""
Tests the 101 files


"""
import numpy as np
import clustering101 as clustering
import routing101 as routing


def main():
    path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
    # These addresses are stored in 'dataset'
    dataset = np.genfromtxt(path, delimiter=',', skip_header=1)
    students = dataset[:, [1, 2, 3]]
    busStops, students = clustering.kmeans_constrained_cluster(students) # These bus Stops are independent of roads, snap to roads
