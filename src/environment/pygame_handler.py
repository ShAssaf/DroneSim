from typing import Type

import pygame

from src.drone.Drone import Drone
from src.environment.DroneObj import SmallDroneSimObj
from src.utils.Consts import MapConsts, EnvironmentConsts
from src.utils.util_classes import InternalGPS, debug_print


class PygameHandler:
    def __init__(self):
        pygame.init()  #
        self.FONT = pygame.font.Font('freesansbold.ttf', 12)
        self.clock = pygame.time.Clock()
        self.fps = 120
        self.running = True
        self.window = pygame.display.set_mode((MapConsts.SCREEN_WIDTH, MapConsts.SCREEN_HEIGHT))
        self.map_surface = pygame.image.load(MapConsts.MAP_PATH)
        # todo: add map image -> change Consts.MAP_IMG_PATH and scale if needed
        self.viewport_surface = pygame.Surface((MapConsts.SCREEN_WIDTH, MapConsts.SCREEN_HEIGHT))

        # Set up the initial position of the viewport
        self.viewport_x = 0
        self.viewport_y = 0

        # Set up the player's movement speed
        self.step_size = 80

        # modes
        self.mode = EnvironmentConsts.DRONES_CONTROL
        self.input_string = ""
        self.chosen_drone_index = 0

        pygame.display.set_caption("drone simulator")

    def start_simulation(self, drones: list):
        while self.running:
            #self.clock.tick(self.fps)
            self.handle_events(drones)
            self.draw_map()
            self.draw_drones(drones)
        return drones

    def handle_events(self, drones):
        for event in pygame.event.get():
            #pygame.time.delay(100)
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.change_modes(event)
                if event.key == pygame.K_a:
                    drones = add_drone(drones_list=drones)
                if self.mode == EnvironmentConsts.MAP_CONTROL:
                    self.handle_map_control(event)
                elif self.mode == EnvironmentConsts.CHOOSE_DRONE:
                    self.handle_choose_mode(event, len(drones))
                elif self.mode == EnvironmentConsts.DRONES_CONTROL:
                    drones = self.handle_drones_control(event, drones)

        return drones

    def change_modes(self, event):
        if event.key == pygame.K_SPACE:
            if self.mode != EnvironmentConsts.MAP_CONTROL:
                self.mode = EnvironmentConsts.MAP_CONTROL
            else:
                self.mode = EnvironmentConsts.DRONES_CONTROL
        elif event.key == pygame.K_c:
            if self.mode != EnvironmentConsts.CHOOSE_DRONE:
                self.mode = EnvironmentConsts.CHOOSE_DRONE
                self.input_string = ""  # Reset the input string
            else:
                self.mode = EnvironmentConsts.DRONES_CONTROL

    def handle_choose_mode(self, event, drones_len):
        if self.mode == EnvironmentConsts.CHOOSE_DRONE and event.unicode.isdigit():
            self.input_string += event.unicode  # Append the digit to the input string
        elif self.mode == EnvironmentConsts.CHOOSE_DRONE and (
                event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
            if self.input_string:  # Check if the input string is not empty
                try:
                    input_number = int(self.input_string)  # Convert the input string to an integer
                    if 0 <= input_number <= drones_len - 1:
                        self.chosen_drone_index = input_number
                except ValueError:
                    pass
            debug_print("Chosen drone index: " + str(self.chosen_drone_index))

    def handle_map_control(self, event):
        if event.key == pygame.K_LEFT:
            self.viewport_x -= self.step_size
        if event.key == pygame.K_RIGHT:
            self.viewport_x += self.step_size
        if event.key == pygame.K_UP:
            self.viewport_y -= self.step_size
        if event.key == pygame.K_DOWN:
            self.viewport_y += self.step_size

        # Add boundaries to the viewport, so it doesn't go beyond the edges of the map
        if self.viewport_x < 0:
            self.viewport_x = 0
        elif self.viewport_x > MapConsts.MAP_WIDTH - MapConsts.SCREEN_WIDTH:
            self.viewport_x = MapConsts.MAP_WIDTH - MapConsts.SCREEN_WIDTH
        if self.viewport_y < 0:
            self.viewport_y = 0
        elif self.viewport_y > MapConsts.MAP_HEIGHT - MapConsts.SCREEN_HEIGHT:
            self.viewport_y = MapConsts.MAP_HEIGHT - MapConsts.SCREEN_HEIGHT

    def handle_drones_control(self, event, drones):
        if event.key == pygame.K_UP:
            drones[self.chosen_drone_index].motion_controller.accelerate(0, -1, 0)
        if event.key == pygame.K_DOWN:
            drones[self.chosen_drone_index].motion_controller.accelerate(0, 1, 0)
        if event.key == pygame.K_LEFT:
            drones[self.chosen_drone_index].motion_controller.accelerate(-1, 0, 0)
        if event.key == pygame.K_RIGHT:
            drones[self.chosen_drone_index].motion_controller.accelerate(1, 0, 0)
        if event.key == pygame.K_z:
            drones[self.chosen_drone_index].motion_controller.accelerate(0, 0, 1)
        if event.key == pygame.K_x:
            drones[self.chosen_drone_index].motion_controller.accelerate(0, 0, -1)
        return drones

    def draw_map(self):
        # Blit a portion of the map surface onto the viewport surface, based on the current position of the viewport
        self.viewport_surface.blit(self.map_surface, (0, 0),
                                   (self.viewport_x, self.viewport_y, MapConsts.SCREEN_WIDTH, MapConsts.SCREEN_HEIGHT))

    def draw_drones(self, drones):
        for drone in drones:
            drone.calculate_gps()
            drone.check_in_viewport(self.viewport_x, self.viewport_y)
            drone.draw(self.viewport_surface, self.viewport_x, self.viewport_y)
        self.window.blit(self.viewport_surface, (0, 0))
        pygame.display.update()

        debug_print(
            f"drone{self.chosen_drone_index} "
            f"position x: {drones[self.chosen_drone_index].gps.location.x}" +
            f" y: {drones[self.chosen_drone_index].gps.location.y}" +
            f" z: {drones[self.chosen_drone_index].gps.location.z}" +
            f" speed x : {drones[self.chosen_drone_index].get_speed().x}" +
            f" y : {drones[self.chosen_drone_index].get_speed().y}" +
            f" z : {drones[self.chosen_drone_index].get_speed().z}" +
            f" battery : {drones[self.chosen_drone_index].power_controller.get_battery_percentage()}")


def add_drone(drone: Type[Drone] = None, drones_list: list = None):
    if drone is None:
        drone = SmallDroneSimObj(name=f"drone{len(drones_list)}", gps=InternalGPS())
    drones_list.append(drone)
    return drones_list
