import simpy
from sim import Simulation
from athens import SCREEN_HEIGHT, SCREEN_WIDTH

if __name__ == "__main__":
    # test
    env = simpy.Environment()
    sim = Simulation(env=env, numInitVehs=10, screen_height=SCREEN_HEIGHT, screen_width=SCREEN_WIDTH-100)
    sim.initpNeumaNetwork()
    sim.simulate(until=1800)