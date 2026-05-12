from agentspace import Agent, space
from dino import dino

class Perception(Agent): 
    
    def __init__(self,image_name,feature_name):
        self.image_name = image_name
        self.feature_name = feature_name
        super().__init__()
        
    def init(self):
        space.attach_trigger(self.image_name,self)
  
    def senseSelectAct(self):
        image = space[self.image_name]
        if image is None:
            return
        features = dino(image)
        space[self.feature_name] = features
