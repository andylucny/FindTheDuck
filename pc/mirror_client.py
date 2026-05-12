import socket
import re
from agentspace import Agent, space
from demarshaller import demarshal

class MirrorClientAgent(Agent):

    def __init__(self,ip,port,name):
        self.ip = ip
        self.port = port
        self.name = name
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
            print('router is not running')
            self.stop()
        self.buffer = ''
        while not self.stopped:
            try:
                self.putline(self.name)
                line = self.getline() 
                space[self.name] = demarshal(self.name,line)
            except Exception as e:
                print(e)
                self.stop()
  
    def senseSelectAct(self):
        pass
        