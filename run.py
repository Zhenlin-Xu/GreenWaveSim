import simpy
from pprint import pprint
from src.simulation import Simulation

if __name__ == "__main__":
    env = simpy.Environment() 
    sim = Simulation(env=env, numVehInit=3)
    sim.initNetwork()
    sim.initVehicles()
    # pprint(sim.net.nodes)
    # pprint(sim.net.links)

    env.run(until=15)