import queue
from ChatSocket import ChatSocket
class ChatServerClient(ChatSocket):
    def __init__(self,sock, **properties):
        super().__init__(sock)
        self.properties = properties

    def set(self, **kwargs):
        for k,v in kwargs.items():
            self.properties[k] = v

    def get(self, key):
        try:
            return self.properties[key]
        except KeyError:
            return None
