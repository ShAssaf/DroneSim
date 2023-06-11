class Consts:
    BigDroneSize = 10
    SmallDroneSize = 100
    MAP_IMG_PATH = None
    MAX_RANGE_FOR_COLOR = 255

    # default drones

    X = 0
    Y = 1
    Z = 2


DEBUG = True  # Set this flag to True to enable debug mode


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
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480
    MAP_WIDTH = 5000
    MAP_HEIGHT = 2000
    MAP_PATH = '../../data/NewYorkMap.jpg'


class EnvironmentConsts:
    DRONES_CONTROL = 0
    MAP_CONTROL = 1
    CHOOSE_DRONE = 2
    MODES_LIST = [DRONES_CONTROL, MAP_CONTROL, CHOOSE_DRONE]
