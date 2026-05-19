import socket
import re
from agentspace import Agent, space, Trigger
from demarshaller import demarshal

class MirrorClientAgent(Agent):

    def __init__(self,ip,port,names):
        self.ip = ip
        self.port = port
        self.names = names
        self.buffer = ''
        super().__init__()
        
    def getline(self):
        while self.buffer.find('\n')==-1:
            self.buffer += self.sock.recv(1024).decode()
        result = re.sub('[\r\n].*','',self.buffer)
        self.buffer = self.buffer[self.buffer.find('\n')+1:]
        return result

    def putline(self,line):
        self.sock.send((line+'\r\n').encode())
        
    def init(self):
        print('receiver starting')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.ip,self.port))
        except ConnectionRefusedError:
            print('the server is not running')
            self.stop()
        for name in self.names:
            space.attach_trigger(name,self,Trigger.NAMES)
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
