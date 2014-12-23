import ChatSocket
x = ChatSocket.ChatSocket()
packet = x.packPacket(x.headers["ServerMessage"], name="Rudly", message="fudgecycle")
x.byteToHex(packet)
packet = x.unpackPacket(0x09, packet[2:])
print(str(packet))
