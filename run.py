import simpy
from pprint import pprint
from src.simulation import Simulation

if __name__ == "__main__":
    env = simpy.Environment() 
    sim = Simulation(env=env)
    sim.initNetwork()
    # pprint(sim.net.nodes)
    pprint(sim.net.links)