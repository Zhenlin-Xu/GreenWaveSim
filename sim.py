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
from net import Network
from athens import node_CenterPositions, link_Infos, tf_Directions, tf_Phases
from athens import LINK_GRIDSIZE, NODE_HEIGHT, NODE_WIDTH, NODE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, LINK_IN, LINK_OUT
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

    def initpNeumaNetwork(self, numInitVehs=5):
        ####################
        # Init all the Nodes
        ####################
        for nodeId, node_Position in node_CenterPositions.items():
            # Rect nodes && TrafficLight Node
            if nodeId in [1,2,3,4,5,6,7,8,9]:   
                self.net.addTrafficLightNode(
                    nodeId=nodeId,
                    position=node_Position,
                    isExit=False,
                    isControlled=True,
                    shape='RECT'
                )
            # Rect nodes && Normal Nodes
            elif nodeId in [21,22,41,42]:
                self.net.addNode(
                    nodeId=nodeId,
                    position=node_Position,
                    isExit=False,
                    isControlled=False,
                    shape='RECT'
                )
            # Square nodes && Normal Nodes
            else:  
               self.net.addNode(
                    nodeId=nodeId,
                    position=node_Position,
                    isExit=False,
                    isControlled=False,
                    shape='SQUARE'
                )
        assert len(node_CenterPositions) == len(self.net.nodeCollection) # 20
        logging(msg=f"LOGGING: initialize {len(self.net.nodeCollection):2.0f} nodes into network", 
                color='green')
        logging(msg=f"LOGGING: initialize {len(self.net.trafficLightCollection):2.0f} traffic lights into network", 
                color='green')
        
        ####################
        # Init all the Links
        ####################
        for linkId, linkInfo in link_Infos.items():
            self.net.addLink(
                linkId=linkId,
                lengthLane=linkInfo[0], numLanes=linkInfo[1],
                originNodeId=linkInfo[2], destinNodeId=linkInfo[3],
                type=linkInfo[4],
            )
        assert len(self.net.linkCollection) == len(link_Infos)
        assert len(self.net.inflowLinkCollection) == 5
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

        ###############
        # Init vehicles 
        ###############
        self.net.initCars(self.numInitVehs)
        assert len(self.net.carCollection) == self.numInitVehs
        assert self.net.numVehInSystem == self.numInitVehs
        logging(msg=f"LOGGING: initialize {self.numInitVehs:2.0f} cars into network",
                color='green')

if __name__ == "__main__":
    # test
    env = simpy.Environment()
    sim = Simulation(env=env, numInitVehs=10, screen_height=SCREEN_HEIGHT, screen_width=SCREEN_WIDTH-100)
    sim.initpNeumaNetwork()
    sim.simulate(until=100)