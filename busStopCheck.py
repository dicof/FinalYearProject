# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 01:24:50 2021

@author: Diarmuid
"""

# sidewalkCheck : takes bus stop coordinates,
# and checks if each location has a sidewalk and is on a suitable road

# Sidewalk check - done, still need to decide if left and right are suitable
# suitable road - what classifications are suitable for stop


import overpy  # to import the overpy module
import pandas as pd  # to import pandas library
import numpy as np
import json  # to import json
import requests  # to import requests
import time
import geopy.distance
from scipy.spatial import KDTree

# Distance from coordinate to road allowed
DISTANCEALLOWED = 50


def roadtypes_on_route(route):
    for i in range(len(route)):
        query = get_roads_query(route[i])
        print(route[i])
        overpass_url = "http://overpass-api.de/api/interpreter"
        response = requests.get(overpass_url, params={'data': query})
        json_data = response.json()
        if 'elements' in json_data:
            for j in range(len(json_data['elements'])):
                print('stop ' + str(i) + ', way ' + str(j) + ': ' + json_data['elements'][j]['tags']['highway'])
        else:
            print('no elements')
        check_for_sidewalks(route[i])


#   TODO sort this out

def check_for_sidewalks(coords):
    # Checks coordinates for two types of sidewalk
    # 1: affiliated to the road node
    # 2: an entirely separate 'way' that is designated as a path
    query = get_roads_query(coords)
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url, params={'data': query})
    # print(response.text)
    json_data = response.json()
    # print(json_data)
    ways = len(json_data['elements'])  # number of ways to evaluate
    # print(ways)
    for i in range(ways):
        # check which kind of way
        '''
        Types of way:
        secondary,
        path,
        residential,
        service (commonly driveways),
        tertiary (sometimes doesn't have sidewalk tag even when sidewalk present'),
        footway (seems to just be routes through a park so far),
        '''
        if 'elements' in json_data:
            wayType = json_data['elements'][i]['tags']['highway']
            print(json_data['elements'][i]['tags'])
            if wayType == 'secondary':
                # secondary style road - check for sidewalk (If thats a thing, might not be)
                if 'sidewalk' in json_data['elements'][i]['tags']:
                    # Sidewalk on secondary road - perhaps check for left/right
                    '''Check for left right here if needed'''
                    print('sidewalk on secondary, type: ' + json_data['elements'][i]['tags']['sidewalk'])

            elif wayType == 'path':
                if 'foot' in json_data['elements'][i]['tags']:
                    # footway on path. Suitable for bus Stop
                    print('sidewalk on path, type: ' + json_data['elements'][i]['tags']['foot'])
            elif wayType == 'footway':
                print('sidewalk on path, type: ' + json_data['elements'][i]['tags']['highway'])
            elif wayType == 'residential':
                if 'sidewalk' in json_data['elements'][i]['tags']:
                    # Sidewalk on secondary road - perhaps check for left/right
                    '''Check for left right here if needed'''
                    print('sidewalk on residential, type: ' + json_data['elements'][i]['tags']['sidewalk'])
            elif wayType == 'tertiary':
                if 'sidewalk' in json_data['elements'][i]['tags']:
                    # Sidewalk on secondary road - perhaps check for left/right
                    '''Check for left right here if needed'''
                    print('sidewalk on tertiary, type: ' + json_data['elements'][i]['tags']['sidewalk'])
            else:
                print('no sidewalk')
        else:
            print('no elements')


# this function arranges user inputs to build the 'query' (in overpass QL language) for roads data and returns the query
def get_roads_query(user_input):
    prefix = """[out:json][timeout:50];(way["highway"](around:"""  # this is string of syntex in 'Overpass QL' language
    suffix = """););out body;"""  # this is string of syntex in 'Overpass QL' language
    q = str(DISTANCEALLOWED) + ',' + str(user_input[0]) + ',' + str(
        user_input[1])  # (radius,latitude,longitude) in a string from the user input
    built_query = prefix + q + suffix  # arrange all above strings into a correct order to form complete query
    return built_query


def get_roads_coords_query(user_input, distanceAround):
    """Takes in user input of coordinates and returns the coordinates of roads
    that are secondary or tertiary"""
    '''includes distance parameter for around feature'''
    prefix = """[out:json][timeout:25];(way["highway"="secondary"](around:"""
    infix1 = """ way["highway"="tertiary"](around:"""
    infix2 = """ way["highway"="residential"](around:"""
    infix3 = """ node["highway"="turning_circle"](around:"""
    infix4 = """ way["highway"="primary"](around:"""
    suffix = """);out geom;"""
    q = str(distanceAround) + ', ' + str(user_input[0]) + ', ' + str(user_input[1]) + ');'
    built_query = prefix + q + infix1 + q + infix2 + q + infix3 + q + infix4 + q + suffix
    return built_query


def test_query(coords, searchDistance):
    """Test query"""
    query = get_roads_coords_query(coords, searchDistance)
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url, params={'data': query})
    json_data = response.json()
    return json_data


def closest_point(coords, way):
    """Takes the coordinates of the existing bus stop and finds the closest node
    on the suitable road"""
    a = pd.DataFrame.to_numpy(pd.DataFrame(way))
    tree = KDTree(a)
    closest_index = tree.query(coords)

    closest_coords = way[closest_index[1]]
    return [closest_coords['lat'], closest_coords['lon']]


def return_suitable_location(coords):
    """New Implementation: This function will start at checking for suitable roads within 5m,
    then keep moving out until a suitable road is reached.
    \\TODO: Set up flag system to store distance moved, and flag up long transfers

    """

    start = time.time()

    searchDistance = 20
    # INCREMENT = 5
    DISTANCEALLOWED = 1300
    satisfied = False
    newStopCoords = []
    distanceMoved = 0
    json_data = []
    overpass_url = "http://overpass-api.de/api/interpreter"
    while satisfied == False:
        # print(str(i))
        query = get_roads_coords_query(coords, searchDistance)
        response = requests.get(overpass_url, params={'data': query})
        try:
            print(response.json())
            json_data = response.json()
            if not json_data['elements']:
                # no response, no suitable road, move out and try again
                searchDistance += searchDistance
                # print('got here, search distance increased')
                # print('search distance now '+ str(searchDistance))
            else:
                # A response: CHECK FOR PAVEMENT????
                # print('got here: elements returned')
                satisfied = True
                newStopCoords = closest_point(coords, json_data['elements'][0]['geometry'])
                distanceMoved = geopy.distance.distance(coords, newStopCoords).m
                print(
                    'Stop has been moved ' + str(distanceMoved) + 'm, search distance = ' + str(searchDistance) + 'm.')
        except ValueError:
            # Currently operating under the assumption that the API needs a second to breathe
            # So I'm just going to try request it again and see what happens
            print('Json Decode Error')

        if searchDistance > DISTANCEALLOWED:
            # print('got here: search > Distance Allowed')
            satisfied = True
            print('No suitable location for ' + str(coords[0]) + ', ' + str(coords[1]) + ' within ' + str(
                searchDistance) + 'm.')
    end = time.time()

    print(end - start)
    print(newStopCoords)
    newStopCoords.append(distanceMoved)
    return newStopCoords


'''Test New Feature: Search within 150 metres, find if any road types, then prioritise
Primary, then secondary, then tertiary, and then finally 2 lane residential
'''


def return_suitable_location2(coords):
    start = time.time()
    # search distance starting at 150
    searchDistance = 250
    newStopCoords = []
    distanceMoved = 0
    json_data = []
    overpass_url = "http://overpass-api.de/api/interpreter"

    satisfied = False
    while satisfied == False:
        try:
            query = get_roads_coords_query(coords, searchDistance)
            response = requests.get(overpass_url, params={'data': query})
            # print(response.json())
            json_data = response.json()
            if not json_data['elements']:
                # no response, no suitable road, move out and try again
                satisfied = True
                print('No suitable location for ' + str(coords[0]) + ', ' + str(coords[1]) + ' within ' + str(
                    searchDistance) + 'm.')
                newStopCoords = [coords[0], coords[1]]
                chosenRoad = "none"

            else:
                # A response: Check for secondary, then tertiary, then two lane residential
                # \\TODO: Check for pavement
                numberRoads = len(json_data['elements'])  # This minus one for last index
                priorityMeasure = 0
                chosenIndex = -1
                chosenRoad = ""
                turningCircleFlag = False
                turningCircleCoords = []
                for i in range(0, numberRoads):
                    currentRoad = json_data['elements'][i]['tags']
                    print(json_data['elements'][i])
                    typeRoad = json_data['elements'][i]['tags']['highway']
                    print(currentRoad)
                    currentRoadPriority = 0
                    if (typeRoad == "residential"):
                        # check if access is private, and if 2 lane, and \\TODO: paved surface and TURNING CIRCLE
                        if 'access' in currentRoad:
                            if currentRoad['access'] == 'private':
                                # Not suitable as a road.
                                print("private road")
                        else:
                            if 'lanes' in currentRoad:
                                if int(currentRoad['lanes']) > 1:
                                    # suitable road
                                    currentRoadPriority = 1
                                    if currentRoadPriority > priorityMeasure:
                                        priorityMeasure = currentRoadPriority
                                        chosenIndex = i
                                        chosenRoad = typeRoad
                                else:
                                    # unsuitable road, one lane
                                    print("one lane")
                            elif 'oneway' in currentRoad:
                                # one way, might be an issue
                                print("One way, ignore for now")  # \\TODO: make more sense of this
                            else:
                                # no lanes tag on residential road, rare, take as suitable road
                                print("No lanes tag, residential road")
                                currentRoadPriority = 1
                                if currentRoadPriority > priorityMeasure:
                                    priorityMeasure = currentRoadPriority
                                    chosenIndex = i
                                    chosenRoad = typeRoad
                    elif typeRoad == "turning_circle":
                        # A turning circle has been detected. This might only become relevant
                        # If a residential road is chosen.
                        # Store the co-ordinates of the turning circle and flag that a turning circle is present
                        turningCircleFlag = True
                        print("turning circle found")
                        turningCircleCoords = [json_data['elements'][i]['lat'], json_data['elements'][i]['lon']]
                    elif typeRoad == "tertiary":
                        print("tertiary road")
                        if 'access' in currentRoad:
                            if currentRoad['access'] == 'private':
                                # Not suitable as a road.
                                print("private tertiary road")
                        else:
                            if 'lanes' in currentRoad:
                                if int(currentRoad['lanes']) > 1:
                                    # suitable road
                                    # print("suitable tertiary road")
                                    currentRoadPriority = 2
                                    if currentRoadPriority > priorityMeasure:
                                        priorityMeasure = currentRoadPriority
                                        chosenIndex = i
                                        chosenRoad = typeRoad
                                        # print("Chosen Index: " + str(chosenIndex))
                            else:
                                # no lanes on road, but as tertiary, should be fine
                                currentRoadPriority = 2
                                if currentRoadPriority > priorityMeasure:
                                    priorityMeasure = currentRoadPriority
                                    chosenIndex = i
                                    chosenRoad = typeRoad
                                    # print("Chosen Index: " + str(chosenIndex))
                    elif (typeRoad == "secondary"):
                        if 'access' in currentRoad:
                            if currentRoad['access'] == 'private':
                                # Not suitable as a road.
                                print("private road")
                        else:
                            if 'lanes' in currentRoad:
                                if int(currentRoad['lanes']) > 1:
                                    # suitable road
                                    currentRoadPriority = 3
                                    if currentRoadPriority > priorityMeasure:
                                        priorityMeasure = currentRoadPriority
                                        chosenIndex = i
                                        chosenRoad = typeRoad
                            else:
                                # no lanes tag, but as secondary, should be fine
                                currentRoadPriority = 3
                                if currentRoadPriority > priorityMeasure:
                                    priorityMeasure = currentRoadPriority
                                    chosenIndex = i
                                    chosenRoad = typeRoad
                    elif typeRoad == "primary":
                        currentRoadPriority = 4
                        print("Primary road chosen")
                        if currentRoadPriority > priorityMeasure:
                            priorityMeasure = currentRoadPriority
                            chosenIndex = i
                            chosenRoad = typeRoad
                satisfied = True
                # In case of residential road, turning circle must be dealt with
                # aim is to choose point on road that is furthest from the turning circle
                print(str(priorityMeasure) + " is priority Measure")
                if priorityMeasure == 1 & turningCircleFlag == True:
                    # turning circle present and residential road chosen: choose point furthest from circle
                    print("Went in here")
                    newStopCoords = furthest_point_from_turning_circle(turningCircleCoords,
                                                                       json_data['elements'][chosenIndex]['geometry'])
                if priorityMeasure == 0:
                    # no suitable road found
                    print('No suitable location for ' + str(coords[0]) + ', ' + str(coords[1]) + ' within ' + str(
                        searchDistance) + 'm.')
                    newStopCoords = [coords[0], coords[1]]
                    chosenRoad = 'none'
                else:
                    newStopCoords = closest_point(coords, json_data['elements'][chosenIndex]['geometry'])
                    distanceMoved = geopy.distance.distance(coords, newStopCoords).m
                    print(
                        'Stop has been moved ' + str(distanceMoved) + 'm, search distance = ' + str(
                            searchDistance) + 'm.')
        except ValueError:
            # Currently operating under the assumption that the API needs a second to breathe
            # So I'm just going to try request it again and see what happens
            print('Json Decode Error')

    end = time.time()

    print(end - start)
    print(newStopCoords)
    newStopCoords.append(distanceMoved)
    newStopCoords.append(chosenRoad)
    return newStopCoords


def furthest_point_from_turning_circle(turningCircle, way):
    """
    This function will take a road and the co-ordinates of a turning circle
    It will return the co-ordinates of a point on that road that is as far away from the turning circle as possible
    which can be assumed to be the point where the cul-de-sac links with the more major road
    """

    # \\TODO: This function works perfectly, just have to figure out a method to ensure it measures off a suitable road
    maxDist = 0
    maxDistIndex = -1
    for i in range(0, len(way)):
        currentPoint = [way[i]['lat'], way[i]['lon']]
        currentDist = geopy.distance.distance(turningCircle, currentPoint).m
        if currentDist > maxDist:
            maxDist = currentDist
            maxDistIndex = i

    return [way[maxDistIndex]['lat'], way[maxDistIndex]['lon']]


def return_location_sidewalks(coords):
    start = time.time()
    # search distance starting at 150
    searchDistance = 250
    newStopCoords = []
    distanceMoved = 0
    json_data = []
    overpass_url = "http://overpass-api.de/api/interpreter"

    satisfied = False
    while satisfied == False:
        try:
            query = get_roads_coords_query(coords, searchDistance)
            response = requests.get(overpass_url, params={'data': query})
            # print(response.json())
            json_data = response.json()
            if not json_data['elements']:
                # no response, no suitable road, move out and try again
                satisfied = True
                print('No suitable location for ' + str(coords[0]) + ', ' + str(coords[1]) + ' within ' + str(
                    searchDistance) + 'm.')
                newStopCoords = [coords[0], coords[1]]
                chosenRoad = "none"

            else:
                # A response: Check for secondary, then tertiary, then two lane residential
                # \\TODO: Check for pavement
                numberRoads = len(json_data['elements'])  # This minus one for last index
                priorityMeasure = 0
                chosenIndex = -1
                chosenRoad = ""
                turningCircleFlag = False
                turningCircleCoords = []
                for i in range(0, numberRoads):
                    currentRoad = json_data['elements'][i]['tags']
                    print(json_data['elements'][i])
                    typeRoad = json_data['elements'][i]['tags']['highway']
                    print(currentRoad)
                    currentRoadPriority = 0
                    if (typeRoad == "residential"):
                        # check if access is private, and if 2 lane, and \\TODO: paved surface and TURNING CIRCLE
                        if 'access' in currentRoad:
                            if currentRoad['access'] == 'private':
                                # Not suitable as a road.
                                print("private road")
                        else:
                            if 'lanes' in currentRoad:
                                if int(currentRoad['lanes']) > 1:
                                    # suitable road
                                    currentRoadPriority = 1
                                    if currentRoadPriority > priorityMeasure:
                                        priorityMeasure = currentRoadPriority
                                        chosenIndex = i
                                        chosenRoad = typeRoad
                                else:
                                    # unsuitable road, one lane
                                    print("one lane")
                            elif 'oneway' in currentRoad:
                                # one way, might be an issue
                                print("One way, ignore for now")  # \\TODO: make more sense of this
                            else:
                                # no lanes tag on residential road, rare, take as suitable road
                                print("No lanes tag, residential road")
                                currentRoadPriority = 1
                                if currentRoadPriority > priorityMeasure:
                                    priorityMeasure = currentRoadPriority
                                    chosenIndex = i
                                    chosenRoad = typeRoad
                    elif typeRoad == "turning_circle":
                        # A turning circle has been detected. This might only become relevant
                        # If a residential road is chosen.
                        # Store the co-ordinates of the turning circle and flag that a turning circle is present
                        turningCircleFlag = True
                        print("turning circle found")
                        turningCircleCoords = [json_data['elements'][i]['lat'], json_data['elements'][i]['lon']]
                    elif typeRoad == "tertiary":
                        print("tertiary road")
                        if 'access' in currentRoad:
                            if currentRoad['access'] == 'private':
                                # Not suitable as a road.
                                print("private tertiary road")
                        else:
                            if 'lanes' in currentRoad:
                                if int(currentRoad['lanes']) > 1:
                                    # suitable road
                                    # print("suitable tertiary road")
                                    currentRoadPriority = 2
                                    if currentRoadPriority > priorityMeasure:
                                        priorityMeasure = currentRoadPriority
                                        chosenIndex = i
                                        chosenRoad = typeRoad
                                        # print("Chosen Index: " + str(chosenIndex))
                            else:
                                # no lanes on road, but as tertiary, should be fine
                                currentRoadPriority = 2
                                if currentRoadPriority > priorityMeasure:
                                    priorityMeasure = currentRoadPriority
                                    chosenIndex = i
                                    chosenRoad = typeRoad
                                    # print("Chosen Index: " + str(chosenIndex))
                    elif (typeRoad == "secondary"):
                        if 'access' in currentRoad:
                            if currentRoad['access'] == 'private':
                                # Not suitable as a road.
                                print("private road")
                        else:
                            if 'lanes' in currentRoad:
                                if int(currentRoad['lanes']) > 1:
                                    # suitable road
                                    currentRoadPriority = 3
                                    if currentRoadPriority > priorityMeasure:
                                        priorityMeasure = currentRoadPriority
                                        chosenIndex = i
                                        chosenRoad = typeRoad
                            else:
                                # no lanes tag, but as secondary, should be fine
                                currentRoadPriority = 3
                                if currentRoadPriority > priorityMeasure:
                                    priorityMeasure = currentRoadPriority
                                    chosenIndex = i
                                    chosenRoad = typeRoad
                    elif typeRoad == "primary":
                        currentRoadPriority = 4
                        print("Primary road chosen")
                        if currentRoadPriority > priorityMeasure:
                            priorityMeasure = currentRoadPriority
                            chosenIndex = i
                            chosenRoad = typeRoad
                satisfied = True
                # In case of residential road, turning circle must be dealt with
                # aim is to choose point on road that is furthest from the turning circle
                print(str(priorityMeasure) + " is priority Measure")
                if priorityMeasure == 1 & turningCircleFlag == True:
                    # turning circle present and residential road chosen: choose point furthest from circle
                    print("Went in here")
                    newStopCoords = furthest_point_from_turning_circle(turningCircleCoords,
                                                                       json_data['elements'][chosenIndex]['geometry'])
                if priorityMeasure == 0:
                    # no suitable road found
                    print('No suitable location for ' + str(coords[0]) + ', ' + str(coords[1]) + ' within ' + str(
                        searchDistance) + 'm.')
                    newStopCoords = [coords[0], coords[1]]
                    chosenRoad = 'none'
                else:
                    newStopCoords = closest_point(coords, json_data['elements'][chosenIndex]['geometry'])
                    distanceMoved = geopy.distance.distance(coords, newStopCoords).m
                    print(
                        'Stop has been moved ' + str(distanceMoved) + 'm, search distance = ' + str(
                            searchDistance) + 'm.')
        except ValueError:
            # Currently operating under the assumption that the API needs a second to breathe
            # So I'm just going to try request it again and see what happens
            print('Json Decode Error')

    end = time.time()

    print(end - start)
    print(newStopCoords)
    newStopCoords.append(distanceMoved)
    newStopCoords.append(chosenRoad)
    return newStopCoords


def sidewalk_check(way):
    """
    This method takes in a way from the openStreetMap API and returns true if this way features a suitable sidewalk,
    and false if it doesn't.
    \\TODO: Figure out what to do with footway tagged ways that have sidewalks
    :param way:
    :return:
    """
    wayType = way['highway']
    if wayType == 'secondary':
        # secondary style road - check for sidewalk (If thats a thing, might not be)
        if 'sidewalk' in way:
            # Sidewalk on secondary road - perhaps check for left/right
            '''Check for left right here if needed'''
            print('sidewalk on secondary, type: ' + way['sidewalk'])
            return True
    elif wayType == 'primary':
        if 'sidewalk' in way:
            # Sidewalk on secondary road - perhaps check for left/right
            '''Check for left right here if needed'''
            print('sidewalk on primary, type: ' + way['sidewalk'])
            return True
    elif wayType == 'path':
        if 'foot' in way:
            # footway on path. Suitable for bus Stop
            print('sidewalk on path, type: ' + way['foot'])
            return True
    elif wayType == 'footway':
        print('sidewalk on path, type: ' + way['highway'])
        return True
    elif wayType == 'residential':
        if 'sidewalk' in way:
            # Sidewalk on secondary road - perhaps check for left/right
            '''Check for left right here if needed'''
            print('sidewalk on residential, type: ' + way['sidewalk'])
            return True
    elif wayType == 'tertiary':
        if 'sidewalk' in way:
            # Sidewalk on secondary road - perhaps check for left/right
            '''Check for left right here if needed'''
            print('sidewalk on tertiary, type: ' + way['sidewalk'])
            return True
    else:
        print('no sidewalk')
        return False


def sidewalk_check_stop(coords):
    """
    Takes in a stop, and returns true if a sidewalk is present and false if not.
    :param coords:
    :return:
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    pavement_string = ""
    satisfied = False
    while not satisfied:
        try:
            query = get_roads_sidewalk_query(coords)
            response = requests.get(overpass_url, params={'data': query})
            # print(response.json())
            json_data = response.json()
            if not json_data['elements']:
                # no response, no suitable road, move out and try again
                satisfied = True
                print("ERROR. This shouldn't happen, as these co-ordinates have already returned positive")
                pavement_string = "ERROR"
                return pavement_string

            else:
                # \\TODO: Check for pavement
                numberRoads = len(json_data['elements'])  # This minus one for last index
                pavement = False
                for i in range(0, numberRoads):
                    currentRoad = json_data['elements'][i]['tags']
                    result = sidewalk_check(currentRoad)
                    if result:
                        pavement = True
                if pavement:
                    pavement_string = "Present"
                else:
                    pavement_string = "Not Present"
                satisfied = True
                return pavement_string
        except ValueError:
            # Currently operating under the assumption that the API needs a second to breathe
            # So I'm just going to try request it again and see what happens
            print('Json Decode Error')


def get_roads_sidewalk_query(user_input):
    prefix = """[out:json][timeout:50];(way["highway"](around:"""  # this is string of syntex in 'Overpass QL' language
    suffix = """););out body;"""  # this is string of syntex in 'Overpass QL' language
    q = str(15) + ',' + str(user_input[0]) + ',' + str(
        user_input[1])  # (radius,latitude,longitude) in a string from the user input
    built_query = prefix + q + suffix  # arrange all above strings into a correct order to form complete query
    return built_query


def return_suitable_location_outSearch(coords):
    """
    \\TODO: Write this
    :param coords:
    :return: fixedCoords
    """
    start = time.time()
    # search distance starting at 50
    search_distance = 50
    incrementer = 50
    max_distance = 200
    new_stop_coords = []
    distance_moved = 0
    json_data = []
    overpass_url = "http://overpass-api.de/api/interpreter"

    satisfied = False
    while not satisfied:
        try:
            query = get_roads_coords_query(coords, search_distance)
            response = requests.get(overpass_url, params={'data': query})
            # print(response.json())
            json_data = response.json()
            if not json_data['elements']:
                # no response, no suitable road, move out and try again
                print('No suitable location for ' + str(coords[0]) + ', ' + str(coords[1]) + ' within ' + str(
                    search_distance) + 'm.')
                if search_distance == max_distance:
                    # no suitable roads
                    satisfied = True
                    print("search = max, returning as none")
                    new_stop_coords = [coords[0], coords[1]]
                    chosen_road = "none"
                else:
                    # increment search distance
                    search_distance = search_distance + incrementer
                    print("Extending search distance to " + str(search_distance))
            else:
                # A response: Check for secondary, then tertiary, then two lane residential
                # \\TODO: Check for pavement
                number_roads = len(json_data['elements'])  # This minus one for last index
                priority_measure = 0
                chosen_index = -1
                chosen_road = ""
                turning_circle_flag = False
                turning_circle_coords = []
                for i in range(0, number_roads):
                    current_road = json_data['elements'][i]['tags']
                    #print(json_data['elements'][i])
                    type_road = json_data['elements'][i]['tags']['highway']
                    print(current_road)
                    current_road_priority = 0
                    if type_road == "residential":
                        # check if access is private, and if 2 lane, and \\TODO: paved surface and TURNING CIRCLE
                        if 'access' in current_road:
                            if current_road['access'] == 'private':
                                # Not suitable as a road.
                                print("private road")
                        else:
                            if 'lanes' in current_road:
                                if int(current_road['lanes']) > 1:
                                    # suitable road
                                    current_road_priority = 1
                                    if current_road_priority > priority_measure:
                                        priority_measure = current_road_priority
                                        chosen_index = i
                                        chosen_road = type_road
                                else:
                                    # unsuitable road, one lane
                                    print("one lane")
                            elif 'oneway' in current_road:
                                # one way, might be an issue
                                print("One way, ignore for now")  # \\TODO: make more sense of this
                            else:
                                # no lanes tag on residential road, rare, take as suitable road
                                print("No lanes tag, residential road")
                                current_road_priority = 1
                                if current_road_priority > priority_measure:
                                    priority_measure = current_road_priority
                                    chosen_index = i
                                    chosen_road = type_road
                    elif type_road == "turning_circle":
                        # A turning circle has been detected. This might only become relevant
                        # If a residential road is chosen.
                        # Store the co-ordinates of the turning circle and flag that a turning circle is present
                        turning_circle_flag = True
                        print("turning circle found")
                        turning_circle_coords = [json_data['elements'][i]['lat'], json_data['elements'][i]['lon']]
                    elif type_road == "tertiary":
                        print("tertiary road")
                        if 'access' in current_road:
                            if current_road['access'] == 'private':
                                # Not suitable as a road.
                                print("private tertiary road")
                        else:
                            if 'lanes' in current_road:
                                if int(current_road['lanes']) > 1:
                                    # suitable road
                                    # print("suitable tertiary road")
                                    current_road_priority = 2
                                    if current_road_priority > priority_measure:
                                        priority_measure = current_road_priority
                                        chosen_index = i
                                        chosen_road = type_road
                                        # print("Chosen Index: " + str(chosenIndex))
                            else:
                                # no lanes on road, but as tertiary, should be fine
                                current_road_priority = 2
                                if current_road_priority > priority_measure:
                                    priority_measure = current_road_priority
                                    chosen_index = i
                                    chosen_road = type_road
                                    # print("Chosen Index: " + str(chosenIndex))
                    elif type_road == "secondary":
                        if 'access' in current_road:
                            if current_road['access'] == 'private':
                                # Not suitable as a road.
                                print("private road")
                        else:
                            if 'lanes' in current_road:
                                if int(current_road['lanes']) > 1:
                                    # suitable road
                                    current_road_priority = 3
                                    if current_road_priority > priority_measure:
                                        priority_measure = current_road_priority
                                        chosen_index = i
                                        chosen_road = type_road
                            else:
                                # no lanes tag, but as secondary, should be fine
                                current_road_priority = 3
                                if current_road_priority > priority_measure:
                                    priority_measure = current_road_priority
                                    chosen_index = i
                                    chosen_road = type_road
                    elif type_road == "primary":
                        current_road_priority = 4
                        print("Primary road chosen")
                        if current_road_priority > priority_measure:
                            priority_measure = current_road_priority
                            chosen_index = i
                            chosen_road = type_road
                # In case of residential road, turning circle must be dealt with
                # aim is to choose point on road that is furthest from the turning circle
                print(str(priority_measure) + " is priority Measure")
                if priority_measure == 1 & turning_circle_flag == True:
                    # turning circle present and residential road chosen: choose point furthest from circle
                    print("Went in here")
                    new_stop_coords = furthest_point_from_turning_circle(
                        turning_circle_coords, json_data['elements'][chosen_index]['geometry'])
                if priority_measure == 0:
                    # no suitable road found
                    print('No suitable location for ' + str(coords[0]) + ', ' + str(coords[1]) + ' within ' + str(
                        search_distance) + 'm.')
                    if search_distance == max_distance:
                        # no suitable roads
                        satisfied = True
                        print("search = max, returning as none")
                        new_stop_coords = [coords[0], coords[1]]
                        chosen_road = "none"
                    else:
                        # increment search distance
                        search_distance = search_distance + incrementer
                        print("Extending search distance to " + str(search_distance))
                else:
                    new_stop_coords = closest_point(coords, json_data['elements'][chosen_index]['geometry'])
                    distance_moved = geopy.distance.distance(coords, new_stop_coords).m
                    print(
                        'Stop has been moved ' + str(distance_moved) + 'm, search distance = ' + str(
                            search_distance) + 'm.')
                    satisfied = True
        except ValueError:
            # Currently operating under the assumption that the API needs a second to breathe
            # So I'm just going to try request it again and see what happens
            print('Json Decode Error')

    end = time.time()

    print(end - start)
    print(new_stop_coords)
    new_stop_coords.append(distance_moved)
    new_stop_coords.append(chosen_road)
    return new_stop_coords
