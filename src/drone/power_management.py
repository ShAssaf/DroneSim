from enum import Enum
from src.utils.Consts import BatterySpec
from src.utils.util_classes import ThreeDVector
from typing import Optional

class BatteryModes(Enum):
    emergency = 0
    conservation = 1
    performance = 2

class BatteryWeights(Enum):
    twoD_movement = 2
    down = 3
    up = 4
    mode_wight = 5
    weight = 10

def power_consumption(velocity_vector: Optional[ThreeDVector], accelerate_vector, __mode, __battery):
    """this function calculates the power consumption of the drone according to the velocity vector and the mode"""
    # Calculate the power of the battery in watts
    # The power of the battery is calculated by the formula: P = U * I
    battery_power = BatterySpec.VOLTAGE * (__battery / 1000)
    # Convert the power to milliwatts (mW)
    battery_power_mw = battery_power * 1000
    # Calculate the battery consumption rate per second in milliwatt-seconds (mWs)
    battery_consumption_rate = battery_power_mw / 3600

    # Calculate the weight of the velocity vector for the power consumption
    weight = BatteryWeights.weight.value
    weight = weight + (abs(velocity_vector.x) * BatteryWeights.twoD_movement.value)
    weight = weight + (abs(velocity_vector.y) * BatteryWeights.twoD_movement.value)
    weight = weight + (velocity_vector.z * BatteryWeights.up.value if(velocity_vector.z < 0)
                       else velocity_vector.z * BatteryWeights.down.value)
    # calculate the power consumption of the drone according to its mode
    battery_consumption_rate = (battery_consumption_rate * weight) + __mode.value * BatteryWeights.mode_wight.value
    return battery_consumption_rate


class BatteryController:
    def __init__(self, mode=BatteryModes.conservation, battery_capacity=BatterySpec.CAPACITY):
        self.__battery_percentage = 100
        self.__mode = mode
        self.__battery_capacity = battery_capacity * 3600  # in mAh per second
        self.__max_battery_capacity = battery_capacity

    def set_mode(self, mode):
        self.__mode = mode

    def get_mode(self):
        return self.__mode

    def get_battery_percentage(self):
        return self.__battery_percentage

    def set_battery_percentage(self, percentage):
        self.__battery_percentage = percentage

    def get_battery_capacity(self):
        return self.__battery_capacity

    def set_battery_capacity(self, capacity):
        self.__battery_capacity = capacity

    def calculate_battery(self, velocity_vector, accelerate_vector=None):
        self.__battery_capacity -= power_consumption(velocity_vector, accelerate_vector, self.__mode, self.__max_battery_capacity)
        self.__battery_percentage = (self.__battery_capacity / (self.__max_battery_capacity * 3600)) * 100
