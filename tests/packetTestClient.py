import ChatSocket, struct
dataClasses = {"short":2}
class packetClient(ChatSocket.ChatSocket):
    def __init__(self,sock=None):
        super().__init__()

    def connect(self, host, port):
        self.sock.connect((host,port))

    def login(self, name):
        self.chat_send(struct.pack('>H', 0x00), 2)
        name = name.encode('utf-8')
        self.chat_send(struct.pack('>H', len(name)), 2)
        self.chat_send(name, len(name))

    def sendMessage(self, message):
        print("TODO")

client = packetClient()
client.connect("localhost", 3232)
client.login("Rudy")
input()
client.sock.close()
