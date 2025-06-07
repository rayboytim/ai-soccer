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
from nn import *

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

timer = 5 # both ai have 30 seconds to score, if not they both lose
lastTick = pygame.time.get_ticks()

timerIncrement = 1000 # every x games
timerIncrementAmount = 5 # timer increments by y

# nn stats
gameNum = 0 # how many times has the simulation ran
genNum = 0 # what generation are we in

agentsPerGen = 20 # also the number of games per generation
survivalRate = 0.5

fitnessThreshold = -1000 # if both agents go under this value, end game early

redAgents = []
blueAgents = []

# fitness stats

minDistPerSec = 100 # minimum distance per second to not get punished

# average fitness after each generation
redmedianFitness = []
bluemedianFitness = []

for _ in range(agentsPerGen):
    redAgents.append(Player("Red", "red"))
    blueAgents.append(Player("Blue", "blue"))

# objects

# text elements
textElements = [
    TextElement(str(redScore), "scoreRed", Colors.white),
    TextElement(str(blueScore), "scoreBlue", Colors.white),
    TextElement(str(timer), "timer", Colors.white),
    TextElement(str(gameNum), "gameNum", Colors.white),
    TextElement("", "fitnessRed", Colors.white),
    TextElement("", "fitnessBlue", Colors.white),
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
players = []

# balls
balls = [
    Ball()
]

entities = players + balls

# assess agent performance
# kill off worst and reproduce & mutate best
def assessAgents():
    global redAgents, blueAgents, agentsPerGen, survivalRate, redmedianFitness, bluemedianFitness, genNum

    print(f"End of gen {genNum}")

    # add median fitness to list

    redFitness = []
    blueFitness = []

    for a in redAgents:
        redFitness.append(a.fitness)
    for a in blueAgents:
        blueFitness.append(a.fitness)

    redFitness.sort()
    blueFitness.sort()

    redmedianFitness.append(redFitness[int(agentsPerGen//2)])
    bluemedianFitness.append(blueFitness[int(agentsPerGen//2)])

    print(f"Red median fitness: {redmedianFitness}")
    print(f"Blue median fitness: {bluemedianFitness}")

    # sort agents by fitness
    redAgents = sorted(redAgents, key = lambda x: x.fitness, reverse=True)
    blueAgents = sorted(blueAgents, key = lambda x: x.fitness, reverse=True)

    # find number of agents to survive
    agentsToLive = math.ceil(agentsPerGen * survivalRate)

    # remove those that don't survive
    redAgents = redAgents[:agentsToLive]
    blueAgents = blueAgents[:agentsToLive]

    topRedAgents = redAgents[:agentsToLive]
    topBlueAgents = blueAgents[:agentsToLive]

    # reproduce
    while len(redAgents) < agentsPerGen:
        # randomly select among top agents
        parent = random.choice(topRedAgents)
        child = copy.deepcopy(parent)

        child.nn.mutate(Player.mutateAmount, Player.mutateChance)
        redAgents.append(child)

    
    while len(blueAgents) < agentsPerGen:
        # randomly select among top agents
        parent = random.choice(topBlueAgents)
        child = copy.deepcopy(parent)

        child.nn.mutate(Player.mutateAmount, Player.mutateChance)
        blueAgents.append(child)

# reset game
def reset():
    global timer, gameNum, agentsPerGen, genNum, players, entities, timerIncrement, timerIncrementAmount

    # round fitness
    for player in players:
        player.fitness = math.floor(player.fitness)

    if gameNum != 0:
        print(f"Red fitness: {players[0].fitness}")
        print(f"Blue fitness: {players[1].fitness}")

    players.clear()

    # test new agents
    players.append(redAgents[gameNum % agentsPerGen])
    players.append(blueAgents[gameNum % agentsPerGen])
    
    entities = players + balls

    # reset balls
    for ball in balls:
        ball.pos = Vector2(640, 360)
        ball.height = 0

        ball.speed = 0
        ball.angle = Angle(0)
        ball.pushVector = Vector2(0,0)
        ball.collideVector = Vector2(0,0)

        ball.lastKick = None

    # reset players
    for player in players:
        if player.team == "red":
            player.pos = Vector2(140, 360)
        elif player.team == "blue":
            player.pos = Vector2(1140, 360)
        
        player.height = 0

        player.speed = 0
        player.angle = Angle(0)
        player.pushVector = Vector2(0,0)
        player.collideVector = Vector2(0,0)

        player.ballKicks = 0
        if player.team == "red":
            player.lastPos = Vector2(540,360)
        elif player.team == "blue":
            player.lastPos = Vector2(740,360)

        player.fitness = 0

    # increment game number
    gameNum += 1
    textElements[3].text = str(gameNum)

    # assess agent fitness
    if gameNum % agentsPerGen == 0 and gameNum != 0:
        genNum += 1
        assessAgents()

    # reset timer
    # every 500 games the timer length increases by 5 seconds
    timer = 5 + (gameNum // timerIncrement) * timerIncrementAmount
    textElements[2].text = str(timer)
    
    print(f"\nGame #{gameNum}")

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

    # keys = pygame.key.get_pressed()

    # if keys[pygame.K_w]:
    #     players[0].moveVector.y = -1 * Player.maxWalkSpeed
    # if keys[pygame.K_a]:
    #     players[0].moveVector.x = -1 * Player.maxWalkSpeed
    # if keys[pygame.K_s]:
    #     players[0].moveVector.y = Player.maxWalkSpeed
    # if keys[pygame.K_d]:
    #     players[0].moveVector.x = Player.maxWalkSpeed

    # update fitness text
    if len(players) == 2:
        textElements[4].text = str(math.floor(players[0].fitness))
        textElements[5].text = str(math.floor(players[1].fitness))

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
            # player brain

            if e == players[0]:
                opponent = players[1]
            elif e == players[1]:
                opponent = players[0]

            # inputs are the locations of all entities
            inputsToNN = [
                e.pos.x,
                e.pos.y,
                opponent.pos.x,
                opponent.pos.y,
                balls[0].pos.x,
                balls[0].pos.y,
                # balls[0].angle.degrees,
                # balls[0].speed,
                # balls[0].height,
            ]

            # outputs are the vel [-1, 1]
            outputsfromNN = e.nn.brain(inputsToNN)

            moveX = outputsfromNN[0]
            moveY = outputsfromNN[1]

            # normalize the vector
            moveVector = Vector2(moveX, moveY).normalize() * Player.maxWalkSpeed

            e.move(moveVector)

            # player collision
            for otherPlayer in players:
                if e != otherPlayer:
                    e.playerCollide(otherPlayer)

            # goal post collision
            for goal in goals:
                e.goalCollide(goal)

            # screen bound collision
            e.collideWalls(screenW, screenH)

            # ball interaction
            for ball in balls:
                # dec fitness if player goes past the ball
                if e == players[0]:
                    if e.pos.x > ball.pos.x:
                        e.fitness -= (e.pos.x - ball.pos.x) / 640
                if e == players[1]:
                    if e.pos.x < ball.pos.x:
                        e.fitness -= (ball.pos.x - e.pos.x) / 640

                if e.intersects(ball):
                    e.kickBall(ball)

                    # add to fitness
                    e.fitness += 100
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
                    print("Red scored!")

                    if ball.lastKick == players[0]:
                        players[0].fitness += 1000
                        players[1].fitness -= 500
                    else:
                        players[1].fitness -= 2000

                    redScore += 1
                    textElements[0].text = str(redScore)

                    reset()

                elif score == "blue":
                    print("Blue scored!")

                    if ball.lastKick == players[1]:
                        players[1].fitness += 1000
                        players[0].fitness -= 500
                    else:
                        players[0].fitness -= 2000

                    blueScore += 1
                    textElements[1].text = str(blueScore)

                    reset()
            
            # inc fitness based on ball location on field
            if e.getRect().centerx > 640:
                diff = (e.getRect().centerx - 640) / 640
                
                players[0].fitness += diff
            elif e.getRect().centerx < 640:
                diff = (640 - e.getRect().centerx) / 640
                
                players[1].fitness += diff

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

    # if both players have fitness under threshold, end game early
    if len(players) == 2:
        if players[0].fitness < fitnessThreshold and players[1].fitness < fitnessThreshold:
            reset()

    # timer
    currentTime = pygame.time.get_ticks()

    if currentTime - lastTick >= 1000: # 1000ms

        timer -= 1
        textElements[2].text = str(timer)
        
        # dash cooldown
        for player in players:
            player.dashCooldown -= 1

        # track distance travelled in the last second
        for player in players:
            dist = player.pos.distance(player.lastPos)

            if dist < minDistPerSec:
                player.fitness -= minDistPerSec

            player.lastPos = Vector2(player.pos.x, player.pos.y)

        lastTick = currentTime

        # time up
        if timer <= 0:
            reset()

    # update screen
    pygame.display.update()
    # tick at 60 fps
    dt = clock.tick(60)

pygame.quit()
sys.exit()
