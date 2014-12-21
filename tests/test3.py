import struct
#Packet Info
packets = {
0x00:{"name":"string"},
0x01:{"id":"int"},
0x02:{"id":"int", "message":"string"},
0x03:{"name":"string", "message":"string"}
}
# Maps types to what you need to call struct.unpack()
structKeys = {"short":"H", "int":"I"}

typeLength = {"short":2, "int": 8}

def unpack(ctype,data):
        return struct.unpack(self.structKeys[ctype],data)[0]

def unpackPacket(header,sock):
    packet = {}
    # A dictionary holding the name:type for all fields of the packet specified by the header
    packetFormat = packets[header]
    for(key, ctype in packetFormat.values()):
        if ctype in structKeys.keys():
            packet[key] = unpack(ctype, sock.chat_recv(typeLength[ctype]))
        else:
            if ctype == "string":
                bit_length = unpack("short", sock.chat_recv(typeLength["short"]))
                packet[key] = sock.chat_recv(typeLength["short"])
    return packet
