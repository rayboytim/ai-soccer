# player.py
# rayboytim 6/3/25

import random
import math

from objects import *
from gameutils import *

# player class
class Player(Entity):

    # radius of player when they are on the ground
    minRadius = 30

    # multiplier for how fast player collisions occur
    collisionStiffness = 0.1

    walkSpeed = 5

    # ball hit multipliers
    speedMult = 1.75
    zVelMult = 0.1

    def __init__(self, name: str, team: str):
        self.name = name
        self.team = team

        # team info
        if team == "red":
            self.color = Colors.red
            super().__init__(0, 240, 360)
        elif team == "blue":
            self.color = Colors.blue
            super().__init__(0, 1040, 360)

        self.touchingBall = False

        # user controlled move vector
        self.moveVector = Vector2(0,0)

        # goal collision
        self.lastCollide = None
        self.collideVector = Vector2(0,0)

    def draw(self, surface):
        # calculate visual pos based on height
        # draws entity slightly towards the nearest corner of the screen when in the air
        visualX = self.pos.x + (self.height * (self.pos.x - 640) / 640 * Entity.distortion)
        visualY = self.pos.y + (self.height * (self.pos.y - 360) / 360 * Entity.distortion)

        info = (
            surface,
            self.color,
            self.getRect()
        )

        pygame.draw.rect(*info)

    def getRect(self) -> pygame.Rect:
        top = self.pos.x - Player.minRadius
        left = self.pos.y - Player.minRadius

        info = (top, left, Player.minRadius*2, Player.minRadius*2)

        return pygame.Rect(*info)

    def playerCollide(self, other):

        # if not colliding, reset push vectors
        if not self.intersects(other):
            self.pushVector = Vector2(0,0)
            other.pushVector = Vector2(0,0)
            return
        
        # get distance from other player
        diff = self.pos - other.pos
        dist = self.pos.distance(other.pos)

        # if too far away to actually be colliding, return
        if dist > 60:
            return

        # perfectly overlapping, push randomly
        if dist == 0:
            diff = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            dist = diff.distance()

        # normalize the distance vector
        diffNorm = diff / dist

        # find how much to push
        overlap = Player.minRadius * 2 - dist

        # push each player half the overlap distance away from each other
        pushVector = diffNorm * (overlap / 2) * Player.collisionStiffness

        # add to push vectors
        self.pushVector += pushVector
        other.pushVector -= pushVector

    # goal post collision
    def goalCollide(self, goal):
        playerRect = self.getRect()
        goalRects = goal.getCollisionRects()

        if self.lastCollide:
            if not self.intersectsRect(goal, self.lastCollide):
                self.lastCollide = None
                self.collideVector = Vector2(0,0)

        # collide with top of goal
        if self.intersectsRect(goal, goalRects["top"]):
            rect = goalRects["top"]
            self.lastCollide = rect
            
            # collide from top
            if playerRect.centery < rect.centery:
                self.collideVector += Vector2(0, -1)

            # collide from bottom
            if playerRect.centery > rect.centery:
                self.collideVector += Vector2(0, 1)

        # collide with bottom of goal
        elif self.intersectsRect(goal, goalRects["bottom"]):
            rect = goalRects["bottom"]
            self.lastCollide = rect
            
            # collide from top
            if playerRect.centery < rect.centery:
                self.collideVector += Vector2(0, -1)

            # collide from bottom
            if playerRect.centery > rect.centery:
                self.collideVector += Vector2(0, 1)
        
        # clamp collide vector
        self.collideVector = Vector2(self.collideVector.x, max(-1 * Player.walkSpeed, min(self.collideVector.y, Player.walkSpeed)))

    # walk into ball, lightly tap
    def tapBall(self, ball):
        if not self.touchingBall:
            totalSpeed = self.speed + self.moveVector.length() + self.pushVector.length()

            ball.angle = Angle.angleBetween(self.pos, ball.pos)
            ball.speed = totalSpeed * Player.speedMult
            ball.zVel = totalSpeed * Player.zVelMult

            self.touchingBall = True