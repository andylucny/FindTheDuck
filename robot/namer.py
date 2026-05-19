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
        self.duck = load_features('featduck')
        space.attach_trigger(self.name,self)
  
    def senseSelectAct(self):
        features = space[self.name]
        if features is not None:
            similarity = features @ self.duck
            if similarity > self.threshold:
                space['tospeak'] = "Ou, here is the duck!"
                time.sleep(10)
