from agentspace import Agent, space
from marshaller import marshal
import cv2
import socket
import sys
import re
import numpy as np

class MirrorServiceAgent(Agent):

    def __init__(self,socket,name):
        self.socket = socket
        self.name = name
        self.buffer = ''
        super().__init__()
        
    def getline(self):
        while self.buffer.find('\n')==-1:
            self.buffer += self.socket.recv(1024).decode()
        result = re.sub('[\r\n].*','',self.buffer)
        self.buffer = self.buffer[self.buffer.find('\n')+1:]
        return result
     
    def putline(self,line):
        self.socket.send((line+'\r\n').encode())
        
    def init(self):
        try:
            print('starting mirroring on the port',self.name)
            while not self.stopped:
                name = self.getline()
                if len(name) > 0:
                    self.putline(marshal(name,space[name]))
        except Exception as e:
            print(e)
            self.stop()

    def senseSelectAct(self):
        pass
    
class MirrorServerAgent(Agent):

    def __init__(self,port,name):
        self.port = port
        self.name = name
        super().__init__()
        
    def init(self):
        print('mirroring server starting on port',self.port)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0',self.port))
        except:
            self.stop()
        while not self.stopped:
            try:
                sock.listen(1)
                client, address = sock.accept()
                MirrorServiceAgent(client,self.name)
            except:
                pass
        try:
            sock.close()
        except:
            pass
  
    def senseSelectAct(self):
        pass
    