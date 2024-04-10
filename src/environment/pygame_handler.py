import pygame

from src.drone.drone_agent import DroneAgent
from src.drone.misson_control import Mission
from src.utils.Consts import Consts, MapConsts, EnvironmentConsts, MANUAL_DRONE, Paths
from src.utils.map_obj import MapObject
from src.utils.util_classes import debug_print, create_scaled_maps, ThreeDVector
imitate = False


class PygameHandler:
    def __init__(self, drones_list):
        create_scaled_maps()
        pygame.init()  #
        self.drones = drones_list
        # self.add_drone(len(self.drones))
        self.FONT = pygame.font.Font('freesansbold.ttf', Consts.FONT_SIZE)
        self.clock = pygame.time.Clock()
        self.fps = 120
        self.running = True
        self.map_object = MapObject(MapConsts.MAP_PATH)
        self.window = pygame.display.set_mode((MapConsts.SCREEN_WIDTH, MapConsts.SCREEN_HEIGHT))
        self.map_surface = pygame.image.load(self.map_object.path)
        self.viewport_surface = pygame.Surface((MapConsts.SCREEN_WIDTH, MapConsts.SCREEN_HEIGHT))

        # Set up the initial position of the viewport
        self.viewport_x = 0
        self.viewport_y = 0
        self.zoom_factor = 1

        # Set up the player's movement speed
        self.step_size = 80

        # modes
        self.mode = EnvironmentConsts.DRONES_CONTROL
        self.input_string = ""
        self.chosen_drone_index = 0

        # attributes

        pygame.display.set_caption("drone simulator")

        # self.rl = RLController(self.drones[self.chosen_drone_index])

    def start_simulation(self):
        while self.running:
            # self.clock.tick(self.fps)
            self.handle_events()
            self.draw_map()
            self.draw_on_screen()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.change_modes(event)
                if event.key == pygame.K_a:
                    self.add_drone(len(self.drones))
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
                        self.mode = EnvironmentConsts.DRONES_CONTROL
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

        # zoom in/out
        # Update the viewport size and position based on the zoom level
        # zoom_level = self.zoom_factor
        if event.key == pygame.K_x or event.key == pygame.K_z:
            screen_center = (self.viewport_x + MapConsts.SCREEN_WIDTH / 2,
                             self.viewport_y + MapConsts.SCREEN_HEIGHT / 2)
            if event.key == pygame.K_x:
                if self.zoom_factor < 8:
                    self.zoom_factor = int(self.zoom_factor * 2)
                    screen_center = (self.viewport_x * 2 + MapConsts.SCREEN_WIDTH / 2,
                                     self.viewport_y * 2 + MapConsts.SCREEN_HEIGHT / 2)
            elif event.key == pygame.K_z:
                if self.zoom_factor > 1:
                    self.zoom_factor = int(self.zoom_factor / 2)
                    screen_center = (self.viewport_x / 2 + MapConsts.SCREEN_WIDTH / 2,
                                     self.viewport_y / 2 + MapConsts.SCREEN_HEIGHT / 2)
            self.map_surface = pygame.image.load(f'{Paths.TMP}/scaled_map_{self.zoom_factor}.png')
            self.viewport_x = screen_center[0]
            self.viewport_y = screen_center[1]
            self.map_object.MAP_WIDTH = self.map_surface.get_width()
            self.map_object.MAP_HEIGHT = self.map_surface.get_height()

        # Add boundaries to the viewport, so it doesn't go beyond the edges of the map.osm
        if self.viewport_x < 0:
            self.viewport_x = 0
        elif self.viewport_x > self.map_object.MAP_WIDTH - MapConsts.SCREEN_WIDTH:
            self.viewport_x = self.map_object.MAP_WIDTH - MapConsts.SCREEN_WIDTH
        if self.viewport_y < 0:
            self.viewport_y = 0
        elif self.viewport_y > self.map_object.MAP_HEIGHT - MapConsts.SCREEN_HEIGHT:
            self.viewport_y = self.map_object.MAP_HEIGHT - MapConsts.SCREEN_HEIGHT

    def handle_drones_control(self, event):
        if imitate:
            if event.key == pygame.K_UP:
                self.drones[self.chosen_drone_index].set_imitate(3)
            if event.key == pygame.K_DOWN:
                self.drones[self.chosen_drone_index].set_imitate(2)
            if event.key == pygame.K_LEFT:
                self.drones[self.chosen_drone_index].set_imitate(1)
            if event.key == pygame.K_RIGHT:
                self.drones[self.chosen_drone_index].set_imitate(0)
        else:
            if event.key == pygame.K_UP:
                self.drones[self.chosen_drone_index].accelerate(0, -1, 0)
            if event.key == pygame.K_DOWN:
                self.drones[self.chosen_drone_index].accelerate(0, 1, 0)
            if event.key == pygame.K_LEFT:
                self.drones[self.chosen_drone_index].accelerate(-1, 0, 0)
            if event.key == pygame.K_RIGHT:
                self.drones[self.chosen_drone_index].accelerate(1, 0, 0)
            if event.key == pygame.K_z:
                self.drones[self.chosen_drone_index].accelerate(0, 0, 1)
            if event.key == pygame.K_x:
                self.drones[self.chosen_drone_index].accelerate(0, 0, -1)
            if event.key == pygame.K_KP8:
                self.drones[self.chosen_drone_index].accelerate2(0)
            if event.key == pygame.K_KP2:
                self.drones[self.chosen_drone_index].accelerate2(1)
            if event.key == pygame.K_KP4:
                self.drones[self.chosen_drone_index].turn_to(1)
            if event.key == pygame.K_KP6:
                self.drones[self.chosen_drone_index].turn_to(0)

    def draw_map(self):
        # Blit a portion of the map.osm surface onto the viewport surface, based on the current position of the viewport
        if self.mode == EnvironmentConsts.FOCUS_DRONE:
            x = self.drones[self.chosen_drone_index].last_location.x*self.zoom_factor - MapConsts.SCREEN_WIDTH / 2
            y = self.drones[self.chosen_drone_index].last_location.y*self.zoom_factor - MapConsts.SCREEN_HEIGHT / 2
            if x < 0:
                x = 0
            elif x > self.map_object.MAP_WIDTH - MapConsts.SCREEN_WIDTH:
                x = self.map_object.MAP_WIDTH - MapConsts.SCREEN_WIDTH
            if y < 0:
                y = 0
            elif y > self.map_object.MAP_HEIGHT - MapConsts.SCREEN_HEIGHT:
                y = self.map_object.MAP_HEIGHT - MapConsts.SCREEN_HEIGHT
            self.viewport_x = x
            self.viewport_y = y
        self.viewport_surface.blit(self.map_surface, (0, 0),
                                   (self.viewport_x, self.viewport_y, MapConsts.SCREEN_WIDTH, MapConsts.SCREEN_HEIGHT))

    def draw_status(self):
        # Draw the status text
        status_text = f"drone {self.chosen_drone_index} :\n" + \
                      f"position x: {int(self.drones[self.chosen_drone_index].last_location.x)}" + \
                      f" y: {int(self.drones[self.chosen_drone_index].last_location.y)}" + \
                      f" z: {int(self.drones[self.chosen_drone_index].last_location.z)}\n" + \
                      f" speed x : {int(self.drones[self.chosen_drone_index].last_velocity.x)}" + \
                      f" y : {int(self.drones[self.chosen_drone_index].last_velocity.y)}" + \
                      f" z : {int(self.drones[self.chosen_drone_index].last_velocity.z)}\n" + \
                      f" battery : {int(self.drones[self.chosen_drone_index].last_battery_status)}\n" + \
                      f" target vector x :{int(self.drones[self.chosen_drone_index].get_target_vector()[0])}" + \
                      f" y :{int(self.drones[self.chosen_drone_index].get_target_vector()[1])}\n" + \
                      f" drones : {len(self.drones)}"
        # Split the text into lines
        lines = status_text.split('\n')

        # Iterate over the lines
        for i, line in enumerate(lines):
            # Render each line separately
            line_surface = self.FONT.render(line, True, (255, 255, 255), (0, 0, 0))
            self.viewport_surface.blit(line_surface, (10, i * 15))

    def draw_on_screen(self):
        if (MANUAL_DRONE):
            self.draw_map()
            self.draw_drones()
            self.draw_status()
            self.draw_menu()
            self.draw_heat_legend()
            self.window.blit(self.viewport_surface, (0, 0))
            pygame.display.update()

    def draw_menu(self):
        menu_text = ["a: add drone",
                     "f: focus drone",
                     "arrow keys: move",
                     "space: map control",
                     "c+num+Entr: choose drone"]
        for i in range(5):
            menu_surface = self.FONT.render(menu_text[i], True, (255, 255, 255), (0, 0, 0))
            self.viewport_surface.blit(menu_surface, (0, MapConsts.SCREEN_HEIGHT - Consts.FONT_SIZE * (5 - i)))

    def draw_heat_legend(self):
        legend_text = ["-0",
                       "0",
                       "255",
                       "max",
                       "max+"]
        legend_color = [(0, 0, 0), (255, 0, 0), (255, 255, 0), (255, 255, 255), (0, 0, 0)]
        for i in range(5):
            legend_surface = self.FONT.render(legend_text[i], True, (0, 190, 190), legend_color[i])
            self.viewport_surface.blit(legend_surface, (0, MapConsts.SCREEN_HEIGHT - 70 - (Consts.FONT_SIZE * (5 - i))))

    def draw_drones(self):
        for idx in range(len(self.drones)):
            drone = self.drones[idx]
            # if not drone.is_learning:
            # drone.update()
            drone.get_location()
            drone.get_velocity()
            self.drones[idx] = drone
            drone.check_in_viewport(self.viewport_x, self.viewport_y, self.zoom_factor)
            if drone.in_viewport:
                drone.adjust_drone_color(drone.last_location.z)
                pygame.draw.circle(surface=self.viewport_surface, color=(drone.color.r, drone.color.g, drone.color.b),
                                   radius=Consts.SmallDroneSize,
                                   center=(drone.last_location.x * self.zoom_factor - self.viewport_x,
                                           drone.last_location.y * self.zoom_factor - self.viewport_y))
                drone.adjust_drone_color(drone.last_location.z)

        debug_print(
            f"drone{self.chosen_drone_index} "
            f"position x: {int(self.drones[self.chosen_drone_index].last_location.x)}" +
            f" y: {int(self.drones[self.chosen_drone_index].last_location.y)}" +
            f" z: {int(self.drones[self.chosen_drone_index].last_location.z)}" +
            f" speed x : {int(self.drones[self.chosen_drone_index].last_velocity.x)}" +
            f" y : {int(self.drones[self.chosen_drone_index].last_velocity.y)}" +
            f" z : {int(self.drones[self.chosen_drone_index].last_velocity.z)}" +
            f" battery : {int(self.drones[self.chosen_drone_index].last_battery_status)}")

    # @staticmethod
    def add_drone(len_drones):
        # todo: add drone in subprocess
        a = DroneAgent(name=f"drone{len_drones}")
        a.drone.mission_control.set_mission(Mission(a.drone.get_location(), ThreeDVector(1000, 2500, 0)))
        a.drone.mission_control.mission_start()
