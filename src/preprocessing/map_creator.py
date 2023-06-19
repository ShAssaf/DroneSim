import random
import folium
import json
from src.utils import Consts
from src.utils.map_obj import MapObject

"""This script creates a map with a GeoJSON overlay and a colorbar legend."""


def filter_geojson(input_file, output_file):
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Filter features
    filtered_features = []
    for feature in data['features']:
        if 'building' in feature['properties']:
            filtered_features.append(feature)

    # Update the feature collection
    data['features'] = filtered_features

    # Save the filtered GeoJSON to output file
    with open(output_file, 'w') as file:
        json.dump(data, file)


def generate_building_height():
    # Define the height ranges and their probabilities
    height_ranges = ["0-10", "10-50", "50-100", "100-200", "200-300", "300-"]
    probabilities = [0.10, 0.30, 0.25, 0.20, 0.10, 0.05]
    # Use random.choices to select a height range based on the defined probabilities
    height = random.choices(height_ranges, probabilities)[0]
    height = height.split("-")[1]
    height = float(height) * 0.75 if height != "" else 350
    return height


def generate_color_map(value):
    # Scale the value to a range between 0 and 1
    if value > 400:
        value = 400
    normalized_value = value / 400

    # Interpolate the RGB components
    red = int((normalized_value) * 0)
    green = int((normalized_value) * 0)
    blue = int((normalized_value) * 255)

    # Convert the RGB components to hexadecimal format
    hex_value = "#{:02x}{:02x}{:02x}".format(red, green, blue)

    return hex_value


def get_height(feature):
    try:
        float(feature['properties']['height'].replace('m', ''))
        return float(feature['properties']['height'].replace('m', ''))
    except:
        pass
    if 'building:levels' in feature['properties']:
        return float(feature['properties']['building:levels']) * 3
    elif 'building:height' in feature['properties']:
        return float(feature['properties']['building:height'].replace('m', ''))
    return generate_building_height()


def height_style_function(feature):
    # Get the height value of the feature
    height = get_height(feature)
    # Check if the geometry is a polygon
    if feature['geometry']['type'] == 'Polygon':
        color = generate_color_map(height)
        return {
            "fillOpacity": 1,
            "fillColor": color,
            "weight": 0,

        }

    else:
        # Non-polygon feature (e.g., line or point)
        return {'fillColor': 'gray', 'color': 'black', 'weight': 1.5, 'fillOpacity': 0.6}

def get_north_east_corner(geojson_path):
    with open(geojson_path, 'r') as file:
        data = json.load(file)
    max_lat = float('-inf')
    max_long = float('-inf')
    for feature in data['features']:
        if feature['geometry']['type'] == 'Polygon':
            for point in feature['geometry']['coordinates'][0]:
                if point[1] > max_lat:
                    max_lat = point[1]
                if point[0] > max_long:
                    max_long = point[0]
    return max_lat, max_long
def get_south_west_corner(geojson_path):
    with open(geojson_path, 'r') as file:
        data = json.load(file)
    min_lat = float('inf')
    min_long = float('inf')
    for feature in data['features']:
        if feature['geometry']['type'] == 'Polygon':
            for point in feature['geometry']['coordinates'][0]:
                if point[1] < min_lat:
                    min_lat = point[1]
                if point[0] < min_long:
                    min_long = point[0]
    return min_lat, min_long


def map_creator_main():

    # filter_geojson(Consts.Paths.GEOJSON_PATH, Consts.Paths.BUILDINGS_GEOJSON_PATH)

    # load bounds from csv
    lat_min, long_min = get_south_west_corner(Consts.Paths.BUILDINGS_GEOJSON_PATH)
    lat_max, long_max = get_north_east_corner(Consts.Paths.BUILDINGS_GEOJSON_PATH)
    MapObject.set_map_bounds(lat_min, long_min, lat_max, long_max,Consts.Paths.BUILDINGS_GEOJSON_PATH)

    map_bg = folium.Map(location=[lat_min, long_min], zoom_start=19)
    map_no_bg = folium.Map(location=[lat_min, long_min], zoom_start=19, tiles=None)
    #map_black_CartoDB = folium.Map(location=[lat_min, long_min], zoom_start=20, tiles="CartoDB dark_matter")
    # Add GeoJSON data to the map with custom style
    folium.GeoJson(Consts.Paths.BUILDINGS_GEOJSON_PATH, style_function=height_style_function).add_to(map_bg)
    folium.GeoJson(Consts.Paths.BUILDINGS_GEOJSON_PATH, style_function=height_style_function).add_to(map_no_bg)
    #folium.GeoJson(Consts.Paths.BUILDINGS_GEOJSON_PATH, style_function=height_style_function).add_to(map_black_CartoDB)

    # save the map
    map_no_bg.save("./data/map_no_bg.html")
    map_bg.save("./data/map_bg.html")
    #map_black_CartoDB.save("./data/map_black_CartoDB.html")


if __name__ == '__main__':
    map_creator_main()
