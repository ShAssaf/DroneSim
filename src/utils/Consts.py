import os


class Consts:
    CLOSE_RANGE = 20
    MEDIUM_RANGE = 100
    FAR_RANGE = 500
    DISTANCE_TO_TARGET = 5
    VERTICAL_TAKE_OFF_MIN = 20
    # DRONE_POSITIONS_PATH = 'data/csvs/source_target.csv'
    DT = 1
    REAL_TIME = False
    BigDroneSize = 10
    SmallDroneSize = 20
    MAP_IMG_PATH = None
    MAX_RANGE_FOR_COLOR = 255
    FONT_SIZE = 12
    HOST = '127.0.0.1'
    PORT = 9981
    GRAPH_PORT = 9995
    ENV_PORT = 9996


DEBUG = False  # Set this flag to True to enable debug mode
MANUAL_DRONE = True


class Paths:
    BASE_PATH = 'file://' + os.getcwd()
    ENVIRONMENT_PATHS = 'data/optional_paths.pickle'
    TMP = '/tmp/'
    MAPS = 'data/maps'
    MAP_BOUNDS_PATH = 'data/csvs/map_bounds.csv'
    MAP_NO_BG_PATH = MAPS + '/no_bg_result.png'
    MAP_BG_PATH = MAPS + '/bg_result.png'
    RESCALED_MAP_PATH = MAPS + '/rescaled_map_1_pixel_per_1_meter.png'
    RESCALED_BG_MAP_PATH = MAPS + '/rescaled_map_1_pixel.jpg'
    GEOJSON_PATH = 'data/geojson/exemple_for_geoJson.geojson'
    BUILDINGS_GEOJSON_PATH = 'data/geojson/buildings.geojson'
    MAP_BG_HTML_FULL_PATH = MAPS +'/maps_html/map_bg.html'
    MAP_NO_BG_HTML_FULL_PATH = MAPS + '/maps_html/map_no_bg.html'
    MAP_HTML_FULL_PATH = MAPS + '/maps_html/map_no_bg.html'
    ENVIRONMENT_GRAPH = 'data/environment_graph.pickle'


class BatterySpec:
    VOLTAGE = 3.7
    CAPACITY = 3000  # in mAh


class RadarSpec:
    RANGE = 500  # in meters


class SmallDroneDefaults:
    BATTERY = BatterySpec.CAPACITY
    MAX_SPEED = 8
    MAX_VERTICAL_SPEED = 3
    MAX_HEIGHT = 400
    MAX_DISTANCE = 1000


class MapConsts:
    SCREEN_WIDTH = 500
    SCREEN_HEIGHT = 500
    MAP_PATH = Paths.MAPS + '/rescaled_map_1_pixel_per_1_meter_building_deionised.jpg'


class EnvironmentConsts:
    DRONES_CONTROL = 0
    MAP_CONTROL = 1
    CHOOSE_DRONE = 2
    FOCUS_DRONE = 3
    MODES_LIST = [DRONES_CONTROL, MAP_CONTROL, CHOOSE_DRONE, FOCUS_DRONE]


class NoiseConsts:
    STD = 0
    MEAN = 0