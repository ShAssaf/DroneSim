from typing import Type

import pygame

from src.RL.RL_PG import RLController
from src.drone.Drone import Drone
from src.environment.DroneObj import SmallDroneSimObj
from src.utils.Consts import Consts, MapConsts, EnvironmentConsts, MANUAL_DRONE
from src.utils.util_classes import InternalGPS, debug_print


class PygameHandler:
    def __init__(self, drones_list):
        pygame.init()  #
        self.FONT = pygame.font.Font('freesansbold.ttf', Consts.FONT_SIZE)
        self.clock = pygame.time.Clock()
        self.fps = 120
        self.running = True
        self.window = pygame.display.set_mode((MapConsts.SCREEN_WIDTH, MapConsts.SCREEN_HEIGHT))
        self.map_surface = pygame.image.load(MapConsts.MAP_PATH)
        # todo: add map.osm image -> change Consts.MAP_IMG_PATH and scale if needed
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

        # attributes
        self.drones = drones_list
        pygame.display.set_caption("drone simulator")

        self.rl = RLController(self.drones[self.chosen_drone_index])

    def start_simulation(self):

        while self.running:
            #self.clock.tick(self.fps)
            self.handle_events()
            self.draw_map()
            self.draw_on_screen()
            self.draw_drones()

    def handle_events(self):
        if not MANUAL_DRONE:
            # TODO: not good enough
            self.rl.move()

            # self.rl.move2()
            # self.rl.set_drone(self.drones[self.chosen_drone_index])
            # self.chosen_drone_index = (self.chosen_drone_index + 1) % self.drones.__len__()
            # print("chosen drone index: ", self.chosen_drone_index
            #       ,"drone velocity: ", self.drones[self.chosen_drone_index].gps.velocity.x, " "
            #       ,self.drones[self.chosen_drone_index].gps.velocity.y, " ",
            #        self.drones[self.chosen_drone_index].gps.velocity.z, " "
            #       ,"drone location: ", self.drones[self.chosen_drone_index].gps.location.x, " "
            #       ,self.drones[self.chosen_drone_index].gps.location.y, " "
            #       ,self.drones[self.chosen_drone_index].gps.location.z)

        for event in pygame.event.get():
            # pygame.time.delay(100)
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False
            elif event.type == pygame.KEYDOWN or event.type == self.rl.arrow_key_event:
                self.change_modes(event)
                if event.key == pygame.K_a:
                    self.add_drone()
                if self.mode == EnvironmentConsts.MAP_CONTROL:
                    self.handle_map_control(event)
                elif self.mode == EnvironmentConsts.CHOOSE_DRONE:
                    self.handle_choose_mode(event)
                elif self.mode == EnvironmentConsts.DRONES_CONTROL:
                    self.handle_drones_control(event)
                elif self.mode == EnvironmentConsts.FOCUS_DRONE:
                    self.handle_drones_control(event)

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
        elif event.key == pygame.K_f:
            self.mode = EnvironmentConsts.FOCUS_DRONE

    def handle_choose_mode(self, event):
        if self.mode == EnvironmentConsts.CHOOSE_DRONE and event.unicode.isdigit():
            self.input_string += event.unicode  # Append the digit to the input string
        elif self.mode == EnvironmentConsts.CHOOSE_DRONE and (
                event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
            if self.input_string:  # Check if the input string is not empty
                try:
                    input_number = int(self.input_string)  # Convert the input string to an integer
                    if 0 <= input_number <= len(self.drones) - 1:
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

        # Add boundaries to the viewport, so it doesn't go beyond the edges of the map.osm
        if self.viewport_x < 0:
            self.viewport_x = 0
        elif self.viewport_x > MapConsts.MAP_WIDTH - MapConsts.SCREEN_WIDTH:
            self.viewport_x = MapConsts.MAP_WIDTH - MapConsts.SCREEN_WIDTH
        if self.viewport_y < 0:
            self.viewport_y = 0
        elif self.viewport_y > MapConsts.MAP_HEIGHT - MapConsts.SCREEN_HEIGHT:
            self.viewport_y = MapConsts.MAP_HEIGHT - MapConsts.SCREEN_HEIGHT

    def handle_drones_control(self, event):
        if event.key == pygame.K_UP:
            self.drones[self.chosen_drone_index].motion_controller.accelerate(0, -1, 0)
        if event.key == pygame.K_DOWN:
            self.drones[self.chosen_drone_index].motion_controller.accelerate(0, 1, 0)
        if event.key == pygame.K_LEFT:
            self.drones[self.chosen_drone_index].motion_controller.accelerate(-1, 0, 0)
        if event.key == pygame.K_RIGHT:
            self.drones[self.chosen_drone_index].motion_controller.accelerate(1, 0, 0)
        if event.key == pygame.K_z:
            self.drones[self.chosen_drone_index].motion_controller.accelerate(0, 0, 1)
        if event.key == pygame.K_x:
            self.drones[self.chosen_drone_index].motion_controller.accelerate(0, 0, -1)

    def draw_map(self):
        # Blit a portion of the map.osm surface onto the viewport surface, based on the current position of the viewport
        if self.mode == EnvironmentConsts.FOCUS_DRONE:
            self.viewport_x = self.drones[self.chosen_drone_index].gps.location.x - MapConsts.SCREEN_WIDTH / 2
            self.viewport_y = self.drones[self.chosen_drone_index].gps.location.y - MapConsts.SCREEN_HEIGHT / 2
        self.viewport_surface.blit(self.map_surface, (0, 0),
                                   (self.viewport_x, self.viewport_y, MapConsts.SCREEN_WIDTH, MapConsts.SCREEN_HEIGHT))

    def draw_status(self):
        # Draw the status text
        status_text = f"drone {self.chosen_drone_index} : " + \
                      f"position x: {self.drones[self.chosen_drone_index].gps.location.x}" + \
                      f" y: {self.drones[self.chosen_drone_index].gps.location.y}" + \
                      f" z: {self.drones[self.chosen_drone_index].gps.location.z}" + \
                      f" speed x : {self.drones[self.chosen_drone_index].get_speed().x}" + \
                      f" y : {self.drones[self.chosen_drone_index].get_speed().y}" + \
                      f" z : {self.drones[self.chosen_drone_index].get_speed().z}" + \
                      f" battery : {int(self.drones[self.chosen_drone_index].power_controller.get_battery_percentage())}"\
                      + f" drones : {len(self.drones)}"
        status_surface = self.FONT.render(status_text, True, (255, 255, 255), (0, 0, 0))
        self.viewport_surface.blit(status_surface, (0, 0))

    def draw_on_screen(self):
        if (MANUAL_DRONE):
            self.draw_status()
            self.draw_menu()
            self.draw_heat_legend()

    def draw_menu(self):
        menu_text = ["a: add drone",
                     "f: focus drone",
                     "arrow keys: move",
                     "space: map control",
                     "c+num+Entr: choose drone"]
        for i in range(5):
            menu_surface = self.FONT.render(menu_text[i], True, (255, 255, 255), (0, 0, 0))
            self.viewport_surface.blit(menu_surface, (0, MapConsts.SCREEN_HEIGHT - Consts.FONT_SIZE*(5-i)))

    def draw_heat_legend(self):
        legend_text = ["-0",
                     "0",
                     "255",
                     "max",
                     "max+"]
        legend_color = [(0, 0, 0), (255,0,0), (255,255,0), (255,255,255), (0,0,0)]
        for i in range(5):
            legend_surface = self.FONT.render(legend_text[i], True, (0, 190, 190), legend_color[i])
            self.viewport_surface.blit(legend_surface, (0, MapConsts.SCREEN_HEIGHT - 70 - (Consts.FONT_SIZE * (5 - i))))

    def draw_drones(self):
        for drone in self.drones:
            drone.calculate_gps()
            drone.calculate_power_consumption()
            drone.check_in_viewport(self.viewport_x, self.viewport_y)
            drone.adjust_drone_color(drone.get_gps().z)
            drone.draw(self.viewport_surface, self.viewport_x, self.viewport_y)
        self.window.blit(self.viewport_surface, (0, 0))
        pygame.display.update()

        debug_print(
            f"drone{self.chosen_drone_index} "
            f"position x: {self.drones[self.chosen_drone_index].gps.location.x}" +
            f" y: {self.drones[self.chosen_drone_index].gps.location.y}" +
            f" z: {self.drones[self.chosen_drone_index].gps.location.z}" +
            f" speed x : {self.drones[self.chosen_drone_index].get_speed().x}" +
            f" y : {self.drones[self.chosen_drone_index].get_speed().y}" +
            f" z : {self.drones[self.chosen_drone_index].get_speed().z}" +
            f" battery : {self.drones[self.chosen_drone_index].power_controller.get_battery_percentage()}")

    def add_drone(self):
        self.drones.append(SmallDroneSimObj(name=f"drone{len(self.drones)}", gps=InternalGPS()))
