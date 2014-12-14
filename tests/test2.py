import socket, testClient
#Create an INET STREAMing socket
clientsocket =  testClient.testClientSocket()
#Connect to local machine on my own port
clientsocket.connect('localhost', 3232)
name = "RudyGamb"
clientsocket.sendIM(name)
