import queue
from ChatSocket import ChatSocket
class ChatServerClient(ChatSocket):
    def __init__(self,sock):
        super().__init__(sock)
        self.id = -1
        self.name = ""
