import struct, queue, select, sys
from ChatSocket import ChatSocket
class ChatClient(ChatSocket):
    id = -1
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.message_queue = queue.Queue()

    def connect(self, host, port):
        self.sock.connect((host,port))
        self.sock.setblocking(0)
        self.sock = ChatSocket(self.sock)

    def disconnect(self):
        with self.message_queue.mutex:
            self.message_queue.clear()
        self.sock.close()

    def login(self,name):
        self.handlePacket(self.headers["Login"], name=name)

    def handleInput(self, read):
        print(read)

    def handlePacket(self, length, **packet):
        if packet == {}: # Server -> Client case
            header, packet = self.unpackPacket(header, self.sock)
            if header == self.headers["LoginConfirm"]:
                self.id = packet["id"]
            elif header == self.headers["ServerMessage"]:
                # It's important to stress the difference bewteen the two .put() methods
                # self.sock.put() which must be passed a packed packet afterwhich it's sent down the wire
                # self.put() sends the output to the stream_out in listen
                self.put(packet["name"] + ": " + packet["message"])
        else: # Client -> Server case
            self.sock.put(self.packPacket(header, **packet))

    def listen(self, stream_in=sys.stdin, stream_out = sys.stdout):
        self.login(self.name)
        while True:
            readers = [self.sock, stream_in]
            writers = [self.sock, stream_out]
            readable, writable, exceptional = select.select(readers, writers, writers)

            for reader in readable:
                if reader is self.sock:
                    header = reader.chat_recv(self.typeLength["short"])
                    if header:
                        self.handlePacket(struct.unpack(self.structKeys["short"], header))
                    else:
                        self.put("Connection lost")
                        self.disconnect()
                elif reader is stream_in:
                    read = stream_in.readline()
                    handleInput(read)

            for writer in writers:
                if writer is self.sock:
                    try:
                        next_msg = writer.get()
                    except Queue.Empty:
                        pass
                    else:
                        writer.chat_send(next_msg)
                else:
                    try:
                        next_msg = self.get()
                    except Queue.Empty:
                        pass
                    else:
                        stream_out.write(next_msg)
