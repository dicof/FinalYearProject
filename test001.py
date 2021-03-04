import busStopCheck as bsc
import requests


overpass_url = "http://overpass-api.de/api/interpreter"

query = bsc.get_roads_coords_query([44.7315, -63.75531], 150)
print(query)
response = requests.get(overpass_url, params={'data': query})
print(response.json())
