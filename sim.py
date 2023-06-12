import os, sys
import time
import random
import numpy as np
import simpy
import pygame
from pygame.locals import *
from collections import OrderedDict
from typing import Tuple, List
from utils import Color, logging
from termcolor import colored

os.system('color')

class Simulation(object):

    def __init__(self,
                 env,
                 screen_width :int=800,
                 screen_height:int=600,
                 pauseTime:float  =0.05,
                 numInitVehs:int  =50,
                ):
        pygame.init()
        self.T = None
        self.pauseTime = pauseTime      # control the GUI update speed
        self.numInitVehs = numInitVehs  # #vehicles at the initialization
        self.env = env
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.net = Network(env, screen=self.screen, dt=pauseTime)
        self.action = self.env.process(self.render())

    def simulate(self, until):
        """
        A wrapper for the simpy.Environment.run(until:int)
        """
        self.T = until
        self.env.run(until)
        logging(msg=f"LOGGING: finish the simulation in {self.T} seconds",
                color='green')

    def render(self):
        '''
        Render for the simulation object itself:
        controlling for the distroy of the windows
        '''
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.quit()
            time.sleep(self.pauseTime)
            yield self.env.timeout(1)
        
    def initToyNetwork(self):
        '''
        initialize a network with the shape of ++ with traffic
        8 nodes | 14 links
        '''
        # initialize all the 8 nodes
        nodeIds = [1,2]
        nodePositions = [(self.screen_width//2-Link.GRIDSIZE*25-Node.SIZE//2, self.screen_height//2), 
                         (self.screen_width//2+Link.GRIDSIZE*25+Node.SIZE//2, self.screen_height//2),]
        for nodeId, nodePos in zip(nodeIds, nodePositions):
            self.net.addTrafficLightNode(nodeId, position=nodePos, isExit=False, isControlled=True)
        assert len(self.net.nodeCollection) == 2

        # set the directions of inflow/outflow 
        directionIds = [(11,2,32,41), (12,21,31,1)]
        for nodeId, nodeDirection in zip(nodeIds, directionIds):
            dir = {
                'N':nodeDirection[0],
                'E':nodeDirection[1],
                'S':nodeDirection[2],
                'W':nodeDirection[3],
            }
            self.net.trafficLightCollection[nodeId].direction = dir
        nodeIds = [11, 12, 21, 31, 32, 41]
        nodePositions = [
            (self.screen_width//2-Link.GRIDSIZE*25-Node.SIZE//2, self.screen_height//2-Node.SIZE-Link.GRIDSIZE*50), # 11
            (self.screen_width//2+Link.GRIDSIZE*25+Node.SIZE//2, self.screen_height//2-Node.SIZE-Link.GRIDSIZE*50), # 12
            (self.screen_width//2+Link.GRIDSIZE*25+Node.SIZE*3//2+Link.GRIDSIZE*50, self.screen_height//2),    # 21
            (self.screen_width//2+Link.GRIDSIZE*25+Node.SIZE//2, self.screen_height//2+Node.SIZE+Link.GRIDSIZE*50), # 31
            (self.screen_width//2-Link.GRIDSIZE*25-Node.SIZE//2, self.screen_height//2+Node.SIZE+Link.GRIDSIZE*50), # 32
            (self.screen_width//2-Link.GRIDSIZE*25-Node.SIZE*3//2-Link.GRIDSIZE*50, self.screen_height//2),    # 41
        ]
        for nodeId, nodePos in zip(nodeIds, nodePositions):
            self.net.addNode(nodeId, position=nodePos, isExit=True, isControlled=False)
        assert len(self.net.nodeCollection) == 2 + 6
        logging(msg=f"LOGGING: initialize {len(self.net.nodeCollection):2.0f} nodes into network", 
                color='green')

        # initialize all the links
        linkODs = [(1,2)]
        for (o, d) in linkODs:
            linkId1 = "I" + str(o) + "O" + str(d)
            self.net.addLink(linkId1, lengthLane=350, numLanes=3, originNodeId=o, destinNodeId=d, type=Link.NORMAL)
            linkId2 = "I" + str(d) + "O" + str(o)
            self.net.addLink(linkId2, lengthLane=350, numLanes=3, originNodeId=d, destinNodeId=o, type=Link.NORMAL)
            self.net.linkPairCollection[(o,d)] = (linkId1, linkId2)
        linkODs = [(11,1), (12,2), (21,2), (31,2), (32,1), (41,1)]
        for (o, d) in linkODs:
            linkId1 = "I" + str(o) + "O" + str(d)
            self.net.addLink(linkId1, lengthLane=350, numLanes=3, originNodeId=o, destinNodeId=d, type=Link.IN)
            linkId2 = "I" + str(d) + "O" + str(o)
            self.net.addLink(linkId2, lengthLane=350, numLanes=3, originNodeId=d, destinNodeId=o, type=Link.OUT)            
            self.net.linkPairCollection[(o,d)] = (linkId1, linkId2)
        
        assert len(self.net.linkCollection) == 2 + 6 + 6
        assert len(self.net.inflowLinkCollection) == 6
        assert len(self.net.outflowLinkCollection) == 6
        logging(msg=f"LOGGING: initialize {len(self.net.linkCollection):2.0f} links into network", 
                color='green')

        # set the connected links for each node
        for nodeId, node in self.net.nodeCollection.items():
            inflowLinkIds, outflowLinkIds = [], []
            for linkId, link in self.net.linkCollection.items():
                if link.originNodeId == nodeId:
                    outflowLinkIds.append(linkId)
                elif link.destinNodeId == nodeId:
                    inflowLinkIds.append(linkId)
            self.net.nodeCollection[nodeId].inflowLinkIds  = inflowLinkIds
            self.net.nodeCollection[nodeId].outflowLinkIds = outflowLinkIds
        # initialize the vehicles into network
        self.net.initCars(self.numInitVehs)
        assert len(self.net.carCollection) == self.numInitVehs
        assert self.net.numVehInSystem == self.numInitVehs
        logging(msg=f"LOGGING: initialize {self.numInitVehs:2.0f} cars into network",
                color='green')

    #TODO:
    def initpNeumaNetwork(self, numInitVehs=25):
        '''
        initialize the real-world Athens road network of districts 2 and 3
        20 nodes
        '''
        # initialize all the 8 nodes
        nodeIds = [1,2,3,4,5,6,7,8,9,]
        nodePositions = [
            (self.screen_width//2-350//7*Link.GRIDSIZE, self.screen_width//2-140//7*Link.GRIDSIZE), #1
            (self.screen_width//2, self.screen_width//2-140//7*Link.GRIDSIZE),                    #2
            (self.screen_width//2+91//7*Link.GRIDSIZE-Node.SIZE//2, self.screen_height//2), 
                         (self.screen_width//2+Link.GRIDSIZE*25+Node.SIZE//2, self.screen_height//2),]
        for nodeId, nodePos in zip(nodeIds, nodePositions):
            self.net.addTrafficLightNode(nodeId, position=nodePos, isExit=False, isControlled=True)
        assert len(self.net.nodeCollection) == 9


class Network(object):
       
    def __init__(self, 
                 env,
                 screen,
                 height=600,
                 width=800,
                 dt=0.1):

        self.screen = screen
        self.width = width
        self.height = height
        self.backgroundColor = Color.GREEN
        # store all components
        self.linkCollection = OrderedDict()
        self.inflowLinkCollection = OrderedDict()
        self.outflowLinkCollection= OrderedDict()
        self.nodeCollection = OrderedDict()
        self.trafficLightCollection = OrderedDict()
        self.carCollection = OrderedDict()
        self.linkPairCollection = OrderedDict()
        self.matrixCollection = OrderedDict()
        self.numVehInSystem = 0
        self.totalVeh = 0 
        # discrete simulation process
        self.env = env
        self.dt  = dt
        self.action = self.env.process(self.render())
    
    def render(self):
        # a network process that visualizes the network:
        while True:
            # draw traffic elements in this step function:
            self.__gameStep()
            time.sleep(self.dt)
            ###################
            # vehicle generator
            ###################
            for linkId, inflow in self.inflowLinkCollection.items():
                if random.random() > 0.65:
                    vehId = self.totalVeh 
                    isSpawn = False
                    while(not isSpawn):
                        laneId = random.randint(a=0, b=self.linkCollection[linkId].numLanes-2)
                        gridId = 0
                        type = random.choice([i for i in range(1,6)])
                        if self.linkCollection[linkId].trafficMatrix[laneId][gridId] == 0:
                            # is empty, spawn the car
                            self.addCar(vehId, linkId, laneId, gridId, type=type)
                            logging(msg=f'car{vehId} spawns in the Network',
                                    color='blue')
                            isSpawn = True
            yield self.env.timeout(1)

    def __gameStep(self):
        ##################
        # draw background:
        ##################
        self.screen.fill(self.backgroundColor)
        
        #############
        # draw nodes:
        #############
        for nodeId, node in self.nodeCollection.items():
            pygame.draw.rect(self.screen, Color.WHITE, node.center2corner())
        
        #########################
        # draw the traffic light:
        #########################
        for tfId, tf in self.trafficLightCollection.items():
            lights = tf.lightPositions()
            for direction, positions in lights.items():
                pygame.draw.rect(self.screen, Color.RED, positions)
            lights = tf.getTrafficLightConditions()
            for direction, positions in lights.items():
                pygame.draw.rect(self.screen, Color.GREEN, positions)        
        
        ##################################
        # draw link and vehicles together:
        ##################################
        positions = {
            (1 , 2): ((self.width//2-Link.GRIDSIZE*25, self.height//2-Node.SIZE//2), (self.width//2+Link.GRIDSIZE*25, self.height//2+Node.SIZE//2)),
            (11, 1): ((self.width//2-Link.GRIDSIZE*25-Node.SIZE, self.height//2-Node.SIZE//2-Link.GRIDSIZE*50), (self.width//2-Link.GRIDSIZE*25, self.height//2-Node.SIZE//2)),
            (12, 2): ((self.width//2+Link.GRIDSIZE*25, self.height//2-Node.SIZE//2-Link.GRIDSIZE*50), (self.width//2+Link.GRIDSIZE*25+Node.SIZE, self.height//2+Node.SIZE//2)),
            (21, 2): ((self.width//2+Link.GRIDSIZE*25+Node.SIZE, self.height//2-Node.SIZE//2), (self.width//2+Link.GRIDSIZE*75+Node.SIZE, self.height//2-Node.SIZE//2)),
            (31, 2): ((self.width//2+Link.GRIDSIZE*25, self.height//2+Node.SIZE//2), (self.width//2+Link.GRIDSIZE*25+Node.SIZE, self.height//2+Node.SIZE//2+Link.GRIDSIZE*50)),
            (32, 1): ((self.width//2-Link.GRIDSIZE*25-Node.SIZE, self.height//2+Node.SIZE//2), (self.width//2-Link.GRIDSIZE*25, self.height//2+Node.SIZE//2+Link.GRIDSIZE*50)),
            (41, 1): ((self.width//2-Link.GRIDSIZE*75-Node.SIZE, self.height//2-Node.SIZE//2), (self.width//2-Link.GRIDSIZE*25-Node.SIZE, self.height//2+Node.SIZE//2))
        }
        for (o, d), (linkId1, linkId2) in self.linkPairCollection.items():        
            if (o, d) in [ (1 , 2), (41, 1), 
                           (21, 2), 
                           (11, 1), (12, 2),
                           (31, 2), (32, 1),
                          ]: 
                # retrieve the binary representation of the bi-directional roads:
                link1 = self.linkCollection[linkId1].binaryMatrix
                link2 = self.linkCollection[linkId2].binaryMatrix
                # concatenate the two raods together, 4 cases (orientations):
                # Case1: from left to right
                if (o, d) in [(1,2),(41,1)]:
                    link2 = np.flip(link2)
                    assert link1.shape == link2.shape
                    dualBinaryMatrix = np.concatenate([link2, link1])
                    rows = 6
                    cols = 50
                # Case2: from right to left
                elif (o, d) in [(21,2)]:
                    link1 = np.flip(link1)
                    assert link1.shape == link2.shape
                    dualBinaryMatrix = np.concatenate([link1, link2])
                    rows = 6
                    cols = 50
                # Case3: from top to down
                elif (o, d) in [(11,1), (12,2)]:
                    link1 = np.rot90(link1, k=3)
                    link2 = np.rot90(link2, k=1)
                    assert link1.shape == link2.shape
                    dualBinaryMatrix = np.concatenate([link1, link2], axis=1)
                    rows = 50
                    cols = 6 
                # Case4: from down to top                   
                elif (o, d) in [(31,2), (32,1)]:
                    link1 = np.rot90(link1, k=1)
                    link2 = np.rot90(link2, k=3)
                    assert link1.shape == link2.shape
                    dualBinaryMatrix = np.concatenate([link2, link1], axis=1)                    
                    rows = 50
                    cols = 6
                # store all concatenated matrices:
                self.matrixCollection[(o,d)] = dualBinaryMatrix.copy()
                topLeftCornerPos = positions[(o,d)][0]
                self.__draw_grid(o, d, rows, cols, topLeftCornerPos)
            # display text information in the left-top corner:

        #######################
        # add text information:
        #######################  
        self.__draw_text()
        pygame.display.flip()

    def __draw_grid(self, o, d, rows, cols, topLeftCornersPos):
        """
        Display the matrix for each couple of links:
        @ o: origin id
        @ d: destin id
        @ rows: #rows: depends on the shape of matrix
        @ cols: #cols: depends on the shape of matrix
        @ topLeftCornersPos: the position of left-top corner point
        """
        # retrieve the position and matrix:
        offset_x, offset_y = topLeftCornersPos
        matrix = self.matrixCollection[(o,d)]
        # draw each cell in the matrix row by col
        for row in range(rows):
            for col in range(cols):
                x = col * Link.GRIDSIZE + offset_x
                y = row * Link.GRIDSIZE + offset_y
                # specifiy the red cell for the existence of vehicle
                if matrix[row, col] == 1:
                    color = Color.PINK
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE))
                elif matrix[row, col] == 2:
                    color = Color.RED
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE))
                elif matrix[row, col] == 3:
                    color = Color.LIGHT_BLUE
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE))
                elif matrix[row, col] == 4:
                    color = Color.BLUE
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE))
                elif matrix[row, col] == 5:
                    color = Color.LIGHT_GREEN
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE))
                elif matrix[row, col] == 6:
                    color = Color.DARK_RED
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE))
                # otherwise: black cell for empty cell
                else:
                    color = Color.BLACK
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE), width=0)

    def __draw_text(self, 
                    font_name='Consolas',
                    font_size=18, 
                    font_color=Color.WHITE,):
        """
        Display TEXT information on the left-top corner of window:
        """
        font = pygame.font.SysFont(font_name, font_size)
        textLine1 = f"#Time: {self.env.now}"
        textLine2 = f"#vehicles in system: {self.numVehInSystem}"
        text_surface1 = font.render(textLine1, True, font_color)
        text_surface2 = font.render(textLine2, True, font_color)
        text_rect1 = text_surface1.get_rect()
        text_rect2 = text_surface2.get_rect()
        text_rect1.topleft = (10, 10)
        text_rect2.topleft = (10, 25)
        self.screen.blit(text_surface1, text_rect1)
        self.screen.blit(text_surface2, text_rect2)

    def initCars(self, numInitVehs):
        for vehId in range(numInitVehs):
            isSpawn = False
            while(not isSpawn):
                linkId = random.choice(list(self.linkCollection.keys()))
                laneId = random.randint(a=0, b=self.linkCollection[linkId].numLanes-1)
                gridId = random.randint(a=0, b=self.linkCollection[linkId].numGrids-10)
                type = random.choice([i for i in range(1,6)])
                if self.linkCollection[linkId].trafficMatrix[laneId][gridId] == 0:
                    # is empty, spawn the car
                    self.addCar(vehId, linkId, laneId, gridId, type=type)
                    isSpawn = True

    def addCar(self, vehId, linkId, laneId, gridId, type):
        car = Car(self.env, self, vehId, linkId, laneId, gridId, type=type)
        self.numVehInSystem += 1
        self.totalVeh += 1
        self.linkCollection[linkId].trafficMatrix[laneId][gridId] = car
        self.linkCollection[linkId].binaryMatrix[laneId, gridId] = type
        self.carCollection[vehId] = car
    
    def addNode(self, nodeId:int, position:Tuple[int,int], isExit:bool, isControlled:bool,):
        node = Node(nodeId, position, isExit, isControlled)
        self.nodeCollection[nodeId] = node
        
    def addTrafficLightNode(self, nodeId:int, position:Tuple[int,int], isExit:bool, isControlled:bool,):
        trafficLight = TrafficLight(nodeId, self.env, self, position, isExit, isControlled, greenTimes=[25,25,25,25])
        self.nodeCollection[nodeId] = trafficLight
        self.trafficLightCollection[nodeId] = trafficLight

    def addLink(self,linkId, lengthLane, numLanes, originNodeId, destinNodeId, type):
        link = Link(linkId, lengthLane, numLanes, originNodeId, destinNodeId, type)
        if type == Link.IN:
            self.inflowLinkCollection[linkId] = link
        elif type == Link.OUT:
            self.outflowLinkCollection[linkId]= link
        self.linkCollection[linkId] = link

class Node(object):
    
    SIZE = 24

    def __init__(self, 
                 id:int, 
                 position:Tuple[int,int],
                 isExit:bool, 
                 isControlled:bool
                ):
        self.nodeId = id
        self.x = position[0]
        self.y = position[1]
        self.inflowLinkIds  = []
        self.outflowLinkIds = []
        
        # binary bits to indicator status
        self.isExit = isExit
        self.isControlled = isControlled
    
    def center2corner(self):
        leftTopCornerPos = (self.x - Node.SIZE/2, self.y - Node.SIZE/2)
        size = (Node.SIZE, Node.SIZE)
        return (leftTopCornerPos, size)
    
    def __repr__(self):
        return f"Node{self.nodeId:2.0f}"
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.nodeId))
    
class Link(object):
    
    NORMAL = 0
    IN = 1
    OUT = -1 
    COLOR = (255,255,255)
    GRIDSIZE = 4
    
    def __init__(self, 
                 id: str, 
                 lengthLane:int,
                 numLanes:int,
                 originNodeId:int,
                 destinNodeId:int,
                 type:int,
                ): 
        self.linkId = id
        self.numLanes = numLanes
        self.lenLane = lengthLane
        self.lenGrid = 7 # meter
        self.numGrids = self.lenLane // self.lenGrid
        self.trafficMatrix = [[ 0 for _ in range(self.numGrids)] for _ in range(self.numLanes)] 
        self.binaryMatrix = np.zeros((self.numLanes, self.numGrids))
        assert len(self.trafficMatrix) == self.numLanes
        assert len(self.trafficMatrix[0]) == self.numGrids
        assert self.binaryMatrix.shape == (self.numLanes, self.numGrids)
        
        # connected nodes
        self.originNodeId = originNodeId
        self.destinNodeId = destinNodeId
        self.type = type # 0: normal, 1:inflow, -1:outflow

    def getFrontCarLane(self, numLane,):
        isFront = False
        veh = None

        for idx in [-1, -2, -3]:
            if isinstance(self.trafficMatrix[numLane][idx], Car):
                isFront = True
                veh = self.trafficMatrix[numLane][idx]
                # veh.seeTrafficLight = True
                break
                
        return isFront, veh

    def __repr__(self):
        return f"Link{self.linkId}"
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.linkId))       
    
class Car(object):
    
    MAX_SPEED = 3 
    IN_TrafficLight = True

    T_Car = 1
    T_Bus = 2
    T_Taxi = 3
    T_Heavy = 4
    T_Medium = 5
    
    def __init__(self, 
                 env, 
                 net,
                 id:int,
                 linkId:str, 
                 laneId:int, 
                 gridId:int,
                 type:int=1,
                 randomization:float=0.1,
                 laneChangeThres:float=0.2):
        self.env = env
        self.net = net
        self.vehId = id
        self.currentLinkId = linkId
        self.currentLane = laneId
        self.currentGrid = gridId
        self.currentSpeed = random.randint(a=2, b=Car.MAX_SPEED)
        self.randomization = randomization
        self.laneChangeThres = laneChangeThres
        self.type = type

        # binary state indicators
        self.seeTrafficLight = False
        self.seeRedLight = True
        self.leaveNetwork = None
        self.checkStatus()
        self.nextLinkId = None
        # setup the process for event
        self.action = self.env.process(self.run())
        
    def run(self):
        while (not self.leaveNetwork):
            # if not self.seeTrafficLight:
            if not self.seeTrafficLight:
                # in the link, perform cellular automata logic
                ##############################################
                # 1. compare current speed with desired speed:
                ##############################################
                targetSpeed = min(self.currentSpeed+1, Car.MAX_SPEED)
                ################################################
                # 2. compare current speed with safety distance:
                ################################################
                targetSpeed = min(targetSpeed, self.__getSafetyDistance(targetSpeed))
                ###################
                # 3. randomization:
                ###################
                if random.random() < self.randomization:
                    targetSpeed = max(0, targetSpeed-1)
                ####################
                # 4. perform action:
                ####################
                self.currentSpeed = targetSpeed
                oldGrid = self.currentGrid
                self.currentGrid += self.currentSpeed
                if self.currentSpeed != 0:
                    # update the traffic matrix
                    self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = \
                        self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][oldGrid]
                    self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][oldGrid] = 0
                    # update the binary matrix
                    self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid] = self.type
                    self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, oldGrid] = 0
                #################
                # 5. lane change:
                #################
                if random.random() > self.laneChangeThres and self.currentSpeed > 0:
                    if self.currentLane == 0 or (random.random() < 0.5 and self.currentLane == 1):
                        # case1: in the leftmost lane, check its right lane
                        # case2: in the middle lane, randomly change to its right lane
                        if self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane+1, self.currentGrid] == 0:
                            self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane+1][self.currentGrid] = \
                                self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid]
                            self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = 0
                            # update the binary matrix
                            self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane+1, self.currentGrid] = self.type
                            self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid] = 0  
                            self.currentLane += 1
                            self.currentSpeed = 0
                        elif self.currentLane == 2 or (random.random() >= 0.5 and self.currentLane == 1):
                        # case3: in the rightmost lane, check its left lane
                        # case4: in the middle lane, randomly change to its left lane
                            self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane-1][self.currentGrid] = \
                                self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid]
                            self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = 0
                            # update the binary matrix
                            self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane-1, self.currentGrid] = self.type
                            self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid] = 0  
                            self.currentLane -= 1  
                            self.currentSpeed = 0                          
                # # warning: stop in the link
                # if self.currentSpeed == 0:
                    # print(colored(f"{self} stops in link {self.currentLinkId, self.currentGrid} at {self.env.now}", 'red'))
                yield self.env.timeout(1)
                # check status
                self.checkStatus()
            else:
                if self.seeRedLight:
                    # currentLink = self.net.linkCollection[self.currentLinkId]
                    # currentNodeId = currentLink.destinNodeId
                    # currentNode = self.net.nodeCollection[currentNodeId]
                    # redLightTime = currentNode.greenTimes[currentNode.currentPhase]
                    self.currentSpeed = 0
                    yield self.env.timeout(1)
                else: # see green light:
                    passTime = 1
                    yield self.env.timeout(passTime)
                    if self.net.linkCollection[self.nextLinkId].trafficMatrix[self.currentLane][0] == 0:
                        self.net.linkCollection[self.nextLinkId].trafficMatrix[self.currentLane][0] = self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid]
                        self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = 0
                        self.net.linkCollection[self.nextLinkId].binaryMatrix[self.currentLane][0] = self.type
                        self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane][self.currentGrid] = 0
                        self.currentLinkId = self.nextLinkId
                        self.currentGrid = 0
                        self.seeTrafficLight = False
                        self.seeRedLight = False 
                self.checkStatus()
        
        print(colored(f"{self.__str__()} leaves Network", 'green'))
        self.net.carCollection.pop(self.vehId)
        self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = 0
        self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid] = 0
        self.net.numVehInSystem -= 1
        del self

    def __getSafetyDistance(self, speed) -> int:
        safeDistance = 0
        linkMaxGrid = self.net.linkCollection[self.currentLinkId].numGrids
        # first decide whether it will go outside the link
        if self.currentGrid + speed + 1 > linkMaxGrid:
            binaryVector = self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid+1:].copy() 
        else:
            binaryVector = self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid+1: self.currentGrid+1+speed].copy()
            assert binaryVector.shape == (speed,)
        for idx in range(binaryVector.shape[0]):
            if binaryVector[idx] == 0:
                safeDistance += 1
            else:
                break
        return safeDistance
          
    def checkStatus(self,):
        '''
        return:
            seeTrafficLight
                # check whether this car can see the traffic light
                    # 1. near the end of the link (remaining grid < current speed)
                    # 2. at the front of the lane
            leaveNetwork
                # check whether this car will leave the whole network?
                    # 1. near the end of the link (remaining grid < current speed)
                    # 2. in the outbound link
                    # 3. front vehicle
        '''
        currentLinkType = self.net.linkCollection[self.currentLinkId].type
        self.leaveNetwork = self.__isMyselfFrontCar() and self.__isStepOutsideLink() and currentLinkType == Link.OUT
        self.seeTrafficLight = True if self.currentGrid + 3 >= self.net.linkCollection[self.currentLinkId].numGrids else False
        # self.__isMyselfFrontCar() and self.__isStepOutsideLink()
        
    def __isStepOutsideLink(self,) -> bool:
        # check whether self will step outside of the link in the next step:
        # by comparing the current speed and remaining grids
        isStepOutsideLink = False
        linkMaxGrid = self.net.linkCollection[self.currentLinkId].numGrids
        if self.currentGrid >= linkMaxGrid-3:
            isStepOutsideLink = True
        return isStepOutsideLink
        
    def __isMyselfFrontCar(self,) -> bool:
        # check whether self is the front car in the current lane
        isFrontCar = False
        binaryVector = self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid+1:]
        if np.all(binaryVector == 0):
            isFrontCar = True
        return isFrontCar
        
    def __repr__(self):
        return f"Car{self.vehId}"
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.vehId))  

class TrafficLight(Node): 
    def __init__(self, id: int, env, net, position: Tuple[int, int], isExit: bool, isControlled: bool,
                 greenTimes:List[int]):
        super().__init__(id, position, isExit, isControlled)
        self.net = net
        # traffic control setups
        self.currentPhase = 0
        self.numPhases = 4
        self.greenTimes = greenTimes
        # try to apply actuated light control for west-east straight traffic flow.       
        self.controlledPhase = 2    
        assert len(self.greenTimes) == self.numPhases
        self.direction = OrderedDict()
        self.phaseTime = 0
        self.phaseTotalTime = self.greenTimes[self.currentPhase]
        self.env = env
        self.action = self.env.process(self.trafficLightControl())

        self.north = ((self.x-Node.SIZE//3, self.y-Node.SIZE//2), (Node.SIZE//3, Node.SIZE//6))
        self.south = ((self.x, self.y+Node.SIZE//3), (Node.SIZE//3, Node.SIZE//6))
        self.west  = ((self.x-Node.SIZE//2, self.y), (Node.SIZE//6, Node.SIZE//3))
        self.east  = ((self.x+Node.SIZE//3, self.y-Node.SIZE//3), (Node.SIZE//6, Node.SIZE//3))

    def trafficLightControl(self,):
        # retrieve all links and nodes necessary:
        westNodeId = self.direction['W']
        eastNodeId = self.direction['E']
        northNodeId= self.direction['N']
        southNodeId= self.direction['S']
        westInLinkId = 'I'+str(westNodeId)+'O'+str(self.nodeId)
        eastInLinkId = 'I'+str(eastNodeId)+'O'+str(self.nodeId)
        northInLinkId= 'I'+str(northNodeId)+'O'+str(self.nodeId)
        southInLinkId= 'I'+str(southNodeId)+'O'+str(self.nodeId)
        westLink = self.net.linkCollection[westInLinkId]
        eastLink = self.net.linkCollection[eastInLinkId]
        northLink= self.net.linkCollection[northInLinkId]
        southLink= self.net.linkCollection[southInLinkId]
        
        # control the vehicle encountering the traffic light
        while True:
            if self.currentPhase == 0: # North-south straight green
                # North inflow
                isFront, car = northLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                isFront, car = northLink.getFrontCarLane(1) # green
                if isFront:
                    car.seeRedLight = False
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                isFront, car = northLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                # South inflow
                isFront, car = southLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                isFront, car = southLink.getFrontCarLane(1) # green
                if isFront:
                    car.seeRedLight = False
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                isFront, car = southLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                # Western inflow
                isFront, car = westLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                isFront, car = westLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                isFront, car = westLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                # Eastern inflow
                isFront, car = eastLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True                
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                isFront, car = eastLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                isFront, car = eastLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 

            elif self.currentPhase == 1: # North-south turnleft green
                # North inflow
                isFront, car = northLink.getFrontCarLane(0) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                isFront, car = northLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                isFront, car = northLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                # South inflow
                isFront, car = southLink.getFrontCarLane(0) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                isFront, car = southLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                isFront, car = southLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                # Western inflow
                isFront, car = westLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                isFront, car = westLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                isFront, car = westLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                # Eastern inflow
                isFront, car = eastLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                isFront, car = eastLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                isFront, car = eastLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 

            elif self.currentPhase == 2: # West-East straight green
                # North inflow
                isFront, car = northLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                isFront, car = northLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                isFront, car = northLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                # South inflow
                isFront, car = southLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                isFront, car = southLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                isFront, car = southLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                # Western inflow
                isFront, car = westLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                isFront, car = westLink.getFrontCarLane(1) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                isFront, car = westLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                # Eastern inflow
                isFront, car = eastLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                isFront, car = eastLink.getFrontCarLane(1) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                isFront, car = eastLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 

            elif self.currentPhase == 3: # West-East turnleft green
                # North inflow
                isFront, car = northLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                isFront, car = northLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                isFront, car = northLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                # South inflow
                isFront, car = southLink.getFrontCarLane(0) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                isFront, car = southLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                isFront, car = southLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                # Western inflow
                isFront, car = westLink.getFrontCarLane(0) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                isFront, car = westLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(eastNodeId) 
                isFront, car = westLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                # Eastern inflow
                isFront, car = eastLink.getFrontCarLane(0) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(southNodeId) 
                isFront, car = eastLink.getFrontCarLane(1) # red
                if isFront:
                    car.currentSpeed = 0
                    car.seeRedLight = True
                    car.seeTrafficLight = True
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(westNodeId) 
                isFront, car = eastLink.getFrontCarLane(2) # green
                if isFront:
                    car.seeRedLight = False
                    car.nextLinkId = 'I'+str(self.nodeId)+'O'+str(northNodeId) 
                
            # step forward 1 second
            yield self.env.timeout(1)
            self.phaseTime += 1
            if self.phaseTime == self.phaseTotalTime:
                # loop through all four phases: 0 -> 1 -> 2 -> 3 -> 0 ...
                oldPhase = self.currentPhase
                if self.currentPhase == 3:
                    self.currentPhase = 0
                else:
                    self.currentPhase += 1     
                # reset the phaseTime and phaseTotalTime
                self.phaseTime = 0
                self.phaseTotalTime = self.greenTimes[self.currentPhase]
                print(self, f"change phase {oldPhase} to new phase {self.currentPhase} at {self.env.now}")       

    def lightPositions(self):
        '''
        Return a dictionary that contains the base positions of traffic light 
        Later, the green light is applied to update them
        '''
        return {'N':self.north, 'S':self.south, 'W':self.west, 'E':self.east,}
    
    def getTrafficLightConditions(self,):
        """
        Return back a dictionary that contains the position of each green light
        """
        lights = None
        if self.currentPhase == 0:
        # NS-turnleft
            lights = {
                'N': ((self.x-Node.SIZE//3, self.y-Node.SIZE//2), (Node.SIZE//6, Node.SIZE//6)),
                'S': ((self.x+Node.SIZE//6, self.y+Node.SIZE//3), (Node.SIZE//6, Node.SIZE//6)),
            }
        elif self.currentPhase == 1: 
        # NS-straight
            lights = {
                'N': ((self.x-Node.SIZE//6, self.y-Node.SIZE//2), (Node.SIZE//6, Node.SIZE//6)),
                'S': ((self.x, self.y+Node.SIZE//3), (Node.SIZE//6, Node.SIZE//6)),
            }
        elif self.currentPhase == 2:
        # WE-straight
            lights = {
                'W': ((self.x-Node.SIZE//2, self.y+Node.SIZE//6), (Node.SIZE//6, Node.SIZE//6)),
                'E': ((self.x+Node.SIZE//2, self.y-Node.SIZE//6), (Node.SIZE//6, Node.SIZE//6)),
            }
        elif self.currentPhase == 3:
            lights = {
                'W': ((self.x-Node.SIZE//2, self.y), (Node.SIZE//6, Node.SIZE//6)),
                'E': ((self.x+Node.SIZE//2, self.y), (Node.SIZE//6, Node.SIZE//6)),
            }
        return lights

    def __repr__(self):
        return f"TrafficLight{self.nodeId}"
    def __str__(self):
        return f"TrafficLight{self.nodeId}"
    def __hash__(self):
        return super().__hash__()

if __name__ == "__main__":
    # test
    env = simpy.Environment()
    sim = Simulation(env=env, numInitVehs=50)
    sim.initToyNetwork()
    sim.simulate(until=100)
