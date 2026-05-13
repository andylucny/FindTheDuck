from agentspace import Agent, space
import cv2

class Viewer(Agent):
    
    def __init__(self,name):
        self.name = name
        super().__init__()
        
    def init(self):
        space.attach_trigger(self.name,self)
  
    def senseSelectAct(self):
        cv2.imshow(self.name,space[self.name])
        cv2.waitKey(1)