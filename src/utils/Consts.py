class Consts:
    BigDroneSize = 10
    SmallDroneSize = 100
    MAP_IMG_PATH = None
    MAX_RANGE_FOR_COLOR = 255
    FONT_SIZE = 12

    # default drones

    X = 0
    Y = 1
    Z = 2


DEBUG = True  # Set this flag to True to enable debug mode
MANUAL_DRONE = False


class Paths:
    MAP_BOUNDS_PATH = 'data/csvs/map_bounds.csv'
    MAP_PATH = './data/maps/no_bg/no_bg_result.png'
    MAP_BG_PATH = 'data/maps/bg/bg_result.png'
    RESCALED_MAP_PATH = 'data/maps/no_bg/rescaled_map_1_pixel_per_{scale}_meter.png'
    RESCALED_BG_MAP_PATH = 'data/maps/bg/rescaled_map_1_pixel_per_{scale}_meter.png'
    GEOJSON_PATH = './data/geojson/export-2.geojson'
    BUILDINGS_GEOJSON_PATH = './data/geojson/buildings.geojson'
    MAP_BG_HTML_FULL_PATH = '/Users/shlomo/Desktop/reps/604/data/map_bg.html'
    MAP_HTML_FULL_PATH = '/Users/shlomo/Desktop/reps/604/data/map_no_bg.html'

class BatterySpec:
    VOLTAGE = 3.7
    CAPACITY = 3000  # in mAh


class SmallDroneDefaults:
    BATTERY = BatterySpec.CAPACITY
    MAX_SPEED = 8
    MAX_VERTICAL_SPEED = 3
    MAX_HEIGHT = 400
    MAX_DISTANCE = 1000


class MapConsts:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 700
    MAP_WIDTH = 5000
    MAP_HEIGHT = 2000
    MAP_PATH = './data/NewYorkMap.jpg'


class EnvironmentConsts:
    DRONES_CONTROL = 0
    MAP_CONTROL = 1
    CHOOSE_DRONE = 2
    FOCUS_DRONE = 3
    MODES_LIST = [DRONES_CONTROL, MAP_CONTROL, CHOOSE_DRONE, FOCUS_DRONE]


# def update_map_shape(path):
#     Consts.MAP_IMG_PATH = path
#
#     map_img.save(path)

# def generate_map(path):
#     map_img = Image.new('RGB', (width, height), color='white')
#     map_img.save(path)
