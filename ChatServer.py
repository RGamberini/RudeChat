import select, logging, sys, queue, socket
from ChatSocket import ChatSocket
from ChatServerClient import ChatServerClient

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class ChatServer(ChatSocket):
    c = 0

    def __init__(self, host, port, connections):
        super().__init__()
        # DEBUG
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # END DEBUG
        self.host = host
        self.port = port
        self.sock.bind((host, port))
        self.sock.listen(connections)
        #Non blocking
        self.sock.setblocking(0)
        # List of currently connected clients
        self.clients = []
        print("Welcome to the RudeChat Server Version " + self.VERSION)

    def addToAllQueues(self, data):
        for sock in self.clients:
            sock.put(data)

    def add_client(self, sock):
        client, clientaddress = sock.accept()
        logging.info("New Connection coming from " + str(clientaddress[0]) + " on port " + str(clientaddress[1]))
        client.setblocking(0)
        # Record the client in list of clients and generate an empty message queue for them
        self.clients.append(ChatServerClient(client))
        self.clients[-1].set(id=self.c,address=clientaddress[0])
        self.c += 1

    def remove_client(self, client):
        logging.info("Connection " + client.get("address") + " is disconnecting")
        self.clients.remove(client)
        client.close()

    def handlePacket(self, client, length):
        # Now that we've received the length
        # Grab the packet off the stream
        header, packet = client.unpackPacket(length)
        if header == self.headers["Login"]:
            logging.debug("Login Attempt...")

            client.set(name=packet["name"])

            # Create the login confirm packet
            confirm = client.packPacket(self.headers["LoginConfirm"], id=client.get("id"))
            # Add it to the socks message queue
            client.put(confirm)
            logging.debug(packet["name"] + " has logged in with id: " + str(client.get("id")))
        elif header == self.headers["ClientMessage"]:
            logging.debug(client.get("name") + ": " + packet["message"])
            new_message = self.packPacket(self.headers["ServerMessage"], name=client.get("name"), message=packet["message"])
            self.addToAllQueues(new_message)

    def listen(self):
        # The server socket to check for incoming clients aswell as all
        # of our current clients which may have sent us something
        readers = [self.sock] + self.clients

        writers =  []
        # All clients should return as writers
        for client in self.clients:
            if client.writing:
                writers.append(client)

        readable, writable, exceptional = select.select(readers, writers, self.clients)
        logging.debug("Listening on " + self.host + ":" + str(self.port))

        for sock in readable:
            if sock is self.sock: # Server Case
                self.add_client(self.sock)
            else: # Client Case
                logging.info("Received a new message from client ")
                # Grab the header off the stream
                try:
                    length = sock.chat_recv(self.typeLength["short"])
                except ConnectionResetError:
                    self.remove_client(sock)
                    break
                if length:
                    length = sock.unpack("short", length)[0]
                    logging.debug("Client sent us " +  str(length) + " bytes")
                    self.handlePacket(sock, length)
                else: # Empty length means dead connection
                    self.remove_client(sock)

        for sock in writable:
            #logging.debug("Sending: " + str(next_msg) + " to " + sock.name)
            sock.send_waiting()

        for sock in exceptional: # Exception means its dead
            remove_client(sock)
