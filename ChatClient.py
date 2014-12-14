import socket
class ChatClient:

    def __init__(self,sock=None):
        super().__init__()

    def connect(self, host, port):
        self.sock.connect((host,port))

    def sendIM(self, msg):
        self.send(self.name, 8)
        self.send(msg, 256)

    def login(self, name):
        self.name = name
