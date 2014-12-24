from ChatClient import ChatClient
chatClient = ChatClient("Rudy")
chatClient.connect("localhost", 3232)
chatClient.login()
chatClient.listen()
