import pygame
import random
from pygame.locals import *


class RLController:
    def __init__(self,drone):
        # Create a custom event for the arrow key
        self.arrow_key_event = pygame.USEREVENT + 1

        # Set the event type for arrow key events
        self.key_arrow_up = pygame.event.Event(self.arrow_key_event, {'key': K_UP})
        self.key_arrow_down = pygame.event.Event(self.arrow_key_event, {'key': K_DOWN})
        self.key_arrow_left = pygame.event.Event(self.arrow_key_event, {'key': K_LEFT})
        self.key_arrow_right = pygame.event.Event(self.arrow_key_event, {'key': K_RIGHT})
        self.key_z = pygame.event.Event(self.arrow_key_event, {'key': K_z})
        self.kew_x = pygame.event.Event(self.arrow_key_event, {'key': K_x})
        self.kew_a = pygame.event.Event(self.arrow_key_event, {'key': K_a})

        self.drone = drone

        self.temp = 1

    def set_drone(self, drone):
        self.drone = drone

    def move_north(self):
        pygame.event.post(self.key_arrow_up)

    def move_south(self):
        pygame.event.post(self.key_arrow_down)

    def move_east(self):
        pygame.event.post(self.key_arrow_left)

    def move_west(self):
        pygame.event.post(self.key_arrow_right)

    def move_up(self):
        pygame.event.post(self.key_z)

    def move_down(self):
        pygame.event.post(self.kew_x)

    def add_drone(self):
        pygame.event.post(self.kew_a)

    # TODO: change score method
    def get_score(self):
        if self.drone.get_gps().x < 0 or self.drone.get_gps().y < 0:
            print("out of bounds")
        if self.drone.get_gps().z < 0:
            print("crash")
        elif self.drone.get_gps().z > 500:
            print("out of bounds")

#TODO: change functions (move & move2) names to a more relevant name

    def move2(self):
        if self.temp == 1:
            self.add_drone()
            self.temp = 0
        else:
            self.move()

    def move(self):
        self.get_score()
        direction = random.randint(0, 5)
        if direction == 0:
            self.move_north()
        elif direction == 1:
            self.move_south()
        elif direction == 2:
            self.move_east()
        elif direction == 3:
            self.move_west()
        elif direction == 4:
            self.move_up()
        elif direction == 5:
            self.move_down()


