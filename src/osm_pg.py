# import matplotlib.patches as patches
# import matplotlib.pyplot as plt
# import numpy as np
# import osmapi
# from mpl_toolkits.basemap import Basemap
#
# osm_file = './data/map.osm'
#
#
# # create an instance of the osmapi class
# api = osmapi.OsmApi()
#
# # open the OSM file
# with open(osm_file, 'r') as f:
#     xml_data = f.read()
#
# # parse the XML data and get the building nodes
# osm_data = osmapi.
# building_nodes = [node for node in osm_data if node['type'] == 'node' and 'building' in node['tags']]
#
# # print the building nodes
# print(building_nodes)
#
# # Create a basemap
# fig = plt.figure(figsize=(8, 8))
# m = Basemap(projection='merc', llcrnrlat=your_min_latitude, urcrnrlat=your_max_latitude,
#             llcrnrlon=your_min_longitude, urcrnrlon=your_max_longitude, resolution='h')
#
# # Add map.osm elements
# m.drawcoastlines()
# m.drawcountries()
# m.drawstates()
#
# # Add buildings to the map.osm
# for building in building_handler.buildings:
#     coords = np.array([(node.lon, node.lat) for node in building.nodes])
#     x, y = m(coords[:, 0], coords[:, 1])
#     patch = patches.Polygon(xy=list(zip(x, y)), facecolor='red', alpha=0.5)
#     plt.gca().add_patch(patch)
#
# # Show the map.osm
# plt.show()


# import osmread
#
# with open('path/to/osm/file.osm.xml', 'rb') as osm_xml_file:
#     for entity in osmread.parse_xml(osm_xml_file):
#         if isinstance(entity, osmread.Node):
#             if 'name' in entity.tags:
#                 print(entity.tags['name'])

#
# import osmium
# import sys
# import osm2geojson
# import json
#
# class OSMHandler(osmium.SimpleHandler):
#     def __init__(self):
#         osmium.SimpleHandler.__init__(self)
#         self.features = []
#
#     def node(self, n):
#         if 'name' in n.tags:
#             feature = osm2geojson.node(n)
#             self.features.append(feature)
#
#     def way(self, w):
#         if 'name' in w.tags:
#             feature = osm2geojson.way(w)
#             self.features.append(feature)
#
#     def relation(self, r):
#         if 'name' in r.tags:
#             feature = osm2geojson.relation(r)
#             self.features.append(feature)
#
# if __name__ == '__main__':
#     # if len(sys.argv) != 3:
#     #     print("Usage: python osm_to_geojson.py input.osm output.geojson")
#     #     sys.exit(-1)
#
#     input_file = '/Users/shlomo/Desktop/reps/604/data/map.osm'
#     output_file = '/Users/shlomo/Desktop/reps/604/data/map2.geojson'
#
#     handler = OSMHandler()
#     handler.apply_file(input_file)
#
#     with open(output_file, 'w') as outfile:
#         json.dump(osm2geojson.json_object(handler.features), outfile).
#
#
#
#
# import osmnx as ox
#
# a= ox.geometries_from_xml('./data/map.osm')
# cols = [i for i in a.columns if 'building' in i]
# b = a[cols]
# pass
import codecs
import osm2geojson

with codecs.open('./data/map.osm', 'r', encoding='utf-8') as data:
    xml = data.read()
geojson = osm2geojson.xml2geojson(xml, filter_used_refs=False, log_level='INFO')
building = [i for i in geojson['features'] if i['properties'].get('building')]
pass