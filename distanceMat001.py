# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 12:23:07 2021

@author: Diarmuid
"""

#Distance matrix function: takes coords and sends back distance matrix from Graphhopper
import time
import requests
import json
import pandas as pd
import numpy as np

def graphhopperMatrix(coords, depot):
    #Potentially slow, perhaps use concatenate
    coords2 = np.insert(coords, 0, depot, axis=0)
    Long = pd.core.series.Series(coords2[:,1])
    Lat = pd.core.series.Series(coords2[:,0])
    locationArray = list(zip(Long, Lat))

    URL = "https://graphhopper.com/api/1/matrix?key=4e2c94b1-14ff-4eb5-8122-cacf2e34043d&ch.disable=true"
    
    payload = {"points":locationArray,
               "vehicle":"foot",
               "out_arrays":["times","distances"]}
    
    start = time.time()
    
    r = requests.post(URL, json = payload)
    
    end = time.time()
    
    print(end - start)
    
    json_data = json.loads(r.text)
    
    return json_data
