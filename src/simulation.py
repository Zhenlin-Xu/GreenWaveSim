from src.network import Network

class Simulation(object):
    def __init__(self,
                 env,
                 ):
        self.env = env
        self.net = Network(env=env)

    def initNetwork(self,):
        '''create a square network''' 
        # add nodes
        nodeID = [i+1 for i in range(4)]
        adjacentNodes = [(2,3), (1,4), (1,4), (2,3)]
        for node_idx in range(4):
            self.net.addNode(nodeID=nodeID[node_idx],
                             adjacentNodes=adjacentNodes[node_idx],
                             isControlled=True,
                             isExit=False,)
        assert len(self.net.nodes) == 4

        # add links by connecting nodes
        for nodeID, node in self.net.nodes.items():
            for adjacent_nodeID in node.adjacentNodes:
                self.net.addLink(linkID=f'I{nodeID}O{adjacent_nodeID}',
                                 numLanes=2,
                                 lenLanes=35,)
                self.net.addLink(linkID=f'I{adjacent_nodeID}O{nodeID}',
                                 numLanes=2,
                                 lenLanes=35,)
        assert len(self.net.links) == 4*2

        # add exit nodes
        nodeID = [11,12,21,22,31,32,41,42]
        adjacentNodes = [(1,),(2,),(2,),(4,),(4,),(3,),(3,),(1,)]
        for node_idx in range(8):
            self.net.addNode(nodeID=nodeID[node_idx],
                             adjacentNodes=adjacentNodes[node_idx],
                             isControlled=False,
                             isExit=True,)            
        assert len(self.net.nodes) == 4 + 8

        # add links by connecting nodes with exit-nodes
        for nodeID in [11,12,21,22,31,32,41,42]:
            node = self.net.nodes[nodeID]
            for adjacent_nodeID in node.adjacentNodes:
                self.net.addLink(linkID=f'I{nodeID}O{adjacent_nodeID}',
                                 numLanes=2,
                                 lenLanes=35,)
                self.net.addLink(linkID=f'I{adjacent_nodeID}O{nodeID}',
                                 numLanes=2,
                                 lenLanes=35,) 

    def source(self,):
        pass
        

