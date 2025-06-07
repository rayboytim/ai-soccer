# gameutils.py
# rayboytim 6/3/25

import math

# vector2 class
class Vector2():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # convert to tuple e.g. (0, 0)
    def toTuple(self) -> tuple:
        return (self.x, self.y)
    
    # normalize the vector
    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2)

        if length == 0:
            return Vector2(0, 0)

        newX = self.x / length
        newY = self.y / length
        
        return Vector2(newX, newY)
    
    # distance from origin
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
    
    # distance between two points
    def distance(self, other):
        dx = other.x - self.x
        dy = other.y - self.y

        return math.sqrt(dx**2 + dy**2)
    
    # add vectors
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y

        return Vector2(x, y)
    
    # subtract vectors
    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y

        return Vector2(x, y)
    
    # multiply vector by float
    def __mul__(self, mult):
        return Vector2(self.x * mult, self.y * mult)

    # divide vector by float
    def __truediv__(self, divisor):
        return Vector2(self.x / divisor, self.y / divisor)
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
# angle class
class Angle():
    # returns the angle between two objects
    @staticmethod
    def angleBetween(v1: Vector2, v2: Vector2):
        dist = v2 - v1
        
        angleRads = math.atan2(dist.y, dist.x)
        angle = math.degrees(angleRads)

        return Angle(angle)

    def __init__(self, angle: int):
        # angle values
        self.degrees = angle % 360 # used for manipulation
        self.rad = math.radians(self.degrees) # used for calculations

        # 2d trig values
        self.x = math.cos(self.rad)
        self.y = math.sin(self.rad)

    # add angles
    def __add__(self, other):
        return Angle(self.degrees + other.degrees)
    
    # subtract angles
    def __sub__(self, other):
        return Angle(self.degrees - other.degrees)
    
    def __str__(self):
        return f"{self.degrees:.2f}"

# colors library
class Colors():
    red = (255,64,64)
    green = (100,165,100)
    blue = (64,64,255)
    white = (255,255,255)
    lightgray = (245,245,245)
    gray = (200,200,200)
    black = (0,0,0)