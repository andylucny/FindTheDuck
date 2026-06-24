from agentspace import Agent, space
import numpy as np

class Namer(Agent):

    def __init__(self, name):
        self.name = name
        super().__init__()

    def init(self):
        space.attach_trigger('duck', self)
        space.attach_trigger(self.name, self)
        self.duck = None

    def senseSelectAct(self):
        duck = space['duck']
        if duck is not self.duck:
            self.duck = duck
        if self.duck is None:
            return
        features = space[self.name]
        if features is None:
            return
        sim = float(features @ self.duck)
        space['duck_sim'] = sim          # publish for the obstacle agent
        print("sim", round(sim, 3), flush=True)