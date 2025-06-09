# player.py
# rayboytim 6/3/25

import random
import math
import copy

from objects import *
from gameutils import *
from nn import *

# player class
class Player(Entity):

    # radius of player when they are on the ground
    minRadius = 30

    # multiplier for how fast player collisions occur
    collisionStiffness = 0.1

    maxWalkSpeed = 5
    walkSmoothing = 0.85

    # ball hit multipliers
    speedMult = 1.75
    zVelMult = 0.1

    # dash cooldown timer
    dashCooldownTimer = 5

    # nn vars
    
    mutateAmount = 0.2 # amount that weight can be mutated by at once, -mutateAmount to mutateAmount
    mutateChance = 0.1 # percentage of weights to mutate

    ballKickFitnessGain = 250 # fitness gain per ball kick
    wallPunishment = -1 # fitness loss per frame touching wall

    def __init__(self, name: str, team: str):
        self.name = name
        self.team = team

        # team info
        if team == "red":
            self.color = Colors.red
            super().__init__(0, 140, 360)
        elif team == "blue":
            self.color = Colors.blue
            super().__init__(0, 1140, 360)

        self.touchingBall = False

        # user controlled move vector
        self.moveVector = Vector2(0,0)
        self.smoothedMoveVector = Vector2(0, 0)

        # screen bound collision
        self.boundCollideVector = Vector2(0,0)
        
        # goal collision
        self.lastCollide = None
        self.collideVector = Vector2(0,0)

        # movement
        self.dashCooldown = 0

        self.recentPos = Vector2(0,0) # position from the last frame

        # per-game stats
        self.ballKicks = 0

        # last position per second
        if team == "red":
            self.lastPos = Vector2(540,360)
        elif team == "blue":
            self.lastPos = Vector2(740,360)

        # brain
        layers = [7,12,8,2]

        self.nn = NN(layers)
        self.fitness = 0

        # start with a mutation
        self.nn.mutate(Player.mutateAmount, Player.mutateChance)

        # last save of nn
        self.nnSave = copy.deepcopy(self.nn)

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
    
    # movement
    def move(self, vector: Vector2):

        # if the player is dashing, don't slow them down
        self.speed = max(Player.maxWalkSpeed, self.speed)

        # apply smoothening and momentum
        self.smoothedMoveVector.x = (
            Player.walkSmoothing * self.smoothedMoveVector.x +
            (1 - Player.walkSmoothing) * vector.x
        )

        self.smoothedMoveVector.y = (
            Player.walkSmoothing * self.smoothedMoveVector.y +
            (1 - Player.walkSmoothing) * vector.y
        )

        # change player's angle
        self.moveVector = self.smoothedMoveVector

        # if self.dashCooldown < 0:
        #     self.speed = Player.maxWalkSpeed
        #     self.dashCooldown = 0

    # dash
    def dash(self):
        if not self.dashCooldown:
            self.dashCooldown = 5
            self.speed = Player.maxWalkSpeed * 2

    # collision with other players
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

    # screen bound collision
    def collideWalls(self, screenW, screenH):
        colliding = False

        # left
        if self.pos.x - Player.minRadius <= 0:
            colliding = True
            self.boundCollideVector += Vector2(1, 0)

        # right
        elif self.pos.x + Player.minRadius >= screenW:
            colliding = True
            self.boundCollideVector += Vector2(-1, 0)

        # bottom
        if self.pos.y - Player.minRadius <= 0:
            colliding = True
            self.boundCollideVector += Vector2(0, 1)

        # top
        elif self.pos.y + Player.minRadius >= screenH:
            colliding = True
            self.boundCollideVector += Vector2(0, -1)

        if not colliding:
            self.boundCollideVector = Vector2(0,0)
        else:
            # remove fitness for hitting wall
            self.fitness += Player.wallPunishment

    # goal post collision
    def goalCollide(self, goal):
        playerRect = self.getRect()
        goalRects = goal.getCollisionRects()

        if self.lastCollide:
            if not self.intersectsRect(goal, self.lastCollide):
                self.lastCollide = None
                self.collideVector = Vector2(0,0)
            else:
                # remove fitness for hitting wall
                self.fitness += Player.wallPunishment

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
        self.collideVector = Vector2(self.collideVector.x, max(-1 * Player.maxWalkSpeed, min(self.collideVector.y, Player.maxWalkSpeed)))

    # kick ball
    def kickBall(self, ball):
        if not self.touchingBall:
            self.ballKicks += 1

            totalSpeed = self.moveVector.length() + self.pushVector.length()

            ball.angle = Angle.angleBetween(self.pos, ball.pos)
            ball.speed = totalSpeed * Player.speedMult
            ball.zVel = totalSpeed * Player.zVelMult

            self.touchingBall = True
            ball.lastKick = self

            # inc fitness
            self.fitness += Player.ballKickFitnessGain