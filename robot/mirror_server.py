from agentspace import Agent, space, Trigger
from marshaller import marshal
import cv2
import socket
import sys
import re
import numpy as np

class MirrorServiceAgent(Agent):

    def __init__(self,socket,names):
        self.socket = socket
        self.names = names
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
        for name in self.names:
            space.attach_trigger(name,self,Trigger.NAMES)
        print('starting mirroring')
        self.loopit = True
        
    def loop(self):
        try:
            line = self.getline()
        except Exception as e:
            print(e)
            self.stop()
        try:
            name, marshalled = line.split()
            space[name] = demarshal(name,marshalled)
        except Exception as e:
            print(e)

    def senseSelectAct(self):
        name = self.triggered()
        self.putline(name+" "+marshal(name,space[name]))
    
class MirrorServerAgent(Agent):

    def __init__(self,port,names):
        self.port = port
        self.names = names
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
                print('connected')
                MirrorServiceAgent(client,self.names)
            except:
                pass
        try:
            sock.close()
        except:
            pass
  
    def senseSelectAct(self):
        pass
    