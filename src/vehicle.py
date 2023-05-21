class Veh(object):
    def __init__(self,
                 env,
                 net,
                 linkID,
                 laneID,
                 ) -> None:
        self.env = env
        self.position = (linkID, laneID, 0)
        # self.action = env.process(self.run())

    def run(self,):
        pass