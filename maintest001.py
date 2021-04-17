import numpy as np
import pandas as pd
import clustering101 as cluster
import routing101 as route
import time
import busStopCheck as bsc

path = "C:\\Users\\diarm\\Documents\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\6670Students.csv"
# These addresses are stored in 'dataset'
dataset = pd.read_csv(path)
dataset_np = np.array(dataset)
students = dataset_np[:, [1, 2, 3]]

#bus_stops, students, stats = cluster.stop_creation_loop(students)

# Step One: stop creation loop
bus_stops, students, statistics = cluster.stop_creation_loop(students)

# Step Two: stop amalgamation

pre_walking_matrix = route.student_stop_walking_distances(students, bus_stops)
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")
pre_distance_matrix = route.graphhopper_matrix(bus_stops)
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")
amalg_stops, amalg_students = cluster.new_stop_amalgamation(students, bus_stops, pre_distance_matrix, pre_walking_matrix)

# Step Three: OR-Tools Routing
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")
pre_routing_matrix = route.graphhopper_matrix_depot(bus_stops)
pre_routes = route.ortools_routing(bus_stops, pre_routing_matrix)
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")
post_routing_matrix = route.graphhopper_matrix_depot(amalg_stops)
post_routes = route.ortools_routing(amalg_stops, post_routing_matrix)
print("Need to allow the graphhopper matrix time to recover before requesting again")
time.sleep(60)
print("Time over")
# Step Four: Add Arrival times to students

pre_students = route.calculate_student_travel_time(pre_routes, students, bus_stops, pre_walking_matrix)

post_walking_matrix = route.student_stop_walking_distances(amalg_students, amalg_stops)
amalg_students = route.calculate_student_travel_time(post_routes, amalg_students, amalg_stops, post_walking_matrix)

# Step Five: Save everthing to csvs
pre_final_response = route.turn_routes_into_csv_visualisation_form(pre_routes, bus_stops)
pre_final_response.to_csv("17_April_Final_Response_Pre_Amalg.csv", index=False)

post_final_response = route.turn_routes_into_csv_visualisation_form(post_routes, amalg_stops)
post_final_response.to_csv("17_April_Final_Response_Post_Amalg.csv", index=False)

col_names_stops = ["Stop ID",
                   "Lat", "Lon", "Distance Moved", "Road Type", "Students At Stop", "Average Walking Distance"]
col_names_students = ["Student Number", "Lat", "Lon", "Assigned Stop", "Walking Distance (m)", "Travel Time (s)"]

pre_amalg_stops_PD = pd.DataFrame(bus_stops)
pre_amalg_stops_PD.columns = col_names_stops
post_amalg_stops_PD = pd.DataFrame(amalg_stops)
post_amalg_stops_PD.columns = col_names_stops

pre_students_PD = pd.DataFrame(pre_students)
pre_students_PD.columns = col_names_students
post_students_PD = pd.DataFrame(amalg_students)
post_students_PD.columns = col_names_students

statistics_PD = pd.DataFrame(statistics)
statistics_PD.to_csv("17_April_statistics.csv")

pre_amalg_stops_PD.to_csv("17_April_pre_stops.csv", index=False)
post_amalg_stops_PD.to_csv("17_April_post_stops.csv", index=False)

pre_students_PD.to_csv("17_April_pre_students.csv", index=False)
post_students_PD.to_csv("17_April_post_students.csv", index=False)



# Lastly for fun: sidewalk check loop
pavements = []
for i in range(len(amalg_stops)):
    coords = amalg_stops[i, [1, 2]]
    pavement = bsc.sidewalk_check_stop(coords)
    pavements.append(pavement)

pavements = np.array(pavements)

# One Step left: Change the arrival times on responses to time format on the excel.

