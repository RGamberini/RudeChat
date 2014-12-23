import socket, queue, struct
class ChatSocket(object):
    # TODO
    # Read packet length first
    # Redo chat_send and chat_recv I may not need the wrapper at all

    # Version Info
    VERSION = "0.1"

    # Packet Info
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
        self.close = self.sock.close

    def send_waiting(self):
        sent = self.sock.send(self.message_buffer)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        message_buffer = message_buffer[sent:]
        if message_buffer == b"":
            self.writing = False

    # Without specifying MSGLEN chat_recv pulls as much as it can (2048 bits)
    def chat_recv(self, MSGLEN=2048):
        return self.sock.recv(MSGLEN)

    # Pull a type off the stream
    def unpack(self,ctype,data,position=0):
        if ctype in self.structKeys.keys():
            return struct.unpack(self.structKeys[ctype], data[position:position + self.typeLength[ctype]])[0], self.typeLength[ctype]
        elif ctype == "string":
            bit_length = self.unpack("short", data, position)[0]
            return data[position:position +bit_length].decode('utf-8'), bit_length + self.typeLength["short"]

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
    # packed_packet means I expect a packet right off the stream
    def unpackPacket(self, length):
        packed_packet = self.chat_recv(length)
        header, position = self.unpack("short", packed_packet)
        packet = self.packets[header]
        for key, ctype in packet.items():
            packet[key], step = self.unpack(ctype, packed_packet, position)
            position += step
        return header, packet

    # A packets is a dictionary key:value
    def packPacket(self,header,**packet):
        packed_packet = self.pack("short", header)
        for key, data in packet.items():
            #print("Building packet " + str(self.headers[header]) + " currently: " + packed_packet)
            packed_packet += self.pack(self.packets[header][key],data)
        packed_packet = self.pack("short", len(packed_packet)) + packed_packet # Preface packets with length
        return packed_packet

    def put(self, data):
        self.writing = True
        self.message_buffer += data

    def get(self):
        self.writing = False
        result = self.message_buffer
        return self.message_buffer
