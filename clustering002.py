# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 11:38:49 2021

@author: Diarmuid
"""

import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon

street_map = gpd.read_file('C:\\Users\\Diarmuid\\Documents\\College\\MSISS 4TH YEAR\\FYP\\Notes and Misc\\Halifax Shape File\\Street_Network.shp')
fig.ax = plt.suplots(figsize = (15,15))
street_map.plot(ax = ax)
