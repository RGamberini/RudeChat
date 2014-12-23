import cProfile
from ChatServer import ChatServer
chatServer = ChatServer("localhost", 3232, 5)

#cProfile.run(chatServer.listen())
while True:
    chatServer.listen()
