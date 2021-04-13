"""
Tests the 101 files


"""
import numpy as np
import pandas as pd
import clustering101 as clustering
import routing101 as routing
import time
"""
path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = np.genfromtxt(path, delimiter=',', skip_header=1)
students = dataset[:, [1, 2, 3]]

bus_stops, students = clustering.distance_constrained_cluster(students)
bus_stops_snapped = clustering.snap_stops_to_roads(bus_stops)
distance_matrix = routing.graphhopper_matrix(bus_stops_snapped)
# bus_stops_amalgamated = clustering.stop_amalgamation(bus_stops_snapped, distance_matrix)
walking_matrix = routing.student_stop_walking_distances(students, bus_stops_snapped)
bus_stops_reassigned, students_reassigned = clustering.new_student_reassignment(
    bus_stops_snapped, students, walking_matrix)

# Weird test idea
#depotMatrix = routing.graphhopper_matrix_depot(bus_stops_reassigned, [44.72048, -63.69856])
solution = routing.ortools_routing(bus_stops_reassigned)
"""
path = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\stops8April.csv"
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\students8April.csv"
stops = pd.read_csv(path)
students = pd.read_csv(path2)
bus_stops = np.array(stops)
students = np.array(students)

distance_matrix = routing.graphhopper_matrix_depot(bus_stops)
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")
walking_matrix = routing.student_stop_walking_distances(students, bus_stops)
routes = routing.ortools_routing(bus_stops, distance_matrix)
students2 = routing.calculate_student_travel_time(routes, students, walking_matrix)
studentsDF = pd.DataFrame(students)
col_names_students = ["Student Number", "Lat", "Lon", "Assigned Stop", "Walking Distance (m)", "Travel Time (s)"]
studentsDF.columns = col_names_students
response = routing.turn_routes_into_csv_visualisation_form(routes, students, bus_stops)
response.columns = [
    'vehicle_id', 'sequence', 'latitude', 'longitude',
    'vehicle_cumul_dist', 'cumul_demands', 'arrival_time',
    'dist_to_school', 'stop_number', 'node']
response.to_csv('response_first_test.csv', index=False)











"""
To save time, stops will be read in

path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\movedStops29MarchPostAmalg.csv"
dataset3 = pd.read_csv(path2)
datasetnp = dataset3.to_numpy()
movedStops = datasetnp[:, 1:]

# These addresses are stored in 'dataset'


busStops, students = clustering.student_reassignment(movedStops, students)
distance_matrix = routing.graphhopper_matrix(busStops)

solution = routing.ortools_routing(busStops, distance_matrix)

walking_matrix = routing.student_stop_walking_distances(students, busStops)
busStops, students = clustering.new_student_reassignment(busStops, students, walking_matrix)

"""


"""
busStops, students = clustering.kmeans_constrained_cluster(students) # These bus Stops are independent of roads,
# snap to roads
busStops2 = clustering.snap_stops_to_roads(busStops) # this method takes a long time, write to csv after

# Assign students to stops
busStops3, students2 = clustering.student_reassignment(busStops2, students)

#Amalgamate stops
distance_matrix = routing.graphhopper_matrix(busStops3)
busStops4 = clustering.stop_amalgamation(busStops3, distance_matrix)
# reassign students
busStops5, students3 = clustering.student_reassignment(busStops4, students2)
"""







# For test, read in roads stored to save time
"""
movedStopsDF = pd.DataFrame(busStops)
movedStopsDF.to_csv("movedStops26MarchPreAmalg.csv")

busStops, students = clustering.student_reassignment(busStops, students) # this is done 
# before stop amalgamation just to have statistics
distance_matrix = routing.graphhopper_matrix(busStops)
busStops = clustering.stop_amalgamation(busStops, distance_matrix)
busStops, students = clustering.student_reassignment(busStops, students)

movedStopsDF = pd.DataFrame(busStops)
movedStopsDF.to_csv("movedStops26MarchPostAmalg.csv") # This is post amalgamation, written to csv. Write students too

studentsDF = pd.DataFrame(students)
studentsDF.to_csv("students26March.csv")
"""




"""
path2 = "C:\\Users\\diarm\\PycharmProjects\\FinalYearProject\\movedStops4.csv"
# These addresses are stored in 'dataset'
dataset2 = np.genfromtxt(path2, delimiter=',', skip_header=1)
movedStops = dataset2[:, [1, 2, 3]]
movedStops = movedStops[movedStops[:, 2] != -1]
distance_matrix = routing.graphhopper_matrix(movedStops)
# try using the method
movedStops = clustering.stop_amalgamation(movedStops, distance_matrix)

movedStops, students = clustering.student_reassignment(movedStops, students)
"""