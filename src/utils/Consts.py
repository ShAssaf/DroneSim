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


DEBUG = False  # Set this flag to True to enable debug mode
MANUAL_DRONE = True

class BatterySpec:
    VOLTAGE = 3.7
    CAPACITY = 3000  # in mAh


class SmallDroneDefaults:
    BATTERY = BatterySpec.CAPACITY
    MAX_SPEED = 8
    MAX_VERTICAL_SPEED = 3
    MAX_HEIGHT = 400


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

def generate_map(path):
    map_img = Image.new('RGB', (width, height), color='white')
    map_img.save(path)