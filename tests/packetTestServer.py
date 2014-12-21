import struct
from ChatSocket import ChatSocket
class packetServer(ChatSocket):
    def __init__(self, host, port, connections):
        super().__init__()
        self.sock.bind((host, port))
        self.sock.listen(connections)

    def unpack(self, ctype, data):
        if ctype == "short":
            return struct.unpack("H",data)[0]
        elif ctype == "int":
            return struct.unpack("I",data)[0]
        elif ctype == "string":
            return data.decode("utf-8")

    def pack(self, ctype, data):
        if ctype == "short":
            return struct.pack("H",data)[0]
        elif ctype == "int":
            return struct.pack("I",data)[0]
        elif ctype == "string":
            return data.encode("utf-8")

    def startLogin(self, sock):
        header = struct.unpack('H', sock.chat_recv(2))[0]
        print("Header: " + str(header))
        stringLen = int(struct.unpack('H', sock.chat_recv(2))[0])
        print("Length: " + str(stringLen))
        name = sock.chat_recv(stringLen).decode('utf-8')
        print("Name: " + name)


    def listen(self):
        while True:
            print("Searching for connection")
            (clientsocket, address) = self.sock.accept()
            print("Conection made!")
            clientsocket = ChatSocket(clientsocket)
            print("Starting Login...")
            self.startLogin(clientsocket)
