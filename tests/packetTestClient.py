import ChatSocket, struct
dataClasses = {"short":2}
class packetClient(ChatSocket.ChatSocket):
    def __init__(self,sock=None):
        super().__init__()

    def connect(self, host, port):
        self.sock.connect((host,port))

    def login(self, name):
        login_packet = self.packPacket(self.headers["Login"], name=name)
        self.put(login_packet)
        self.send_waiting()

    def sendMessage(self, message):
        self.put(self.packPacket(self.headers["ClientMessage"], id=0, message="FUCK"))

client = packetClient()
client.connect("localhost", 3232)
client.login("Rudy")
input()
client.sock.close()
