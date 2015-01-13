import struct, queue, select, sys
from ChatSocket import ChatSocket
from collections import deque
class ChatClient(ChatSocket):
    id = -1
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.message_queue = deque()

    def connect(self, host, port):
        print("Establishing connection to", host, "on port", str(port))
        self.sock.connect((host,port))
        print("Connected")
        self.sock.setblocking(0)
        self.sock = ChatSocket(self.sock)
        self.sock.setProperty(host=host,port=port)

    def put(self, data):
        self.writing = True
        self.message_queue.append(data)

    def putString(self, *argv):
        self.put(" ".join(map(str,argv)))

    def disconnect(self):
        print("Server Connection to", self.sock.getProperty("host"), "Lost")
        self.sock.close()

    def login(self):
        login_packet = self.sock.packPacket(self.headers["Login"], name=self.name)
        print("Logging in with name:", self.name)
        self.sock.put(login_packet)

    def sendMessage(self, payload):
        message_packet = self.sock.packPacket(self.headers["ClientMessage"], id=self.getProperty("id"), message=payload)
        # print(self.name + ":",payload)
        self.sock.put(message_packet)

    def handleInput(self, read):
        self.sendMessage("Hello World")

    # It's important to stress the difference bewteen the two .put() methods
    # self.sock.put() which must be passed a packed packet afterwhich it's sent down the wire
    # self.put() sends the output to the stream_out in listen

    def handlePacket(self, server, length):
        header, packet = server.unpackPacket(length)
        if header == self.headers["LoginConfirm"]:
            self.setProperty(id=packet["id"])
            print("Logged in with ID: ", packet["id"])
        elif header == self.headers["ServerMessage"]:
            print(packet["name"] + ":", packet["message"])

    def listen(self, stream_in=sys.stdin, stream_out = sys.stdout):
        while True:
            readers = [self.sock, stream_in]
            writers = [self.sock]
            readable, writable, exceptional = select.select(readers, writers, writers)

            for reader in readable:
                if reader is self.sock:
                    length = reader.chat_recv(self.typeLength["short"])
                    if length:
                        length = reader.unpack("short", length)[0]
                        self.handlePacket(reader,length)
                    else:
                        print("Connection lost")
                        self.disconnect()
                elif reader is stream_in:
                    read = stream_in.readline()
                    self.handleInput(read)

            for writer in writers:
                if writer is self.sock and writer.writing:
                    writer.send_waiting()
