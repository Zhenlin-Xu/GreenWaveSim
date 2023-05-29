class Veh(object):
    def __init__(self,
                 env,
                 net,
                 vehID,
                 linkID,
                 laneID,
                 ) -> None:
        self.env = env
        self.net = net
        self.vehID = vehID
        self.position = (linkID, laneID, 0)
        self.isExit = False
        self.isLink = True # whether the car arrives at the intersection
        self.action = env.process(self.run())

    def run(self,):
        print(f"Generate {self.__repr__()} in T:{self.env.now:3.0f} at link {self.position[0]}")
        self.isExit, self.isLink = self.checkState()
        # perform simulation after generation
        while not self.isExit:
            # first check its state, whether in the link or arrives at the intersection?
            if self.isLink:
                # still in the link, perform cellular automata logic
                self.cellularAutomata()
                yield self.env.timeout(1)
            else:
                # arrives at intersection, according to the traffic light
                pass
            self.isExit, self.isLink = self.checkState()
        # remove the vehicle if exiting
        self.net.vehicles.pop(self.vehID)
        self.net.numVehNow -= 1        

    def cellularAutomata(self,):
        pass

    def checkState(self,) -> tuple(bool, bool):
        '''
        Veh checks its state (isExit, isLink).
        '''
        linkID = self.position[0]
        link = self.net.links[linkID]
        DestinNodeID = link.destin
        DestinNode = self.net.nodes[DestinNodeID]
        isExit = True if DestinNode.isExit == True and self.position[2] == link.numGrids else False
        isLink = True if self.position < link.numGrids else False
        return (isExit, isLink)

    def __repr__(self) -> str:
        return f"Veh{self.vehID}"
    def __str__(self) -> str:
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.vehID))