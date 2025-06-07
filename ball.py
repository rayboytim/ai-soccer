# ball.py
# rayboytim 6/3/25

from objects import *
from player import *
from gameutils import *

import random
import time
import sys

class Ball(Entity):

    # radius of ball when it is on the ground
    minRadius = 20

    def __init__(self):
        super().__init__(0, 640, 360) # always spawn in middle of screen

        self.color = Colors.gray

        # last hit goal post (to ensure that goals aren't scored if it hits the post)
        self.lastHit = None
        self.canScore = True

        # last player to kick ball
        self.lastKick = None

    def draw(self, surface):
        # calculate visual pos based on height
        # draws entity slightly towards the nearest corner of the screen when in the air
        visualX = self.pos.x + (self.height * (self.pos.x - 640) / 640 * Entity.distortion)
        visualY = self.pos.y + (self.height * (self.pos.y - 360) / 360 * Entity.distortion)

        info = (
            surface,
            self.color,
            (visualX, visualY),
            self.radius
        )

        pygame.draw.circle(*info)

    def getRect(self):
        top = self.pos.x - Ball.minRadius * 0.75
        left = self.pos.y - Ball.minRadius * 0.75

        info = (top, left, Ball.minRadius*1.5, Ball.minRadius*1.5)

        return pygame.Rect(*info)
    
    # bounce off walls
    def bounce(self, screenW, screenH):

        # left
        if self.pos.x - Ball.minRadius <= 0:
            if self.angle.degrees > 90 and self.angle.degrees < 270:
                self.angle = Angle(180 - self.angle.degrees)
            self.speed *= Entity.slowdownRate

        # right
        elif self.pos.x + Ball.minRadius >= screenW:
            if self.angle.degrees < 90 or self.angle.degrees > 270:
                self.angle = Angle(180 - self.angle.degrees)
            self.speed *= Entity.slowdownRate

        # bottom
        if self.pos.y - Ball.minRadius <= 0:
            if self.angle.degrees > 180:
                self.angle = Angle(-self.angle.degrees)
            self.speed *= Entity.slowdownRate

        # top
        elif self.pos.y + Ball.minRadius >= screenH:
            if self.angle.degrees < 180:
                self.angle = Angle(-self.angle.degrees)
            self.speed *= Entity.slowdownRate

    # bounce off goal sides
    def bounceGoal(self, goal):
        ballRect = self.getRect()
        goalRects = goal.getCollisionRects()

        if self.lastHit:
            if not self.intersectsRect(goal, self.lastHit):
                self.lastHit = None
                self.canScore = True

        # hit top of goal
        if self.intersectsRect(goal, goalRects["top"]):
            rect = goalRects["top"]
            self.lastHit = rect
            self.canScore = False

            # hit from top
            if ballRect.centery < rect.centery and self.angle.degrees < 180:
                self.angle = Angle(-self.angle.degrees)
                self.speed *= Entity.slowdownRate

            # hit from bottom
            if ballRect.centery > rect.centery and self.angle.degrees > 180:
                self.angle = Angle(-self.angle.degrees)
                self.speed *= Entity.slowdownRate

        # hit bottom of goal
        elif self.intersectsRect(goal, goalRects["bottom"]):
            rect = goalRects["bottom"]
            self.lastHit = rect
            self.canScore = False

            # hit from top
            if ballRect.centery < rect.centery and self.angle.degrees < 180:
                self.angle = Angle(-self.angle.degrees)
                self.speed *= Entity.slowdownRate

            # hit from bottom
            if ballRect.centery > rect.centery and self.angle.degrees > 180:
                self.angle = Angle(-self.angle.degrees)
                self.speed *= Entity.slowdownRate


    # ball moves into player, push away (usually when the player is stationary)
    # returns true if the ball is touching the player
    def playerCollide(self, other) -> bool:

        # if not colliding, skip player
        if self.intersects(other):
            return False
        
        # get distance from other player
        diff = self.pos - other.pos
        dist = self.pos.distance(other.pos)

        # if too far away to actually be colliding, return
        if dist > 60:
            return False

        # perfectly overlapping, push randomly
        if dist == 0:
            diff = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            dist = diff.distance()

        # normalize the distance vector
        diffNorm = diff / dist

        # find how much to push
        overlap = Player.minRadius * 2 - dist

        # push ball half the overlap distance away from each other
        pushVector = diffNorm * (overlap / 2) * Player.collisionStiffness

        # add to push vector
        self.pushVector -= pushVector

        return True
    
    # check goal and score goal
    def checkGoal(self, goal) -> str:
        if self.canScore:
            if not self.intersects(goal):
                return
            else:
                # opposite team scores
                if goal.team == "red":

                    self.pos = Vector2(440, 360)
                    self.speed = 0
                    self.height = 10
                    self.zVel = 0

                    return("blue")
                
                elif goal.team == "blue":

                    self.pos = Vector2(840, 360)
                    self.speed = 0
                    self.height = 10
                    self.zVel = 0

                    return("red")