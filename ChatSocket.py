import socket
class ChatSocket:
    def __init__(self,sock=None):
        if (sock is None):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def send(self, msg, MSGLEN):
        if (isinstance(msg, str) and len(msg) < MSGLEN):
            msg = bytes(msg.ljust(length), "UTF-8")
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
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
