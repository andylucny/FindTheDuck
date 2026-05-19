from agentspace import Agent, space
import cv2
from dino import load_features
import time

class Namer(Agent):
    
    def __init__(self,name):
        self.name = name
        self.threshold = 1900.0
        super().__init__()
        
    def init(self):
        space.attach_trigger('duck', self)
        space.attach_trigger(self.name, self)
        self.duck = None

    def senseSelectAct(self):
        name = self.triggered()
        if name == 'duck':
            self.duck = space['duck']
            print("There is a duck vector on our blackboard", flush=True)
            return
        if self.duck is None:
            return
        features = space[self.name]
        if features is not None:
            similarity = features @ self.duck
            if similarity > self.threshold:
                space['tospeak'] = "Ou, here is the duck!"
