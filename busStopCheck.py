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
    ways = len(json_data['elements'])  # number of ways to evaluate
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


# this function gets the input from user.  INPUT = {laitutde, longitude, search_radius, option to specify the data
# domain like hospital,education etc.} returns the list of user inputs
userInput = [44.7007801, -63.6981095]


# this function arranges user inputs to build the 'query' (in overpass QL language) for roads data and returns the query
def get_roads_query(user_input):
    prefix = """[out:json][timeout:50];(way["highway"](around:"""  # this is string of syntex in 'Overpass QL' language
    suffix = """););out body;"""  # this is string of syntex in 'Overpass QL' language
    q = str(DISTANCEALLOWED) + ',' + str(user_input[0]) + ',' + str(
        user_input[1])  # (radius,latitude,longitude) in a string from the user input
    built_query = prefix + q + suffix  # arrange all above strings into a correct order to form complete query
    return built_query


def get_roads_coords_query(user_input, distanceAround):
    '''Takes in user input of coordinates and returns the coordinates of roads
    that are secondary or tertiary'''
    '''includes distance parameter for around feature'''
    prefix3 = """[out:json][timeout:25];(way["highway"="secondary"](around:"""

    infix3 = """ way["highway"="tertiary"](around:"""
    suffix3 = """);out geom;"""
    q = str(distanceAround) + ', ' + str(user_input[0]) + ', ' + str(user_input[1]) + ');'
    built_query = prefix3 + q + infix3 + q + suffix3
    return built_query


def test_query(coords, searchDistance):
    '''Test query'''
    query = get_roads_coords_query(coords, searchDistance)
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url, params={'data': query})
    json_data = response.json()
    return json_data


def closest_point(coords, way):
    '''Takes the coordinates of the existing bus stop and finds the closest node
    on the suitable road'''
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


'''Test New Feature: Search within 150 metres'''


