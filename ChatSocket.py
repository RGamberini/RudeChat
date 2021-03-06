import socket, queue, struct
from ChatExceptions import PacketIncompleteError
class ChatSocket(object):
    # TODO
    # Packet definitions must go into either a tuple of tuples or an enum or
    # ordereddict however storing the info in a normal dict causes
    # Version Info
    VERSION = "0.2"

    # Packet Info
    packets =(
    ("Login", ("name","string")),
    ("LoginConfirm", ("id","int")),
    ("ClientMessage", ("id","int"), ("message","string")),
    ("ServerMessage", ("name","string"), ("message","string"))
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

    typeLength = {"short":2, "int": 4}

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
        self.properties = {} # For storing useful information

    def byteToHex(self, byteStr):
	    return ''.join( [ "%02X " % x for x in byteStr ] ).strip()

    def setProperty(self, **kwargs):
        for k,v in kwargs.items():
            self.properties[k] = v

    def getProperty(self, key):
        try:
            return self.properties[key]
        except KeyError:
            return None

    def send_waiting(self):
        # print(str(self.message_buffer))
        sent = self.sock.send(self.message_buffer)
        if sent == 0:
            raise RuntimeError("socket connection broken")
        self.message_buffer = self.message_buffer[sent:]
        if self.message_buffer == b"":
            self.writing = False

    # Without specifying MSGLEN chat_recv pulls as much as it can (2048 bits)
    def chat_recv(self, MSGLEN=2048):
        return self.sock.recv(MSGLEN)

    # Pull a type off the stream
    def unpack(self,ctype,data,position=0):
        if ctype in self.structKeys.keys():
            selectdata = data[position:position + self.typeLength[ctype]] # DEBUG
            x = struct.unpack_from(self.structKeys[ctype], data, position)[0], self.typeLength[ctype] # DEBUG
            print("Attempt to unpack",ctype,"from",data[position:],"resulted in",x) # DEBUG
            return x
        elif ctype == "string":
            bit_length, step = self.unpack("short", data, position)
            position += step
            # return data[position:position + bit_length].decode('utf-8'), bit_length
            x = data[position:position + bit_length].decode('utf-8') # DEBUG
            print("Attempt to unpack",ctype,"from",data[position:],"resulted in",x) # DEBUG
            return x, bit_length # DEBUG

    # Encodes the data you pass it into bytes
    # Then returns it to you in a concatenated bytestring
    def pack(self,ctype,data):
        if ctype in self.structKeys.keys():
            result = struct.pack(self.structKeys[ctype],data)
            return result
        elif ctype == "string":
            byte_string = data.encode('utf-8')
            return self.pack("short", len(byte_string)) + byte_string

    # Goes through the packet definition and pulls everything
    # packed_packet means I expect a packet right off the stream
    def unpackPacket(self, length, packed_packet=None):
        if not packed_packet:
            packed_packet = self.chat_recv(length)
        if len(packed_packet) < length:
            raise PacketIncompleteError(packed_packet)
        print("Received", packed_packet)
        header, position = self.unpack("short", packed_packet)
        packet = self.packets[header].copy()
        #before, word = 0, "header" # DEBUG
        for i, ctype in packet.iter():
            #print("Before:", self.byteToHex(packed_packet[before:position]), "Read:", word, "left:", self.byteToHex(packed_packet[position:])) # DEBUG
            packet[key], step = self.unpack(ctype, packed_packet, position)
            before = position
            position += step
            #word = key # DEBUG
        print("Unpack", str(packet)) # DEBUG
        return header, packet

    # A packets is a dictionary key:value
    def packPacket(self,header,*packet):
        print("Pack", str(packet)) # DEBUG
        packed_packet = self.pack("short", header)
        for i,data in packet.iter():
            packed_packet += self.pack(self.packets[header][i],data)
            # print("Packed", self.packets[header][key],"full byte string: ", self.byteToHex(packed_packet))
        packed_packet = self.pack("short", len(packed_packet)) + packed_packet # Preface packets with length
        print("Sending", packed_packet)
        return packed_packet

    def put(self, data):
        self.writing = True
        self.message_buffer += data

    def get(self):
        self.writing = False
        result = self.message_buffer
        return self.message_buffer
