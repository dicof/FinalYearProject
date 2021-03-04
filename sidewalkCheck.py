# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 01:24:50 2021

@author: Diarmuid
"""

#sidewalkCheck : takes bus stop coordinates, and checks if each location has a sidewalk and is on a suitable road
    
import overpy           # to import the overpy module
import pandas as pd     # to import pandas library
import json 						# to import json
import requests					# to import requests

def check_for_sidewalks(coords):
    query = get_roads_query(coords)
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url,params={'data':query})
    #print(response.text)
    json_data = response.json()
    if 'elements' in json_data:
        if 'sidewalk' in json_data['elements'][0]['tags']:
            if json_data['elements'][0]['tags']['sidewalk'] == 'left':
                print('left')
            else:
                print('right')
        else:
            print('no sidewalk in tags')
    else:
        print('no elements')

#this function gets the input from user.  INPUT = {laitutde, longitude, search_radius, option to specify the data domain like hospital,education etc.}
#returns the list of user inputs
userInput = [44.7007801 , -63.6981095]
#this function arrenge user inputs to build the 'query' (in overpass QL language) for roads data and returns the query
def get_roads_query(user_input):
	prefix = """[out:json][timeout:50];(way["highway"](around:10,""" #this is string of syntex in 'Overpass QL' language
	suffix = """););out body;"""							   	  #this is string of syntex in 'Overpass QL' language
	q = str(user_input[0])+','+str(user_input[1])         #(radius,latitude,longitude) in a string from the user input
	built_query = prefix + q + suffix                             #arrange all above strings into a correct order to form complete query
	return built_query   


# this funciton uses the overpy.Overpass API to send a query and get the response from overpass servers in json format and then it extract the nodes(hospitals , schools) data to a csv file.
def extract_nodes_data_from_OSM(built_query):
	api = overpy.Overpass()                       # creating a overpass API instance 
	result = api.query(built_query)               # get result from API by sending the query to overpass servers
	list_of_node_tags = []                        # initializing empty list , we'll use it to form a dataframe .
	for node in result.nodes:                     # from each node , get the all tags information
		node.tags['latitude'] =  node.lat
		node.tags['longitude'] = node.lon
		node.tags['id'] = node.id
		list_of_node_tags.append(node.tags)
	data_frame = pd.DataFrame(list_of_node_tags)  # forming a pandas dataframe using list of dictionaries
	#data_frame.to_csv('output_data.csv')
	#print("\nCSV file created- 'output_data.csv'. Check the file in current directory.")
	return data_frame                             # return data frame if you want to use it further in main function.



# this function only extracts the raw  json data from overpass api through get request
def extract_raw_data_from_OSM(built_query):
	overpass_url = "http://overpass-api.de/api/interpreter" 					 #url of overpass api
	response = requests.get(overpass_url,params={'data': built_query}) # sending a get request and passing the overpass query as data parameter in url
	#print(response.text)
	json_data = response.json()
	with open("output_data.json", "w") as outfile:  									 # writing the json output to a file
		json.dump(json_data, outfile)
	print("Raw Data extraction successfull!  check 'output_data.json' file.")
	return json_data
 
	
	

    
	
    
    