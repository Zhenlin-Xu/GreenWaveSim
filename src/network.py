from collections import OrderedDict

class Network(object):
    def __init__(self, env, numVehInit):
        self.env = env
        self.links = OrderedDict()
        self.nodes = OrderedDict()
        self.vehicles = {}
        self.numVehNow = numVehInit
        self.numVehGen = numVehInit

    def addNode(self, nodeID, adjacentNodes, isControlled, isExit):
        self.nodes[nodeID] = Node(nodeID=nodeID,
                                  isControlled=isControlled,
                                  isExit=isExit,
                                  adjacentNodes=adjacentNodes)

    def addLink(self, linkID, numLanes=2, lenLanes=35):
        self.links[linkID] = Link(linkID=linkID,
                                  numLanes=numLanes, 
                                  lenLanes=lenLanes)

class Node(object):
    def __init__(self,
                 nodeID:int,
                 isControlled:bool,
                 isExit:bool,
                 adjacentNodes: list):
        self.nodeID = nodeID
        self.isControlled = isControlled
        self.isExit = isExit
        self.adjacentNodes = adjacentNodes

    def __repr__(self) -> str:
        return f"Node-{self.nodeID}"
    def __str__(self) -> str:
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.nodeID))
    
class Link(object):
    def __init__(self, 
                 linkID:int,
                 numLanes = 2,
                 lenLanes = 35,):
        self.linkID = linkID
        self.origin = int(self.linkID.split('O')[0].split('I')[1])
        self.destin = int(self.linkID.split('O')[1])
        assert type(self.origin) == int
        assert type(self.destin) == int
        self.numLanes = numLanes
        self.sizeGrid = 7
        self.numGrids = lenLanes // self.sizeGrid
        self.link = [[ 0 for _ in range(self.numGrids)] for _ in range(self.numLanes)]

    def __repr__(self) -> str:
        return str(self.link)
    def __str__(self) -> str:
        return self.__repr__()
    def __hash__(self):
        return hash(str(self.linkID))
    
