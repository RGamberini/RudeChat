import socket
import packetTestServer
serverSocket = packetTestServer.packetServer("localhost", 3232, 5)
serverSocket.listen()
