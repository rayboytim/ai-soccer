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
            *[BoxElement(Colors.lightgray, _+offset-1, 235, 10, 250, 2) for _ in range(9, 97, 8)], # vertical netting
            *[BoxElement(Colors.lightgray, offset, _, 105, 10, 2) for _ in range(243, 473, 8)], # horizontal netting
            BoxElement(Colors.white, offset, 235, 105, 250, 5) # frame
        ]

        # draw each part of the goal
        # will be rendered on top of the player
        for e in elements:
            e.draw(surface)

    # rect for the area where a goal is scored
    def getRect(self):
        if self.team == "red":
            return pygame.Rect(5, 240, 100, 240)
        elif self.team == "blue":
            return pygame.Rect(1175, 240, 100, 240)
    
    # dict of rects for the area where entities will collide with the goal
    def getCollisionRects(self):
        if self.team == "red":
            return {
                "back": pygame.Rect(0, 235, 5, 250),
                "top": pygame.Rect(0, 235, 105, 5),
                "bottom": pygame.Rect(0, 480, 105, 5),
            }
        elif self.team == "blue":
            return {
                "back": pygame.Rect(1275, 235, 5, 250),
                "top": pygame.Rect(1175, 235, 105, 5),
                "bottom": pygame.Rect(1175, 480, 105, 5),
            }