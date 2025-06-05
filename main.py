# main.py
# rayboytim 6/3/25

import pygame
import sys
import random

from objects import *
from player import *
from ball import *
from map import *
from goal import *
from gameutils import *

# pygame elements
pygame.init()

screenW, screenH = 1280, 720
screenSize = (screenW, screenH)

surf = pygame.display.set_mode(screenSize, pygame.SRCALPHA)
pygame.display.set_caption("AI Soccer by Ray Boytim")

clock = pygame.time.Clock()

# stats
redScore = 0
blueScore = 0

# objects

# text elements
textElements = [
    TextElement(str(redScore), "largeRed", Colors.white),
    TextElement(str(blueScore), "largeBlue", Colors.white),
]

# map elements, rendered first
mapElements = [
    BoxElement(Colors.lightgray, 100, 45, 540, 630, 5), # left side of field
    BoxElement(Colors.lightgray, 635, 45, 545, 630, 5), # right side of field
    
    CircleElement(Colors.lightgray, 640, 360, 125, 5), # center circle

    BoxElement(Colors.lightgray, 100, 135, 215, 450, 5), # left pen area
    BoxElement(Colors.lightgray, 965, 135, 215, 450, 5), # right pen area

    BoxElement(Colors.lightgray, 100, 235, 100, 250, 5), # left goal area
    BoxElement(Colors.lightgray, 1080, 235, 100, 250, 5), # right goal area
]

# goals, rendered last
goals = [
    Goal("red"),
    Goal("blue")
]

# entities

# players
players = [
    Player("Player1", "red"),
    Player("Player2", "blue"),
]

# balls
balls = [
    Ball()
]

entities = players + balls

# main loop
running = True
while running:
    
    # reset screen
    surf.fill(Colors.green)

    # event handling
    for event in pygame.event.get():

        # close window
        if event.type == pygame.QUIT:
            running = False

    # sort entities by height
    entities.sort(key = lambda obj: obj.height)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        players[0].moveVector.y = -1 * Player.walkSpeed
    if keys[pygame.K_a]:
        players[0].moveVector.x = -1 * Player.walkSpeed
    if keys[pygame.K_s]:
        players[0].moveVector.y = Player.walkSpeed
    if keys[pygame.K_d]:
        players[0].moveVector.x = Player.walkSpeed

    # render text
    for e in textElements:
        e.draw(surf)

    # render map
    for e in mapElements:
        e.draw(surf)

    # run object functions
    for e in entities:

        # player functions
        if isinstance(e, Player):

            # player collision
            for otherPlayer in players:
                if e != otherPlayer:
                    e.playerCollide(otherPlayer)

            # goal post collision
            for goal in goals:
                e.goalCollide(goal)

            # ball interaction
            for ball in balls:
                if e.intersects(ball):
                    e.tapBall(ball)
                else:
                    e.touchingBall = False

        # ball functions
        if isinstance(e, Ball):

            # player collision
            isTouchingPlayer = False
            
            for player in players:
                if not isTouchingPlayer:
                    isTouchingPlayer = e.playerCollide(player)
                else:
                    e.playerCollide(player)

            # if not touching any player, reset push vector
            if not isTouchingPlayer:
                e.pushVector = Vector2(0,0)
            
            # bounce ball off walls
            e.bounce(screenW, screenH)

            # goal related functions
            for goal in goals:
                # bounce off goal posts
                e.bounceGoal(goal)

                # check and score goals
                score = e.checkGoal(goal)
                if score == "red":
                    redScore += 1
                    textElements[0].text = str(redScore)

                elif score == "blue":
                    blueScore += 1
                    textElements[1].text = str(blueScore)

        # entity functions
        if isinstance(e, Entity):
            # update position of object, after all physics functions have executed
            e.updatePos()

    # render entities
    for e in entities:
        # render shadows
        if hasattr(e, "shadow"):
            e.shadow.draw(surf)

        # render entities
        e.draw(surf)

    # render goals
    for goal in goals:
        goal.draw(surf)

    # update screen
    pygame.display.update()

    # tick at 60 fps
    clock.tick(60)

pygame.quit()
sys.exit()