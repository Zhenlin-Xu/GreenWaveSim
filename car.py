import random
import numpy as np
from athens import LINK_OUT
from utils import logging

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
        self.nextLane = None
        self.randomization = randomization
        self.laneChangeThres = laneChangeThres
        self.type = type

        # binary state indicators
        self.seeTrafficLight = False
        self.seeRedLight = True
        self.leaveNetwork = False
        self.checkStatus()
        self.nextLinkId = None
        # setup the process for event
        self.action = self.env.process(self.run())
        
    def run(self):
        while (not self.leaveNetwork):
            # print(self.currentLinkId, self.currentLane, self.currentGrid)
            if not self.seeTrafficLight:
                ##############################################
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
                self.net.distances[self.type] += self.currentSpeed    
                #################
                # 5. lane change:
                #################
                # if self.net.linkCollection[self.currentLinkId].numLanes > 1:
                #     if random.random() > self.laneChangeThres and self.currentSpeed > 0:
                #         if self.currentLane == 0 or (random.random() < 0.5 and self.currentLane == 1):
                #             # case1: in the leftmost lane, check its right lane
                #             # case2: in the middle lane, randomly change to its right lane
                #             if self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane+1, self.currentGrid] == 0:
                #                 self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane+1][self.currentGrid] = \
                #                     self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid]
                #                 self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = 0
                #                 # update the binary matrix
                #                 self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane+1, self.currentGrid] = self.type
                #                 self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid] = 0  
                #                 self.currentLane += 1
                #                 # self.currentSpeed = 0
                #                 self.net.distances[self.type] += 1    

                #             elif self.currentLane == 2 or (random.random() >= 0.5 and self.currentLane == 1):
                #             # case3: in the rightmost lane, check its left lane
                #             # case4: in the middle lane, randomly change to its left lane
                #                 self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane-1][self.currentGrid] = \
                #                     self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid]
                #                 self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = 0
                #                 # update the binary matrix
                #                 self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane-1, self.currentGrid] = self.type
                #                 self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane, self.currentGrid] = 0  
                #                 self.currentLane -= 1  
                #                 # self.currentSpeed = 0      
                #                 self.net.distances[self.type] += 1    
                    
                # # warning: stop in the link
                # if self.currentSpeed == 0:
                #     logging(msg=f"{self} stops in link {self.currentLinkId, self.currentGrid} at {self.env.now}",
                #             color='red')
                # update time    
                yield self.env.timeout(1)
                # check status
                self.checkStatus()
            else:
                if self.seeRedLight:
                    self.currentSpeed = 0
                    self.net.distances[self.type] += 1
                    yield self.env.timeout(1)
                else: # see green light:
                    passTime = 1
                    self.net.distances[self.type] += 2
                    yield self.env.timeout(passTime)
                    if self.nextLane == None:
                        if self.net.linkCollection[self.nextLinkId].trafficMatrix[self.currentLane][0] == 0:
                            self.net.linkCollection[self.nextLinkId].trafficMatrix[self.currentLane][0] = self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid]
                            self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = 0
                            self.net.linkCollection[self.nextLinkId].binaryMatrix[self.currentLane][0] = self.type
                            self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane][self.currentGrid] = 0
                            self.currentLinkId = self.nextLinkId
                            self.currentGrid = 0
                            self.seeTrafficLight = False
                            self.seeRedLight = False 
                            self.nextLane = None
                    else:
                        if self.net.linkCollection[self.nextLinkId].trafficMatrix[self.nextLane][0] == 0:
                            self.net.linkCollection[self.nextLinkId].trafficMatrix[self.nextLane][0] = self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid]
                            self.net.linkCollection[self.currentLinkId].trafficMatrix[self.currentLane][self.currentGrid] = 0
                            self.net.linkCollection[self.nextLinkId].binaryMatrix[self.nextLane][0] = self.type
                            self.net.linkCollection[self.currentLinkId].binaryMatrix[self.currentLane][self.currentGrid] = 0
                            self.currentLinkId = self.nextLinkId
                            self.currentLane = self.nextLane
                            self.currentGrid = 0
                            self.seeTrafficLight = False
                            self.seeRedLight = False 
                            self.nextLane = None
                # check status 
                self.checkStatus()

        logging(msg=f"{self.__str__()} leaves Network",
                color='green')
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
        self.leaveNetwork = self.__isMyselfFrontCar() and self.__isStepOutsideLink() and currentLinkType == LINK_OUT
        self.seeTrafficLight = True if self.currentGrid + 2 >= self.net.linkCollection[self.currentLinkId].numGrids else False
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
