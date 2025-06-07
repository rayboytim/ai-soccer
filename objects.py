# object.py
# rayboytim 6/3/25

from abc import ABC, abstractmethod
import pygame

from gameutils import *

# abstract object class
class Object(ABC):
    def __init__(self, x: int = 0, y: int = 0):

        # set position
        self.pos = Vector2(x, y)

        # if true, render object on screen
        self.visible = True

    # abstract methods

    @abstractmethod
    def draw(self, surface):
        # passes object info and draws the object onto the screen
        pass

    @abstractmethod
    def getRect(self) -> pygame.Rect:
        # gets the bounding box of the object
        pass

# moveable object abstract class
class Entity(Object):
    
    # amount that velocity slows down per frame
    slowdownRate = 0.95

    # amount that z velocity loses per bounce
    bounceLossRate = 0.4

    # rate that zVel will decrease
    gravity = 0.12

    # amount that entities will be distorted based on their height
    distortion = 1
    radiusDistortion = 0.25

    def __init__(self, height: int = 0, x: int = 0, y: int = 0):
        super().__init__(x, y)

        # movement vars
        self.angle = Angle(0)
        self.speed = 0

        # additional velocity vars
        self.vel = Vector2(0,0)

        # height vars
        self.radius = self.minRadius
        self.height = height
        self.zVel = 0

        from shadow import Shadow

        # shadow
        self.shadow = Shadow(self)

        # force from collision
        self.pushVector = Vector2(0,0)

    def draw(self, surface):
        pass

    # moves the entity based on its angle and speed
    def updatePos(self):
        
        # calculate 2d velocity, except for Player class
        from player import Player
        if not isinstance(self, Player):
            vel = Vector2(
                self.angle.x * self.speed,
                self.angle.y * self.speed
            )
        else:
            # player movement
            vel = self.moveVector
            self.moveVector *= Entity.slowdownRate

        # collision vectors
        if hasattr(self, "pushVector"):
            vel += self.pushVector

        if hasattr(self, "collideVector"):
            vel += self.collideVector

        if hasattr(self, "boundCollideVector"):
            vel += self.boundCollideVector

        # move the entity
        self.pos.x += vel.x
        self.pos.y += vel.y

        # slow the velocity
        if self.height <= 0:
            self.speed *= Entity.slowdownRate
            if self.speed < 0.1:
                self.speed = 0

        # vertical velocity

        # change z velocity based on gravity
        if self.height > 0:
            self.zVel -= Entity.gravity
        
        # make entity bounce if it hits ground
        if self.height <= 0 and self.zVel < 0:
            self.zVel *= -1 * Entity.bounceLossRate
            self.height = 0

        # normalize height if z vel is low enough
        if abs(self.zVel) < 0.2 and self.height < 0.1:
            self.zVel = 0
            self.height = 0

        # change entity height based on z vel
        self.height += self.zVel

        # change the entity's radius based on its height
        self.radius = self.minRadius + self.height * Entity.radiusDistortion

    # test if two objects are intersecting
    def intersects(self, other):
        
        thisRect = self.getRect()
        otherRect = other.getRect()

        # conditions

        c1 = thisRect.x < otherRect.x + otherRect.width
        c2 = thisRect.x + thisRect.width > otherRect.x
        c3 = thisRect.y < otherRect.y + otherRect.height
        c4 = thisRect.height + thisRect.y > otherRect.y

        # height conditions, if other object does not have then ignore
        if hasattr(other, "height"):
            h1 = self.height <= other.minRadius + other.height
            h2 = other.height <= self.minRadius + self.height

            if c1 and c2 and c3 and c4 and h1 and h2:
                return True
            return False
        else:
            if c1 and c2 and c3 and c4:
                return True
            return False
        
    # intersect for when the rect is already defined
    def intersectsRect(self, other, otherRect: pygame.Rect):
        
        thisRect = self.getRect()

        # conditions

        c1 = thisRect.x < otherRect.x + otherRect.width
        c2 = thisRect.x + thisRect.width > otherRect.x
        c3 = thisRect.y < otherRect.y + otherRect.height
        c4 = thisRect.height + thisRect.y > otherRect.y

        # height conditions, if other object does not have then ignore
        if hasattr(other, "height"):
            h1 = self.height <= other.minRadius + other.height
            h2 = other.height <= self.minRadius + self.height

            if c1 and c2 and c3 and c4 and h1 and h2:
                return True
            return False
        else:
            if c1 and c2 and c3 and c4:
                return True
            return False