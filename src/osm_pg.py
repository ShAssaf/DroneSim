import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import osmapi
from mpl_toolkits.basemap import Basemap

osm_file = './data/map.osm'


# create an instance of the osmapi class
api = osmapi.OsmApi()

# open the OSM file
with open(osm_file, 'r') as f:
    xml_data = f.read()

# parse the XML data and get the building nodes
osm_data = osmapi.
building_nodes = [node for node in osm_data if node['type'] == 'node' and 'building' in node['tags']]

# print the building nodes
print(building_nodes)

# Create a basemap
fig = plt.figure(figsize=(8, 8))
m = Basemap(projection='merc', llcrnrlat=your_min_latitude, urcrnrlat=your_max_latitude,
            llcrnrlon=your_min_longitude, urcrnrlon=your_max_longitude, resolution='h')

# Add map.osm elements
m.drawcoastlines()
m.drawcountries()
m.drawstates()

# Add buildings to the map.osm
for building in building_handler.buildings:
    coords = np.array([(node.lon, node.lat) for node in building.nodes])
    x, y = m(coords[:, 0], coords[:, 1])
    patch = patches.Polygon(xy=list(zip(x, y)), facecolor='red', alpha=0.5)
    plt.gca().add_patch(patch)

# Show the map.osm
plt.show()
