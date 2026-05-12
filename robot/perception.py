from agentspace import Agent, space
from dino import dino
import os
import numpy as np

class Perception(Agent): 
    
    def __init__(self,image_name,feature_name):
        self.image_name = image_name
        self.feature_name = feature_name
        super().__init__()
        
    def init(self):
        space.attach_trigger(self.image_name,self)
  
    def senseSelectAct(self):
        try:
            image = space[self.image_name]
            if image is None:
                print("[Perception] image is None")
                return
#print(f"[Perception] got image: type={type(image).__name__} "
                #f"shape={getattr(image, 'shape', '?')}")
            features = dino(image)
            if features is None:
                print("[Perception] dino() returned None")
                return
           # print(f"[Perception] features shape={features.shape}")
            space[self.feature_name] = features
        except Exception as e:
            import traceback
            print(f"[Perception] EXCEPTION: {type(e).__name__}: {e}")
            traceback.print_exc()