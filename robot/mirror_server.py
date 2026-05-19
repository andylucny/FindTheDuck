from agentspace import Agent, space, Trigger
from marshaller import marshal
import cv2
import socket
import sys
import re
import numpy as np
from demarshaller import demarshal

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
            space.attach_trigger(name, self, Trigger.NAMES)
        print('starting mirroring')
        import threading
        self.reader = threading.Thread(target=self.read_loop, daemon=True)
        self.reader.start()

    def read_loop(self):
        while not self.stopped:
            try:
                line = self.getline()
            except Exception as e:
                print('reception closed:', e, flush=True)
                self.stop()
                return
            try:
                name, marshalled = line.split(None, 1)
                #print(f"robot server: received name={name!r}, len={len(marshalled)}", flush=True)
                space[name] = demarshal(name, marshalled)
                #print(f"robot server: wrote space[{name!r}], is_none={space[name] is None}", flush=True)
            except Exception as e:
                print(f"robot server: parse/demarshal failed: {e}", flush=True)

    def senseSelectAct(self):
        name = self.triggered()
        try:
            self.putline(name+" "+marshal(name,space[name]))
        except:
            print('transmission closed')
            self.stop()
    
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
    