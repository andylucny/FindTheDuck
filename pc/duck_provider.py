from agentspace import Agent, space
import cv2
import numpy as np

class DuckProvider(Agent):
    
    def __init__(self, object_feature_location):
        self.object_feature_location = object_feature_location
        self.name = "duck"
        super().__init__()
        
    def init(self):
        space[self.name] = np.load(self.object_feature_location)
        #print(space[self.name])
        self.stop() 