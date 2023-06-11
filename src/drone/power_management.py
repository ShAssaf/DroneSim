from enum import Enum
from src.utils.Consts import BatterySpec
from src.utils.util_classes import ThreeDVector
from typing import Optional

class BatteryModes(Enum):
    performance = 1
    conservation = 2
    emergency = 3


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
    weight = 1
    weight = weight + (abs(velocity_vector.x) * 0.01)
    weight = weight + (abs(velocity_vector.y) * 0.01)
    weight = weight +(velocity_vector.z * 0.03 if(velocity_vector.z<0) else velocity_vector.z * 0.01)

    # calculate the power consumption of the drone according to its mode
    if __mode == BatteryModes.performance:
        battery_consumption_rate = battery_consumption_rate * weight + 0.2
    elif __mode == BatteryModes.conservation:
        battery_consumption_rate = battery_consumption_rate * weight
    elif __mode == BatteryModes.emergency:
        battery_consumption_rate = battery_consumption_rate * weight - 0.2
    else:
        raise ValueError("The mode is not defined")

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
