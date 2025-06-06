# map.py
# rayboytim 6/4/25

import pygame

from objects import *

# map element classes
# do not move and are always rendered first

class MapElement(Object):
    def __init__(self, x, y):
        super().__init__(x, y)

    @abstractmethod
    def draw(self, surface):
        pass

    def getRect(self):
        return super().getRect()

class BoxElement(MapElement):
    # x and y are the top left coordinate, w and h extend from there
    def __init__(self, color, x, y, w, h, thickness):
        super().__init__(x, y)

        self.color = color

        self.w = w
        self.h = h
        self.thickness = thickness

    def draw(self, surface):
        rect = pygame.Rect(self.pos.x, self.pos.y, self.w, self.h)

        info = (
            surface,
            self.color,
            rect,
            self.thickness
        )

        pygame.draw.rect(*info)

class CircleElement(MapElement):
    # x and y are the center
    def __init__(self, color, x, y, radius, w):
        super().__init__(x, y)

        self.color = color
        self.radius = radius
        self.w = w

    def draw(self, surface):
        info = (
            surface,
            self.color,
            self.pos.toTuple(),
            self.radius,
            self.w
        )

        pygame.draw.circle(*info)
    
class TextElement(MapElement):
    # text fonts
    fonts = {
        "largeRed": ("Arial", 44),
        "largeBlue": ("Arial", 44),
        "timer": ("Arial", 44),
        "gameNum": ("Arial", 44)
    }

    def __init__(self, text, font: str, color):
        self.text = text

        self.fontName = font
        self.font = pygame.font.SysFont(*TextElement.fonts[font], bold=True)

        self.color = color

        super().__init__(0,0)

    def draw(self, surface):
        info = (
            self.text,
            True,
            self.color
        )

        textRender = self.font.render(*info)

        # position text
        # red -> left, blue -> right
        if self.fontName == "largeRed":
            self.pos = Vector2(10, 0)

            surface.blit(textRender, self.pos.toTuple())

        elif self.fontName == "largeBlue":
            rect = textRender.get_rect()
            rect.topright = (1270, 0)

            surface.blit(textRender, rect)

        elif self.fontName == "timer":
            rect = textRender.get_rect()
            rect.center = (640, 24)

            surface.blit(textRender, rect)

        elif self.fontName == "gameNum":
            rect = textRender.get_rect()
            rect.center = (640, 696)

            surface.blit(textRender, rect)
    
    def getRect(self):
        pass
