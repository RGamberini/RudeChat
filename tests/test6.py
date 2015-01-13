from ChatSocket import ChatSocket
x = ChatSocket()
y = x.packPacket(x.headers["ClientMessage"],id=4,message="Hello World")
y = y[2:]
print(str(x.unpackPacket(len(y),y)))
