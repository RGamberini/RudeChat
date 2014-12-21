import select, logging, sys, queue, struct, socket
from ChatSocket import ChatSocket
from ChatServerClient import ChatServerClient
# class Room:
#     def __init__(self, name, password="", MOTD=""):
#         self.name = name
#         self.password = password
#         self.MOTD = MOTD

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class ChatServer(ChatSocket):
    c = 0

    def __init__(self, host, port, connections):
        super().__init__()
        # DEBUG
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # END DEBUG
        self.sock.bind((host, port))
        self.sock.listen(connections)
        #Non blocking
        self.sock.setblocking(0)
        # List of currently connected clients
        self.clients = []

    def addToAllQueues(self, data):
        for sock in self.clients:
            sock.put(data)

    def remove_client(self, sock):
        self.clients.remove(sock)
        sock.close()

    def handlePacket(self, header,sock):
        # Now that we've received the header
        # Grab the packet off the stream
        packet = self.unpackPacket(header, sock)
        if header == self.headers["Login"]:
            logging.debug("Login Attempt...")

            sock.name = packet["name"]
            sock.id = self.c

            # Create the login confirm packet
            confirm = self.packPacket(self.headers["LoginConfirm"], id=self.c)
            # Add it to the socks message queue
            sock.put(confirm)
            logging.debug(packet["name"] + " has logged in with id: " + str(self.c))

            self.c += 1
        elif header == self.headers["ClientMessage"]:
            logging.debug("New Message!")
            new_message = self.packPacket(self.headers["ServerMessage"], name=sock.name, message=packet["message"])
            self.addToAllQueues(new_message)

    def listen(self):
        while True:
            # The server socket to check for incoming clients aswell as all
            # of our current clients which may have sent us something
            readers = [self.sock] + self.clients

            # All clients should return as writers
            writers =  self.clients

            readable, writable, exceptional = select.select(readers, writers, self.clients, 8000)

            for sock in readable:
                if sock is self.sock: # Server Case
                    logging.info("New Connection!")
                    client, clientaddress = sock.accept()
                    client.setblocking(0)
                    # Record the client in list of clients and generate an empty message queue for them
                    self.clients.append(ChatServerClient(client))
                else: # Client Case
                    # Grab the header off the stream
                    header = sock.chat_recv(self.typeLength["short"])
                    if header:
                        header = struct.unpack(self.structKeys["short"], header)[0]
                        logging.debug("Client sent us a " +  self.headers[header] + " packet")
                        self.handlePacket(header, sock)
                    else: #Empty header means dead connection
                        logging.info(sock.name + " has disconnected")
                        remove_client(sock)
                for sock in writable:
                    if sock.writing == True:
                        next_msg = sock.get()
                        logging.debug("Sending: " + str(next_msg) + " to " + sock.name)
                        sock.chat_send(next_msg, len(next_msg))

                for sock in exceptional: # Exception means its dead
                    remove_client(sock)
