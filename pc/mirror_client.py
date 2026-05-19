import socket
import re
from agentspace import Agent, space, Trigger
from demarshaller import demarshal
from marshaller import marshal

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
        self.sock.settimeout(5)
        try:
            self.sock.connect((self.ip, self.port))
        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            print(f'the server is not running ({e})')
            self.stop()
            return
        self.sock.settimeout(None)
        for name in self.names:
            space.attach_trigger(name, self, Trigger.NAMES)
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
                space[name] = demarshal(name, marshalled)
            except Exception as e:
                print(f"PC client: parse/demarshal failed: {e}", flush=True)
  
    def senseSelectAct(self):
        name = self.triggered()
        try:
            self.putline(name+" "+marshal(name,space[name]))
        except:
            print('transmission closed')
            self.stop()

