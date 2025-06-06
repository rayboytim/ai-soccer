# goal.py
# rayboytim 6/5/25

import pygame
from objects import *
from map import *

class Goal(Object):
    def __init__(self, team):

        # self.team is the side the goal is on
        # e.g. red team will score on blue goal

        self.team = team

        if team == "red":
            super().__init__(0, 235)
        elif team == "blue":
            super().__init__(1180, 235)

    def draw(self, surface):

        if self.team == "red":
            offset = 0
        elif self.team == "blue":
            offset = 1175

        elements = [
            *[BoxElement(Colors.lightgray, _+offset-1, 135, 10, 450, 2) for _ in range(9, 97, 8)], # vertical netting
            *[BoxElement(Colors.lightgray, offset, _, 105, 10, 2) for _ in range(135, 580, 8)], # horizontal netting
            BoxElement(Colors.white, offset, 135, 105, 450, 5) # frame
        ]

        # draw each part of the goal
        # will be rendered on top of the player
        for e in elements:
            e.draw(surface)

    # rect for the area where a goal is scored
    def getRect(self):
        if self.team == "red":
            return pygame.Rect(5, 140, 100, 440)
        elif self.team == "blue":
            return pygame.Rect(1175, 140, 100, 440)
    
    # dict of rects for the area where entities will collide with the goal
    def getCollisionRects(self):
        if self.team == "red":
            return {
                "back": pygame.Rect(0, 135, 5, 450),
                "top": pygame.Rect(0, 135, 105, 5),
                "bottom": pygame.Rect(0, 580, 105, 5),
            }
        elif self.team == "blue":
            return {
                "back": pygame.Rect(1275, 135, 5, 450),
                "top": pygame.Rect(1175, 135, 105, 5),
                "bottom": pygame.Rect(1175, 580, 105, 5),
            }