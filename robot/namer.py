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
            features = space[self.name]

            if duck is None or features is None:
                space['duck_sim'] = None          
                print("namer waiting: duck None?", duck is None,
                    "feat None?", features is None, flush=True)
                return

            if duck is not self.duck:
                self.duck = duck

            sim = float(features @ self.duck)
            space['duck_sim'] = sim
            print("sim", round(sim, 3), flush=True)