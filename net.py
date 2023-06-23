import time
import pickle
import random
import numpy as np
import pygame
from pygame.locals import *

from typing import Tuple, List
from collections import OrderedDict
from utils import Color, logging
from athens import *
from car import Car

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
        self.matrixCollection = OrderedDict()
        self.numVehInSystem = 0
        self.totalVeh = 0 
        self.total_emission = 0
        self.car_emission = 0
        self.bus_emission = 0
        self.taxi_emission = 0
        self.heavy_emission = 0
        self.medium_emission = 0
        self.distances = {
            T_Car    : 0, 
            T_Bus    : 0, 
            T_Taxi   : 0, 
            T_Heavy  : 0, 
            T_Medium : 0,
        }
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
            if self.env.now == 1799:
                type = {1:"Car", 2:"Bus", 3:"Taxi", 4:"H_Veh", 5:"M_Veh"}
                logging(msg=f"CO2 Emission by Type Car: {self.car_emission:10.0f}",
                        color='yellow')
                logging(msg=f"CO2 Emission by Type Bus: {self.bus_emission:10.0f}",
                        color='yellow')                
                logging(msg=f"CO2 Emission by Type Taxi: {self.taxi_emission:10.0f}",
                        color='yellow')
                logging(msg=f"CO2 Emission by Type H_Veh: {self.heavy_emission:10.0f}",
                        color='yellow')
                logging(msg=f"CO2 Emission by Type M_Veh: {self.medium_emission:10.0f}",
                        color='yellow')                
                logging(msg=f"CO2 Emission in total: {self.total_emission:10.0f}",
                        color='yellow') 
                with open("./emission.pickle", 'rb') as file:
                     emission_dict = pickle.load(file)
                emission_dict['car'].append(self.car_emission)
                emission_dict['bus'].append(self.bus_emission)
                emission_dict['taxi'].append(self.taxi_emission)
                emission_dict['heavy'].append(self.heavy_emission)
                emission_dict['medium'].append(self.medium_emission)
                with open("./emission.pickle", 'wb') as file:
                    pickle.dump(emission_dict, file)

            ###################
            # vehicle generator
            ###################
            # for linkId, inflow in self.inflowLinkCollection.items():
            #     link = self.linkCollection[linkId]
            #     numLanes = link.numLanes
            #     if numLanes == 5: # 主路
            #          for laneId in range(numLanes):
            #                 if random.random() > 0.75 and link.binaryMatrix[laneId, 0] == 0:
            #                     vehId = self.totalVeh
            #                     if random.random() > 0.8:
            #                         typeId = T_Car
            #                     else:
            #                         typeId = random.choice([i for i in range(2,6)])
            #                     self.addCar(vehId, linkId, laneId, 0, typeId)
            #                     logging(msg=f'car{vehId} spawns in the Network',
            #                         color='blue')
            #     elif numLanes == 1: # 支路
            #         if random.random() > 0.95 and link.binaryMatrix[0, 0] == 0:
            #             vehId = self.totalVeh
            #             typeId = random.choice([i for i in range(1,6)])
            #             self.addCar(vehId, linkId, 0, 0, typeId)
            #             logging(msg=f'car{vehId} spawns in the Network',
            #                 color='blue')
            for linkId, inflow in self.inflowLinkCollection.items():
                if random.random() > 0.76:
                        vehId = self.totalVeh 
                        isSpawn = False
                        while(not isSpawn):
                            linkId = random.choice(list(self.linkCollection.keys()))
                            laneId = random.randint(a=0, b=self.linkCollection[linkId].numLanes-1)
                            gridId = 0 # random.randint(a=0, b=self.linkCollection[linkId].numGrids-1)
                            prob_Type = random.random()
                            if prob_Type <= 0.90:
                                type = T_Car
                            elif prob_Type <= 0.95:
                                type = T_Taxi
                            elif prob_Type <= 0.96:
                                type = T_Heavy
                            elif prob_Type <= 0.985:
                                 type = T_Bus
                            else:
                                 type = T_Medium
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
        
        #########################
        # draw the traffic light:
        #########################
        # for tfId, tf in self.trafficLightCollection.items():
        #     lights = tf.lightPositions()
        #     for direction, positions in lights.items():
        #         pygame.draw.rect(self.screen, Color.RED, positions)
        #     lights = tf.getTrafficLightConditions()
        #     for direction, positions in lights.items():
        #         pygame.draw.rect(self.screen, Color.GREEN, positions)        
        
        ##################################
        # draw link and vehicles together:
        ##################################
        for linkId, link in self.linkCollection.items():
            binaryMatrix = link.binaryMatrix.copy()
            leftTopCornerPosition = link_Infos[linkId][5]
            # Case 1: from right to left // 5 lanes
            if linkId in ['i2o1','i3o2','i4o3',
                          'i21o4','i1o42',]:
                binaryMatrix = np.flip(binaryMatrix)
                rows = 5
                cols = link.numGrids
            # Case 2: from left to right // 5 lanes
            elif linkId in ['i6o5','i7o6','i8o7','i9o8',
                          'i5o22','i41o9']:
                # binaryMatrix = np.flip(binaryMatrix)
                rows = 5
                cols = link.numGrids
            elif linkId in ['i1o11', 'i9o1', 'i34o9', 
                            'i2o12', 'i7o2', 'i32o7',
                            'i4o13', 'i5o4', 'i31o5',]:
                binaryMatrix = np.rot90(binaryMatrix, k=1)
                rows = link.numGrids
                cols = 1
            else:
                binaryMatrix = np.rot90(binaryMatrix, k=3)
                rows = link.numGrids
                cols = 1
            self.__draw_grid(rows, cols, leftTopCornerPosition, binaryMatrix)

        
        #############
        # draw nodes:
        #############
        for nodeId, node in self.nodeCollection.items():
            pygame.draw.rect(self.screen, Color.BLACK, node.center2corner())

        #######################
        # add text information:
        #######################  
        self.__draw_text()

        ####################
        # update the screen:
        #################### 
        pygame.display.flip()

    def __draw_grid(self, rows, cols, topLeftCornersPos, binaryMatrix):
        """
        Display the matrix for each couple of links:
        @ rows: #rows: depends on the shape of matrix
        @ cols: #cols: depends on the shape of matrix
        @ topLeftCornersPos: the position of left-top corner point
        """
        # retrieve the position and matrix:
        offset_x, offset_y = topLeftCornersPos
        # draw each cell in the matrix row by col
        for row in range(rows):
            for col in range(cols):
                x = col * LINK_GRIDSIZE + offset_x
                y = row * LINK_GRIDSIZE + offset_y
                # specifiy the red cell for the existence of vehicle
                if binaryMatrix[row, col] == 1:
                    color = Color.PINK
                    pygame.draw.rect(self.screen, color, (x, y, LINK_GRIDSIZE, LINK_GRIDSIZE))
                elif binaryMatrix[row, col] == 2:
                    color = Color.RED
                    pygame.draw.rect(self.screen, color, (x, y, LINK_GRIDSIZE, LINK_GRIDSIZE))
                elif binaryMatrix[row, col] == 3:
                    color = Color.LIGHT_BLUE
                    pygame.draw.rect(self.screen, color, (x, y, LINK_GRIDSIZE, LINK_GRIDSIZE))
                elif binaryMatrix[row, col] == 4:
                    color = Color.BLUE
                    pygame.draw.rect(self.screen, color, (x, y, LINK_GRIDSIZE, LINK_GRIDSIZE))
                elif binaryMatrix[row, col] == 5:
                    color = Color.YELLOW
                    pygame.draw.rect(self.screen, color, (x, y, LINK_GRIDSIZE, LINK_GRIDSIZE))
                elif binaryMatrix[row, col] == 6:
                    color = Color.DARK_RED
                    pygame.draw.rect(self.screen, color, (x, y, LINK_GRIDSIZE, LINK_GRIDSIZE))
                # otherwise: black cell for empty cell
                else:
                    color = Color.GREY
                    pygame.draw.rect(self.screen, color, (x, y, LINK_GRIDSIZE, LINK_GRIDSIZE), width=0)

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

        type = {1:"Car", 2:"Bus", 3:"Taxi", 4:"H_Veh", 5:"M_Veh"}
        # HBEFA Emission factors
        factors = {1:160.803, 2:926.564, 3:223.166, 4:880.849, 5:680.631}
        total_emission = 0
        for typeId, distance in self.distances.items():
            vehType_emission = distance*7*factors[typeId]/1000
            total_emission += vehType_emission
            if typeId == T_Car:
                 self.car_emission = vehType_emission
            elif typeId == T_Bus:
                 self.bus_emission = vehType_emission
            elif typeId == T_Taxi:
                 self.taxi_emission = vehType_emission
            elif typeId == T_Heavy:
                 self.heavy_emission = vehType_emission
            elif typeId == T_Medium:
                 self.medium_emission = vehType_emission                        
            
            textLine = f"CO2 Emission by Type {type[typeId]}: {vehType_emission:10.0f}"
            text_surface = font.render(textLine, True, font_color)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (10, 15*typeId + 25)
            self.screen.blit(text_surface, text_rect)
        
        self.total_emission = total_emission
        textLine3 = f"CO2 Emission in total: {total_emission:10.0f}"
        text_surface3 = font.render(textLine3, True, font_color)
        text_rect3 = text_surface3.get_rect()
        text_rect3.topleft = (10, 115)
        self.screen.blit(text_surface3, text_rect3)


    def initCars(self, numInitVehs):
        for vehId in range(numInitVehs):
            isSpawn = False
            while(not isSpawn):
                linkId = random.choice(list(self.linkCollection.keys()))
                laneId = random.randint(a=0, b=self.linkCollection[linkId].numLanes-1)
                gridId = random.randint(a=0, b=self.linkCollection[linkId].numGrids-1)
                typeId = random.choice([i for i in range(1,6)])
                if self.linkCollection[linkId].trafficMatrix[laneId][gridId] == 0:
                    # is empty, spawn the car
                    self.addCar(vehId, linkId, laneId, gridId, typeId)
                    isSpawn = True

    def addCar(self, vehId, linkId, laneId, gridId, type):
        car = Car(self.env, self, vehId, linkId, laneId, gridId, type=type)
        self.numVehInSystem += 1
        self.totalVeh += 1
        self.linkCollection[linkId].trafficMatrix[laneId][gridId] = car
        self.linkCollection[linkId].binaryMatrix[laneId, gridId] = type
        self.carCollection[vehId] = car
    
    def addNode(self, nodeId:int, position:Tuple[int,int], isExit:bool, isControlled:bool, shape:str):
        node = Node(nodeId, position, isExit, isControlled, shape)
        self.nodeCollection[nodeId] = node
        
    def addTrafficLightNode(self, nodeId:int, position:Tuple[int,int], isExit:bool, isControlled:bool, shape:str):
        trafficLight = TrafficLight(nodeId, self.env, self, position, isExit, isControlled, shape=shape)
        self.nodeCollection[nodeId] = trafficLight
        self.trafficLightCollection[nodeId] = trafficLight

    def addLink(self,linkId, lengthLane, numLanes, originNodeId, destinNodeId, type):
        link = Link(linkId, lengthLane, numLanes, originNodeId, destinNodeId, type)
        if type == LINK_IN: # inflow
            self.inflowLinkCollection[linkId] = link
        elif type == LINK_OUT: # outflow
            self.outflowLinkCollection[linkId]= link
        self.linkCollection[linkId] = link

class Node(object):
    
    def __init__(self, 
                 id:int, 
                 position:Tuple[int,int],
                 isExit:bool, 
                 isControlled:bool,
                 shape: str,
                ):
        self.nodeId = id
        self.x = position[0]
        self.y = position[1]
        self.inflowLinkIds  = []
        self.outflowLinkIds = []
        self.shape = shape
        # binary bits to indicator status
        self.isExit = isExit
        self.isControlled = isControlled
    
    def center2corner(self):
        """
        Given the CenterPosition of one node, return its left-top corner position.
        """
        if self.shape == "RECT": # traffic light 
            leftTopCornerPos = (self.x - NODE_WIDTH//2, self.y - NODE_HEIGHT//2)
            size = (NODE_WIDTH, NODE_HEIGHT)
        elif self.shape == "SQUARE":
            leftTopCornerPos = (self.x - NODE_SIZE//2, self.y - NODE_SIZE//2)
            size = (NODE_SIZE, NODE_SIZE)            
        return (leftTopCornerPos, size)
    
    def __repr__(self):
        return f"Node{self.nodeId:2.0f}"
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.nodeId))

class TrafficLight(Node): 
    def __init__(self, id: int, env, net, position: Tuple[int, int], isExit: bool, isControlled: bool, shape:str):
        super().__init__(id, position, isExit, isControlled, shape)
        self.net = net
        self.currentPhase = 0
        self.numPhases = None
        self.greenTimes = None
        self.direction = OrderedDict()
        self.leftTurnThreshold = 0.8
        self.setDirections(tf_Directions[self.nodeId])
        self.setPhase(tf_Phases[self.nodeId])
        self.phaseUsedTime = 0
        self.phaseTotalTime = self.greenTimes[self.currentPhase]
        self.env = env
        self.action = self.env.process(self.trafficLightControl())

    def trafficLightControl(self,):
        while True:
            # retrieve the connecting links:
            self.upstreamM_NodeId = self.direction['UP_Mainroad']
            self.upstreamM_LinkId = 'i'+str(self.upstreamM_NodeId)+'o'+str(self.nodeId)
            self.upstreamM_Link = self.net.linkCollection[self.upstreamM_LinkId]

            self.downstreamM_NodeId = self.direction['DOWN_Mainroad']
            self.downstreamM_LinkId = 'i'+str(self.nodeId)+'o'+str(self.downstreamM_NodeId)
            self.downstreamM_Link = self.net.linkCollection[self.downstreamM_LinkId]

            if 'DOWN_Branch' in self.direction.keys():
                self.downstreamB_NodeId = self.direction['DOWN_Branch']
                self.downstreamB_LinkId = 'i'+str(self.nodeId)+'o'+str(self.downstreamB_NodeId)
                self.downstreamB_Link = self.net.linkCollection[self.downstreamB_LinkId]

            if 'UP_Branch' in self.direction.keys():
                self.upstreamB_NodeId = self.direction['UP_Branch']
                self.upstreamB_LinkId = 'i'+str(self.upstreamB_NodeId)+'o'+str(self.nodeId)
                self.upstreamB_Link = self.net.linkCollection[self.upstreamB_LinkId]
            
            # Case1: two phases: <-
            if self.nodeId in [1,2,4]:
                numLanes = 5
                # Main flow phase
                if self.currentPhase == 0:
                    # Main flow leg
                    for laneId in range(5):
                        isFront, car = self.upstreamM_Link.getFrontCarLane(laneId)
                        if isFront and laneId == 4: # green // turn
                                car.seeRedLight = False
                                car.seeTrafficLight = True
                                car.nextLinkId = self.downstreamB_LinkId 
                                car.nextLane = 0
                        elif isFront and laneId < 4: # green // straight
                                car.seeRedLight = False
                                car.seeTrafficLight = True
                                car.nextLinkId = self.downstreamM_LinkId
                    # Branch flow leg
                    isFront, car = self.upstreamB_Link.getFrontCarLane(0)
                    if isFront:
                        car.currentSpeed = 0
                        car.seeRedLight = True
                        car.seeTrafficLight = True
                        car.nextLinkId = self.downstreamM_LinkId
                # Branch flow phase: 
                elif self.currentPhase == 1:
                    for laneId in range(5):
                        # Main flow leg
                        isFront, car = self.upstreamM_Link.getFrontCarLane(laneId)
                        if isFront and laneId == 0: # green // turn
                                car.currentSpeed = 0
                                car.seeRedLight = True
                                car.seeTrafficLight = True
                                car.nextLinkId = self.downstreamB_LinkId 
                        elif isFront and laneId > 0: # green // straight
                                car.currentSpeed = 0
                                car.seeRedLight = True
                                car.seeTrafficLight = True
                                car.nextLinkId = self.downstreamM_LinkId
                    # Branch flow leg
                    isFront, car = self.upstreamB_Link.getFrontCarLane(0)
                    if isFront:
                        car.seeRedLight = False
                        car.seeTrafficLight = True
                        car.nextLinkId = self.downstreamM_LinkId
            # Case2: two phases: ->
            elif self.nodeId in [5,7,9]:
                numLanes = 5
                # Main flow phase 
                if self.currentPhase == 0:
                    # Main flow leg
                    for laneId in range(5):
                        isFront, car = self.upstreamM_Link.getFrontCarLane(laneId)
                        if isFront and laneId == 0: # green // turn
                                car.seeRedLight = False
                                car.seeTrafficLight = True
                                car.nextLinkId = self.downstreamM_LinkId
                        elif isFront and laneId > 0: # green // straight
                                car.seeRedLight = False
                                car.seeTrafficLight = True
                                car.nextLinkId = self.downstreamM_LinkId
                    # Branch flow leg
                    isFront, car = self.upstreamB_Link.getFrontCarLane(0)
                    if isFront:
                        car.currentSpeed = 0
                        car.seeRedLight = True
                        car.seeTrafficLight = True
                        car.nextLinkId = self.downstreamB_LinkId
                elif self.currentPhase == 1:
                    for laneId in range(5):
                        # Main flow leg
                        isFront, car = self.upstreamM_Link.getFrontCarLane(laneId)
                        if isFront and laneId == 0: # green // turn
                                car.currentSpeed = 0
                                car.seeRedLight = True
                                car.seeTrafficLight = True
                                car.nextLinkId = self.downstreamB_LinkId 
                        elif isFront and laneId > 0: # green // straight
                                car.currentSpeed = 0
                                car.seeRedLight = True
                                car.seeTrafficLight = True
                                car.nextLinkId = self.downstreamM_LinkId
                    # Branch flow leg
                    isFront, car = self.upstreamB_Link.getFrontCarLane(0)
                    if isFront:
                        car.seeRedLight = False
                        car.seeTrafficLight = True
                        car.nextLinkId = self.downstreamB_LinkId

            # Case3: one phase: node 3            
            elif self.nodeId == 3:
                numLanes = 5
                # Main flow phase
                # Main flow leg
                for laneId in range(5):
                    isFront, car = self.upstreamM_Link.getFrontCarLane(laneId)
                    if isFront and laneId == 0: # green // turn
                            car.seeRedLight = False
                            car.seeTrafficLight = True
                            if random.random() > self.leftTurnThreshold:
                                car.nextLinkId = self.downstreamB_LinkId 
                            else:
                                 car.nextLinkId = self.downstreamM_LinkId
                    elif isFront and laneId > 0: # green // straight
                            car.seeRedLight = False
                            car.seeTrafficLight = True
                            car.nextLinkId = self.downstreamM_LinkId
            # Case4: one phase: node 3            
            elif self.nodeId == 6:
                # Main flow phase
                # Main flow leg
                for laneId in range(5):
                    isFront, car = self.upstreamM_Link.getFrontCarLane(laneId)
                    if isFront and laneId == 0: # green // turn
                            car.seeRedLight = False
                            car.seeTrafficLight = True
                            car.nextLinkId = self.downstreamM_LinkId 
                    elif isFront and laneId > 0: # green // straight
                            car.seeRedLight = False
                            car.seeTrafficLight = True
                            car.nextLinkId = self.downstreamM_LinkId
                    # Branch flow leg
                    isFront, car = self.upstreamB_Link.getFrontCarLane(0)
                if isFront:
                    car.seeRedLight = False
                    car.seeTrafficLight = True
                    car.nextLinkId = self.downstreamM_LinkId                
            elif self.nodeId == 8:
                # Main flow phase
                # Main flow leg
                for laneId in range(5):
                    isFront, car = self.upstreamM_Link.getFrontCarLane(laneId)
                    if isFront and laneId == 4: # green // turn
                            car.seeRedLight = False
                            car.nextLane = 0
                            car.seeTrafficLight = True
                            car.nextLinkId = self.downstreamB_LinkId 
                    elif isFront and laneId < 4: # green // straight
                            car.seeRedLight = False
                            car.seeTrafficLight = True
                            car.nextLinkId = self.downstreamM_LinkId              
            
            # step forward 1 second
            yield self.env.timeout(1)
            self.phaseUsedTime += 1
            if self.phaseUsedTime == self.phaseTotalTime:
                # loop through all four phases: 0 -> 1 -> 2 -> 3 -> 0 ...
                oldPhase = self.currentPhase
                if self.numPhases == 2:
                    if self.currentPhase == 1:
                        self.currentPhase = 0
                    else:
                        self.currentPhase = 1     
                # reset the phaseTime and phaseTotalTime
                self.phaseUsedTime = 0
                self.phaseTotalTime = self.greenTimes[self.currentPhase]
                print(self, f"change phase {oldPhase} to new phase {self.currentPhase} at {self.env.now}")       

#     def lightPositions(self):
#         '''
#         Return a dictionary that contains the base positions of traffic light 
#         Later, the green light is applied to update them
#         '''
#         return {'N':self.north, 'S':self.south, 'W':self.west, 'E':self.east,}
    
#     def getTrafficLightConditions(self,):
#         """
#         Return back a dictionary that contains the position of each green light
#         """
#         lights = None
#         if self.currentPhase == 0:
#         # NS-turnleft
#             lights = {
#                 'N': ((self.x-Node.SIZE//3, self.y-Node.SIZE//2), (Node.SIZE//6, Node.SIZE//6)),
#                 'S': ((self.x+Node.SIZE//6, self.y+Node.SIZE//3), (Node.SIZE//6, Node.SIZE//6)),
#             }
#         elif self.currentPhase == 1: 
#         # NS-straight
#             lights = {
#                 'N': ((self.x-Node.SIZE//6, self.y-Node.SIZE//2), (Node.SIZE//6, Node.SIZE//6)),
#                 'S': ((self.x, self.y+Node.SIZE//3), (Node.SIZE//6, Node.SIZE//6)),
#             }
#         elif self.currentPhase == 2:
#         # WE-straight
#             lights = {
#                 'W': ((self.x-Node.SIZE//2, self.y+Node.SIZE//6), (Node.SIZE//6, Node.SIZE//6)),
#                 'E': ((self.x+Node.SIZE//2, self.y-Node.SIZE//6), (Node.SIZE//6, Node.SIZE//6)),
#             }
#         elif self.currentPhase == 3:
#             lights = {
#                 'W': ((self.x-Node.SIZE//2, self.y), (Node.SIZE//6, Node.SIZE//6)),
#                 'E': ((self.x+Node.SIZE//2, self.y), (Node.SIZE//6, Node.SIZE//6)),
#             }
#         return lights
    def setPhase(self, tf_Phases):
        self.numPhases = tf_Phases[0]
        self.greenTimes = tf_Phases[1]
        assert len(self.greenTimes) == self.numPhases
    def setDirections(self, tf_Directions):
        self.direction['UP_Mainroad'] = tf_Directions[0]
        self.direction['DOWN_Mainroad'] = tf_Directions[1]
        if tf_Directions[2] != None:
            self.direction['DOWN_Branch'] = tf_Directions[2] 
        if tf_Directions[3] != None:
            self.direction['UP_Branch'] = tf_Directions[3] 

    def __repr__(self):
        return f"TrafficLight{self.nodeId}"
    def __str__(self):
        return f"TrafficLight{self.nodeId}"
    def __hash__(self):
        return super().__hash__()

class Link(object):
    
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

    def getFrontCarLane(self, LaneId,):
        isFront = False
        veh = None
        for idx in [-1, -2, -3]:
            if isinstance(self.trafficMatrix[LaneId][idx], Car):
                isFront = True
                veh = self.trafficMatrix[LaneId][idx]
                # veh.seeTrafficLight = True
                break
                
        return isFront, veh

    def __repr__(self):
        return f"Link{self.linkId}"
    def __str__(self):
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.linkId))       
  