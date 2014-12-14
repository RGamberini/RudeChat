import socket
class testClientSocket:
    def __init__(self,sock=None):
        if (sock is None):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host,port))

    def send(self, msg, MSGLEN):
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            #print("Message: " + msg.decode("UTF-8").strip() + "\tSent: " + str(sent) + "\nTotal: " + str(totalsent) + "\tLength: " + str(MSGLEN))
            totalsent = totalsent + sent

    def recv(self, MSGLEN):
        msg = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            pull = self.sock.recv(MSGLEN - bytes_recd)
            if pull == b'':
                raise RuntimeError("socket connection broken")
            msg.append(pull)
            bytes_recd += len(pull)
        return b''.join(msg)

    def bytesWithPadding(self,msg, length):
        return bytes(msg.ljust(length), "UTF-8")

    def sendIM(self, name, msg):
        self.send(self.bytesWithPadding(name, 8), 8)
        self.send(self.bytesWithPadding(msg, 256), 256)
