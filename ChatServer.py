import sockets, select
import ChatSocket from ChatSocket
# class Room:
#     def __init__(self, name, password="", MOTD=""):
#         self.name = name
#         self.password = password
#         self.MOTD = MOTD

logger = logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
class ChatServer(ChatSocket):
    def __init__(self, host, port, connections):
        super().__init__()
        self.sock.bind((host, port))
        self.sock.listen(connections)
        self.sock.setblocking(0)
        self.clients = []
        # Outgoing message queues (socket:Queue)
        self.message_queues = {}

    def listen(self):
        while True:
            # The server socket to check for incoming clients aswell as all
            # of our current clients which may have sent us something
            readers = [self.sock] + self.clients

            # All clients should return as writers
            writers =  self.clients

            logger.debug("Polling connections... ")
            readable, writable, exceptional = select.select(readers, writers, self.clients, 8000)
            logger.debug("Polled!")

            for sock in readable:
                if sock is self.sock: # Server Case
                    logger.info("New Connection!")
                    client, clientaddress = sock.accept()
                    client.setblocking(0)
                    #Record the client in list of clients and generate an empty message queue for them
                    self.clients.append(client)
                    self.message_queues[client] = Queue.Queue()
                else: # Client Case
                    logger.debug("Message!")
                    header = sock.recv(2)
                    if header:
                        self.handlePacket(header, sock)
                    else: #Empty header means dead connection
                        self.clients.remove(sock)
                        del self.message_queues[sock]
                        sock.close()
                for sock in writable:
                    # TODO Read from message queues for each of the connections
                for sock in exceptional: # Exception means its dead
