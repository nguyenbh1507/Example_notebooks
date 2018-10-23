"""
Simulator for GridWorld Game
Source = https://medium.com/p/8438a3e2b8df

In the environment the agent controls a blue square,
and the goal is to navigate to the green squares (reward +1)
while avoiding the red squares (reward -1)

Game map = map of game
Map for visualization: map to show on screen
"""


import numpy as np
import random
import itertools
import scipy.misc
import matplotlib.pyplot as plt


class gameOb:
    """
    Game Object
    """
    def __init__(self, coordinates, size, intensity, channel, reward, name):
        """
        Game objects initialization

        :param coordinates: indexed by (x, y), objective location
        :param size: size of object, = 1
        :param intensity: colour intensity
        :param channel: hero = 2 (blue chane), fire = 0 (red chanel), goal = 1 (green chanel)
        :param reward: hero = None, fire = -1, goal = +1
        :param name: hero = blue square, fire = red square, goal = green square
        """
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.size = size
        self.intensity = intensity
        self.channel = channel
        self.reward = reward
        self.name = name
        

class gameEnv:
    """
    Game environment simulator

    """
    def __init__(self, partial, size):
        """
        Initialise game environment
        :param partial: True/False, If True then game map is always of 5x5-grid,
        where "hero" is located at center
        :param size: size of 2D map
        number of actions = 4, move left, right, up, down
        """
        self.sizeX = size
        self.sizeY = size
        self.actions = 4
        self.objects = []
        self.partial = partial
        self.reset()
        
    def reset(self):
        """
        reset game environment
        create game objects (hero, bug=goal, hole=fire) and add to its environment
        for each object first random? get location (coordinates)
        then feed to gameOb() to create
        :return: initial state of game environment
        """
        # Reset object list
        self.objects = []

        # Add hero
        hero = gameOb(self.newPosition(), 1, 1, 2, None, 'hero')
        self.objects.append(hero)

        # Add goal/bug
        bug = gameOb(self.newPosition(), 1, 1, 1, 1, 'goal')
        self.objects.append(bug)

        # Add fire/hole
        hole = gameOb(self.newPosition(), 1, 1, 0, -1, 'fire')
        self.objects.append(hole)

        # Add more objects
        bug2 = gameOb(self.newPosition(), 1, 1, 1, 1, 'goal')
        self.objects.append(bug2)
        hole2 = gameOb(self.newPosition(), 1, 1, 0, -1, 'fire')
        self.objects.append(hole2)
        bug3 = gameOb(self.newPosition(), 1, 1, 1, 1, 'goal')
        self.objects.append(bug3)
        bug4 = gameOb(self.newPosition(), 1, 1, 1, 1, 'goal')
        self.objects.append(bug4)

        # render (create map for visualization) and set state and return it
        state = self.renderEnv()
        self.state = state
        return state

    def moveChar(self, direction):
        """
        Move hero and return penalize (always 0)
        :param direction: 0 - up, 1 - down, 2 - left, 3 - right
        :return: penalize for each movement
        """
        # Get hero and it initialize coordinates
        hero = self.objects[0]
        heroX = hero.x
        heroY = hero.y

        penalize = 0.

        if direction == 0 and hero.y >= 1:
            hero.y -= 1  # move down
        if direction == 1 and hero.y <= self.sizeY-2:
            hero.y += 1  # move up
        if direction == 2 and hero.x >= 1:
            hero.x -= 1  # move left
        if direction == 3 and hero.x <= self.sizeX-2:
            hero.x += 1  # move right

        # in case no move (direction is not 0..3)
        if hero.x == heroX and hero.y == heroY:
            penalize = 0.0

        # reset hero
        self.objects[0] = hero

        # return penalize
        return penalize
    
    def newPosition(self):
        """
        Create coordinates for game objects
        - create list of all possible points
        - remove all busy points (points with existing objects)
        - randomly choice from remaining list
        :return: coordinates of new "available" position
        """

        # Create map points (x, y), where 0<= x < sizeX, 0<= y < ziseY
        iterables = [range(self.sizeX), range(self.sizeY)]
        points = []
        for t in itertools.product(*iterables):
            points.append(t)

        # Get all busy positions
        currentPositions = []
        for objectA in self.objects:
            if (objectA.x, objectA.y) not in currentPositions:
                currentPositions.append((objectA.x, objectA.y))

        # remove all busy positions
        for pos in currentPositions:
            points.remove(pos)

        # Randomly choice position and return it
        location = np.random.choice(range(len(points)), replace=False)
        return points[location]

    def checkGoal(self):
        """
        Check if "hero" falls in "goal"
        :return: reward, End game status, (game never end)
        """
        # Create list of non-"hero" objects
        others = []
        hero = None
        for obj in self.objects:
            if obj.name == 'hero':
                hero = obj
            else:
                others.append(obj)

        ended = False

        # check "other" list
        # if hero location = "other" location
        # remove current "other" object
        # and random create new object of the same type of "other"
        # then return "other" reward and False status

        for other in others:
            if hero and hero.x == other.x and hero.y == other.y:
                self.objects.remove(other)

                if other.reward == 1:  # goal type
                    self.objects.append(gameOb(self.newPosition(), 1, 1, 1, 1, 'goal'))
                else:                  # fire type
                    self.objects.append(gameOb(self.newPosition(), 1, 1, 0, -1, 'fire'))

                # return and escape for loop
                return other.reward, False

        if not ended:  # in case hero is None
            return 0.0, False

    def renderEnv(self):
        """
        Render game environment/map (image 3 chanels <=> numpy array, shape = (sizeX, sizeY, 3)
        Map image will be resize to 84 x 84 x 3
        :return: map for visualization = game state
        """
        # initialize white game map
        a = np.ones([self.sizeY+2, self.sizeX+2, 3])  # plus 2 for "game map-frame"
        a[1:-1, 1:-1, :] = 0  # all game "pixels" is black

        # fill intensity = 1 for all game pixels
        hero = None
        for item in self.objects:
            a[item.y+1:item.y+item.size+1, item.x+1:item.x+item.size+1, item.channel] = \
                item.intensity
            if item.name == 'hero':
                hero = item

        # clip game map if partial = True
        if self.partial:
            a = a[hero.y:hero.y+3, hero.x:hero.x+3, :]

        # fit game map to visualization (84x84 screen pixels), chanel by chanel then stack them
        b = scipy.misc.imresize(a[:, :, 0], [84, 84, 1], interp='nearest')  # Red chanel
        c = scipy.misc.imresize(a[:, :, 1], [84, 84, 1], interp='nearest')  # Green chanel
        d = scipy.misc.imresize(a[:, :, 2], [84, 84, 1], interp='nearest')  # Blue chanel
        a = np.stack([b, c, d], axis=2)

        return a

    def step(self, action):
        """
        do the action in one step
        :param action: move: 0 - up, 1 - down, 2 - left, 3 - right
        :return: new game state, reward, end-game status
        """
        # do action and get penalty
        penalty = self.moveChar(action)

        # get reward and check end-game status
        reward, done = self.checkGoal()

        # set new state
        state = self.renderEnv()

        if reward is None:
            print("Game over:", done, "\t Reward:", reward, "\tPenalty:", penalty)
            return state, penalty, done
        else:
            return state, (reward + penalty), done
