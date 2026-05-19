from agentspace import Agent, space
import cv2
import time
from speak import speak

class Speaker(Agent):
    
    def __init__(self,name):
        self.name = name
        super().__init__()
        
    def init(self):
        space.attach_trigger(self.name,self)
  
    def senseSelectAct(self):
        text = space[self.name]
        if text is not None and len(text) > 0:
            speak(text)