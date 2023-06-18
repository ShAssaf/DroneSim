import math
import geojsonio
import geojson
import matplotlib.pyplot as plt
import pandas as pd
import pyproj
from mpl_toolkits.basemap import Basemap
import geopandas as gpd
from src.get_image_from_google_maps import get_image_from_google_maps
from src.utils.Consts import Paths


# os.environ['PROJ_LIB'] = r'D:\ProgramData\python\Library\share'


class GeoJsonParser:
    def __init__(self):
        self.gj = self.get_geojson_from_data()
        self.building_types = self.get_all_building_types()
        self.roads = self.get_all_roads()
        self.buildings = self.get_all_buildings()

    def get_building_coordinates(self, building_type):
        coordinates = []
        for feature in self.gj['features']:
            if 'building' in feature['properties']:
                if feature['properties']['building'] == building_type:
                    coordinates.append(feature['geometry']['coordinates'])
        return coordinates

    def get_all_building_types(self):
        building_types = set()
        for feature in self.gj['features']:
            if 'building' in feature['properties']:
                building_types.add(feature['properties']['building'])
        return building_types

    def get_all_buildings(self):
        buildings = []
        for feature in self.gj['features']:
            if 'building' in feature['properties']:
                buildings.append(feature)
        return buildings

    def get_all_roads(self):
        roads = []
        for feature in self.gj['features']:
            # if 'highway' in feature['properties']:
            #     roads.append(feature)
            if 'class' in feature['properties']:
                if 'road' in feature['properties']['class']:
                    roads.append(feature)

        return roads

    def get_map_border_from_geo_list(self):
        x_list = []
        y_list = []
        for feature in self.gj['features']:
            coordinates = feature['geometry']['coordinates']
            all_pints = GeoJsonParser.get_elements(coordinates)
            for point in all_pints:
                x_list.append(point[0])
                y_list.append(point[1])
        return [[min(x_list), min(y_list)], [max(x_list), max(y_list)]]

    # def get_google_map_image_by_border(self):
    #     borders = self.get_map_border_from_geo_list()
    #     x_borders_list = [borders[0][0], borders[1][0]]
    #     y_borders_list = [borders[0][1], borders[1][1]]
    #     x_center, y_center = self.get_center_point(x_borders_list, y_borders_list)
    #     center = f"{y_center},{x_center}"
    #     get_image_from_google_maps(center)

    @staticmethod
    def get_center_point(x_borders_list, y_borders_list):
        x_center = (x_borders_list[0] + x_borders_list[1]) / 2
        y_center = (y_borders_list[0] + y_borders_list[1]) / 2
        return x_center, y_center

    @staticmethod
    def get_geojson_from_data(path=Paths.GEOJSON_PATH):
        with open(path, encoding='utf-8') as f:
            gj = geojson.load(f)
        return gj

    @staticmethod
    def get_elements(lst):
        if type(lst[0]) is float:
            return [lst]
        # Recursive case: get the elements from the sub-lists
        elements = []
        for sublist in lst:
            try:
                if type(sublist[0]) is float:
                    elements.append(sublist)
                else:
                    elements.extend(GeoJsonParser.get_elements(sublist))
            except:
                print(sublist[0])
        # Return the elements from the current list, along with the elements from the sub-lists
        return elements

    @staticmethod
    def create_boarder_for_plotting(coordinates):
        # create a new figure
        plt.figure(figsize=(50, 50))

        # create a Basemap instance
        m = Basemap(
            projection='merc', llcrnrlat=coordinates[0][1], urcrnrlat=coordinates[1][1]
            , llcrnrlon=coordinates[0][0], urcrnrlon=coordinates[1][0])
        return m

    @staticmethod
    def add_points_for_plotting(coordinates, sim_map, color='red'):
        # convert latitude and longitude to x and y coordinates
        buildings = []
        for [longitude, latitude] in coordinates:
            x, y = sim_map(longitude, latitude)
            # plot the points on the map.osm
            buildings.append([x, y])
            # map.osm.scatter(x, y, marker='o', color='blue')
        sim_map.plot([x[0] for x in buildings], [x[1] for x in buildings], marker=None, color=color)

    @staticmethod
    def add_roads_for_plotting(roads, sim_map):
        for road in roads:
            coordinates = road['geometry']['coordinates']
            all_pints = GeoJsonParser.get_elements(coordinates)
            all_pints = [sim_map(point[0], point[1]) for point in all_pints]
            sim_map.plot(*zip(*all_pints), marker=None, color='red')

    def plot_map(self, building):
        building = self.get_all_buildings()
        b = pd.read_csv(Paths.MAP_BOUNDS_PATH)
        b = [[b['minx'][0]-5, b['miny'][0]-5], [b['maxx'][0]+10, b['maxy'][0]+10]]
        m = GeoJsonParser.create_boarder_for_plotting(b)
        for i in range(0, len(building)):
            for j in range(0, len(building[i])):
                GeoJsonParser.add_points_for_plotting(building[i][j], m)
        plt.show()

    def plot_heat_map(self):
        buildings = self.get_all_buildings()
        b = pd.read_csv(Paths.MAP_BOUNDS_PATH)
        b = [[b['minx'][0], b['miny'][0]], [b['maxx'][0], b['maxy'][0]]]
        b_map = GeoJsonParser.create_boarder_for_plotting(b)
        for coordinates in buildings:
            if 'height' in coordinates['properties']:
                try:
                    if coordinates['properties']['height'] > '350':
                        GeoJsonParser.add_points_for_plotting(coordinates['geometry']['coordinates'][0], b_map,
                                                              color='red')
                    elif coordinates['properties']['height'] > '300':
                        GeoJsonParser.add_points_for_plotting(coordinates['geometry']['coordinates'][0], b_map,
                                                              color='yellow')
                    elif coordinates['properties']['height'] > '250':
                        GeoJsonParser.add_points_for_plotting(coordinates['geometry']['coordinates'][0], b_map,
                                                              color='orange')
                    elif coordinates['properties']['height'] > '200':
                        GeoJsonParser.add_points_for_plotting(coordinates['geometry']['coordinates'][0], b_map,
                                                              color='pink')
                    elif coordinates['properties']['height'] > '100':
                        GeoJsonParser.add_points_for_plotting(coordinates['geometry']['coordinates'][0], b_map,
                                                              color='blue')
                    elif coordinates['properties']['height'] > '50':
                        GeoJsonParser.add_points_for_plotting(coordinates['geometry']['coordinates'][0], b_map,
                                                              color='purple')
                    else:
                        GeoJsonParser.add_points_for_plotting(coordinates['geometry']['coordinates'][0], b_map,
                                                              color='green')
                except:
                    save_list_to_file(coordinates['geometry']['coordinates'], './data/logs/error_log.txt')
            else:
                try:
                    GeoJsonParser.add_points_for_plotting(coordinates['geometry']['coordinates'][0], b_map,
                                                          color='black')
                except:
                    save_list_to_file(coordinates['geometry']['coordinates'], './data/logs/error_log.txt')

        background_img = plt.imread(Paths.MAP_PATH)

        # Display the image as a background
        b_map.imshow(background_img, interpolation='lanczos', origin='upper', alpha=0.8)

        plt.show()


def save_list_to_file(data, file_name):
    with open(file_name, 'a') as f:
        for item in data:
            f.write(str(item) + '\n')


def determine_utm_zone(longitude):
    return int((longitude + 180) / 6) + 1


def convert_wgs_to_utm(lat, lon):
    wgs84 = pyproj.Proj(proj='latlong', datum='WGS84')
    utm = pyproj.Proj(proj='utm', zone=determine_utm_zone(lon), datum='WGS84')
    x, y = pyproj.transform(wgs84, utm, lon, lat)
    return x, y


#a = GeoJsonParser()
# a.plot_heat_map()
#a.plot_map(a.get_building_coordinates('tower'))
# # save_list_to_file(a.get_all_buildings(), 'buildings.txt')
# # # a.get_google_map_image_by_border()
