import sys
import time
import random
import numpy as np
import simpy
import pygame
from collections import OrderedDict
from typing import Tuple, List
from utils import Color


class Simulation(object):

    pauseTime = 0.3


    def __init__(self,
                 env,
                ):
        self.env = env
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.net = Network(env, self.screen)
        self.action = self.env.process(self.render())
        # simulation setup
        self.T = None

    def simulate(self, until):
        self.T = until
        self.env.run(until)
        print(f"LOGGING: finish the simulation in {self.T} seconds")

    def render(self):
        # a simulation process for:
        # 1. checking game events
        while True:
            # if self.env.now < self.T:
            #     pygame.quit()
            #     sys.quit()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.quit()
            # time.sleep(Simulation.pauseTime)
            yield self.env.timeout(1)
        
    def initToyNetwork(self, numInitVehs=1):
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
        print(f"LOGGING: initialize {len(self.net.nodeCollection):2.0f} nodes into network")

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
        print(f"LOGGING: initialize {len(self.net.linkCollection):2.0f} links into network")

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
        self.net.initCars(numInitVehs)
        assert len(self.net.carCollection) == numInitVehs
        assert self.net.numVehInSystem == numInitVehs
        print(f"LOGGING: initialize {numInitVehs:2.0f}  cars into network")

class Network(object):
       
    def __init__(self, 
                 env,
                 screen,
                 height=600,
                 width=800,
                 dt=0.1):

        # Pygame setups
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
            yield self.env.timeout(1)

    def __gameStep(self):
        # draw background:
        self.screen.fill(self.backgroundColor)
        # draw nodes:
        for nodeId, node in self.nodeCollection.items():
            pygame.draw.rect(self.screen, Color.WHITE, node.center2corner())
        # draw link and vehicles together:
            # 1. collect all binaryMatrix
            # 2. assign the position of rect grid
            # 3. plot
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
            link1 = self.linkCollection[linkId1].binaryMatrix
            link2 = self.linkCollection[linkId2].binaryMatrix
            link2 = np.flip(link2, axis=1)
            assert link1.shape == link2.shape
            if (o, d) in [(1,2), (41,1), (32,1), (31,2),]:
                dualBinaryMatrix = np.concatenate([link2, link1])
            else: # if (o, d) in [(11,1), (12,2)]:
                dualBinaryMatrix = np.concatenate([link1, link2])
            assert dualBinaryMatrix.shape == (link1.shape[0]*2, link1.shape[1])
            if (o, d) == (21,2):
                dualBinaryMatrix = np.flip(dualBinaryMatrix, axis=1)
            self.matrixCollection[(o,d)] = dualBinaryMatrix.copy()
            (originPos, destinPos) = positions[(o,d)]
            if (o,d) in [(31,2), (32,1)]:
                dualBinaryMatrix = np.flip(dualBinaryMatrix, axis=1)
                self.matrixCollection[(o,d)] = dualBinaryMatrix.copy()
            if (o,d) in [(11,1), (12,2), (31,2), (32,1)]:
                rows = 50
                cols = 6
            else:
                rows = 6
                cols = 50
            if abs(originPos[0]-destinPos[0]) > abs(originPos[1]-destinPos[1]):
                # 横长竖短
                size = (50*Link.GRIDSIZE, Node.SIZE)
            else:
                dualBinaryMatrix = dualBinaryMatrix.T
                self.matrixCollection[(o,d)] = dualBinaryMatrix
                # 横短竖长
                size = (Node.SIZE, 50*Link.GRIDSIZE)
            topLeftCornerPos = positions[(o,d)][0]
            self.__draw_grid(o, d, rows, cols, topLeftCornerPos)
        pygame.display.flip()

    def __draw_grid(self, o, d, rows, cols, topLeftCornersPos):
        offset_x, offset_y = topLeftCornersPos
        matrix = self.matrixCollection[(o,d)]
        for row in range(rows):
            for col in range(cols):
                x = col * Link.GRIDSIZE + offset_x
                y = row * Link.GRIDSIZE + offset_y
                if matrix[row, col] == 1:
                    color = Color.RED
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE))
                else:
                    color = Color.BLACK
                    pygame.draw.rect(self.screen, color, (x, y, Link.GRIDSIZE, Link.GRIDSIZE), width=0)

    def initCars(self, numInitVehs=3):
        for vehId in range(numInitVehs):
            isSpawn = False
            while(not isSpawn):
                linkId = random.choice(list(self.linkCollection.keys()))
                laneId = random.randint(a=0, b=self.linkCollection[linkId].numLanes-1)
                gridId = random.randint(a=0, b=self.linkCollection[linkId].numGrids//2)
                if self.linkCollection[linkId].trafficMatrix[laneId][gridId] == 0:
                    # is empty, spawn the car
                    self.addCar(vehId, linkId, laneId, gridId)
                    isSpawn = True
        
    def addCar(self, vehId, linkId, laneId, gridId):
        car = Car(self.env, self, vehId, linkId, laneId, gridId)
        self.numVehInSystem += 1
        self.totalVeh += 1
        self.linkCollection[linkId].trafficMatrix[laneId][gridId] = car
        self.linkCollection[linkId].binaryMatrix[laneId, gridId] = 1
        self.carCollection[vehId] = car
    
    def addNode(self, nodeId:int, position:Tuple[int,int], isExit:bool, isControlled:bool,):
        node = Node(nodeId, position, isExit, isControlled)
        self.nodeCollection[nodeId] = node
        
    def addTrafficLightNode(self, nodeId:int, position:Tuple[int,int], isExit:bool, isControlled:bool,):
        trafficLight = TrafficLight(nodeId, self.env, self, position, isExit, isControlled, greenTimes=[8,6,4,4])
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
    COLOR = (0,0,0)

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
        self.originNodeId = None
        self.destinNodeId = None
        self.type = type # 0: normal, 1:inflow, -1:outflow
    #TODO: identify the front car for the lane
    def getFrontCarLane(self, numLane,):
        isFront = False
        veh = None
        return (isFront, veh)
    
    def __repr__(self):
        return f"Link{self.linkId}"
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.linkId))       
    
class Car(object):
    
    MAX_SPEED = 3 
    IN_TrafficLight = True
    
    def __init__(self, 
                 env, 
                 net,
                 id:int,
                 linkId:str, 
                 laneId:int, 
                 gridId:int,
                 randomization:float=0.1):
        self.env = env
        self.net = net
        self.vehId = id
        self.currentLinkId = linkId
        self.currentLane = laneId
        self.currentGrid = gridId
        self.currentSpeed = random.randint(a=2, b=Car.MAX_SPEED)
        self.randomization = randomization
        
        # binary state indicators
        self.seeTrafficLight = None
        self.leaveNetwork = None
        self.checkStatus()
        
        # setup the process for event
        self.action = self.env.process(self.run())
        
    def run(self):
        while (not self.leaveNetwork):
            if not self.seeTrafficLight:
                # in the link, perform cellular automata logic
                # 1. compare current speed with desired speed:
                targetSpeed = min(self.currentSpeed, Car.MAX_SPEED)
                # 2. compare current speed with safety distance:
                targetSpeed = min(targetSpeed, self.__getSafetyDistance(targetSpeed))
                # 3. randomization:
                if random.random() < self.randomization:
                    targetSpeed = max(0, targetSpeed-1)
                # 4. perform action:
                # update the field inside the object
                self.currentSpeed = targetSpeed
                oldGrid = self.currentGrid
                self.currentGrid += self.currentSpeed
                if self.currentSpeed != 0:
                    # update the traffic matrix
                    self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = \
                        self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][oldGrid]
                    self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][oldGrid] = 0
                    # update the binary matrix
                    self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid] = 1
                    self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, oldGrid] = 0
                
                # update time
                print(f"{self} driving in link {self.currentLinkId, self.currentGrid} at {self.env.now}")
                yield self.env.timeout(1)
                
                # check status
                self.checkStatus()
                
            else:
                # in the intersection
                # based on the red / green light
                try:
                    #TODO: implement the logic inside intersection when light is green.
                    raise NotImplementedError
                    self.__intersection()

                except simpy.Interrupt:
                    print(self, f"Encounter RED light and top")
                yield self.env.timeout(10)
        print("Leave Network")
        raise NotImplementedError()

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
        self.seeTrafficLight = self.__isMyselfFrontCar() and self.__isStepOutsideLink()
        
    def __isStepOutsideLink(self,) -> bool:
        # check whether self will step outside of the link in the next step:
        # by comparing the current speed and remaining grids
        isStepOutsideLink = False
        linkMaxGrid = self.net.linkCollection[self.currentLinkId].numGrids
        if self.currentGrid + self.currentSpeed + 1 > linkMaxGrid:
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

        self.env = env
        self.action = self.env.process(self.trafficLightControl())

    def trafficLightControl(self,):
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
        #TODO: acturated light control
        while True:    
            if self.currentPhase == 0:
                # North-south straight green
                # set the front cars in other 3 phases to stop:
                # west-straight
                isFront, car = westLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # west-turnleft
                isFront, car = westLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # east-straight
                isFront, car = eastLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # east-turnleft
                isFront, car = eastLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # north-turnleft
                isFront, car = northLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # south-turnleft
                isFront, car = southLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
            elif self.currentPhase == 1:
                # North-south turn-left green
                # set the front cars in other 3 phases to stop:
                # west-straight
                isFront, car = westLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # west-turnleft
                isFront, car = westLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # east-straight
                isFront, car = eastLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # east-turnleft
                isFront, car = eastLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # north-straight
                isFront, car = northLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # south-straight
                isFront, car = southLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
            elif self.currentPhase == 2:
                # West-east straight green
                # set the front cars in other 3 phases to stop:
                # north-straight
                isFront, car = northLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # north-turnleft
                isFront, car = northLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # south-straight
                isFront, car = southLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # south-turnleft
                isFront, car = southLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # west-turnleft
                isFront, car = northLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # east-turnleft
                isFront, car = southLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
            elif self.currentPhase == 3:
                # West-east turn-left green
                # set the front cars in other 3 phases to stop:
                # perform green time in this phase
                # north-straight
                isFront, car = northLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # north-turnleft
                isFront, car = northLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # south-straight
                isFront, car = southLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # south-turnleft
                isFront, car = southLink.getFrontCarLane(numLane=0)
                if isFront:
                    car.action.interupt()
                # west-straight
                isFront, car = northLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
                # east-straight
                isFront, car = southLink.getFrontCarLane(numLane=1)
                if isFront:
                    car.action.interupt()
            yield self.env.timeout(self.greenTimes[self.currentPhase])
            # self forward
            self.__stepForwardPhase()

    # helper function for trafficLight class  
    def __stepForwardPhase(self):
        # loop through all four phases: 0 -> 1 -> 2 -> 3 -> 0 ...
        oldPhase = self.currentPhase
        if self.currentPhase == 3:
            self.currentPhase = 0
        else:
            self.currentPhase += 1     
        # print(self, f"change phase {oldPhase} to new phase {self.currentPhase}")

    def __repr__(self):
        return f"TrafficLight{self.nodeId}"
    def __str__(self):
        return f"TrafficLight{self.nodeId}"
    def __hash__(self):
        return super().__hash__()

# test
env = simpy.Environment()
sim = Simulation(env=env)
sim.initToyNetwork()

# print(len(sim.net.nodeCollection))
# print(len(sim.net.linkCollection))
# print(len(sim.net.carCollection))

sim.simulate(until=30)
