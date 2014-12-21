import socket, queue, struct
class ChatSocket(object):
    # TODO
    # Read packet length first
    # Redo chat_send and chat_recv I may not need the wrapper at all
    #Packet Info
    packets =(
    {"name":"string"},
    {"id":"int"},
    {"id":"int", "message":"string"},
    {"name":"string", "message":"string"}
    )

    # More packet info
    headers = {
    "Login":0x00,
    "LoginConfirm":0x01,
    "ClientMessage":0x02,
    "ServerMessage":0x03,
    # "Optimization" *wink* *wink* *nudge* *nudge*
    0x00:"Login",
    0x01:"LoginConfirm",
    0x02:"ClientMessage",
    0x03:"ServerMessage"
    }
    # Maps types to what you need to call struct.unpack()
    structKeys = {"short":">H", "int":">I"}

    typeLength = {"short":2, "int": 8}

    def __init__(self,sock=None):
        if (sock is None):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.message_buffer = b""
        self.writing = False
        # Allows my socket to be called by select()
        self.fileno = self.sock.fileno

    def chat_send(self, msg, MSGLEN):
        # Probably not needed anymore, if you pass a string
        # of the wrong size this will pad it to the right size
        # but I don't really pass this function strings
        if (isinstance(msg, str) and len(msg) < MSGLEN):
            msg = bytes(msg.ljust(length), "UTF-8")
        totalsent = 0
        # Loop until everything is sent
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def chat_recv(self, MSGLEN):
        msg = []
        bytes_recd = 0
        # Loop until everything is sent
        while bytes_recd < MSGLEN:
            pull = self.sock.recv(MSGLEN - bytes_recd)
            if pull == b'':
                raise RuntimeError("socket connection broken")
            msg.append(pull)
            bytes_recd += len(pull)
        return b''.join(msg)

    # Pull a type off the stream
    def unpack(self,ctype,sock):
        if ctype in self.structKeys.keys():
            return struct.unpack(self.structKeys[ctype],sock.chat_recv(self.typeLength[ctype]))[0]
        elif ctype == "string":
            bit_length = self.unpack("short", sock)
            return sock.chat_recv(bit_length).decode('utf-8')

    # Encodes the data you pass it into bytes
    # Then returns it to you in a concatenated bytestring
    def pack(self,ctype,data):
        if ctype in self.structKeys.keys():
            result = struct.pack(self.structKeys[ctype],data)
            #print("Passed: " + str(data) + ", Result: " + str(result) + ", is number: " + str(isinstance(result[0], int)))
            return result
        elif ctype == "string":
            byte_string = data.encode('utf-8')
            return self.pack("short", len(byte_string)) + byte_string

    # Goes through the packet definition and pulls everything
    def unpackPacket(self,header,sock):
        packet = self.packets[header]
        for key, ctype in packet.items():
            packet[key] = self.unpack(ctype, sock)
        return packet

    # A packets is a dictionary key:value
    def packPacket(self,header,**packet):
        packed_packet = self.pack("short", header)
        for key, data in packet.items():
            #print("Building packet " + str(self.headers[header]) + " currently: " + packed_packet)
            packed_packet += self.pack(self.packets[header][key],data)
        return packed_packet

    def put(self, data):
        self.writing = True
        self.message_buffer.put_nowait(data)

    def get(self):
        self.writing = False
        result = self.message_buffer
        return self.message_buffer
