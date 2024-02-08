import socket
import threading
try:
    from .data import *
except ImportError:
    from data import *
from time import sleep


class Client:
    def __init__(self, ip):
        self.outs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ins = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.variables = {}
        self.messages = []

    def run(self):
        self.outs.connect((self.ip, PORT_TO_SERVER))
        self.ins.connect((self.ip, PORT_TO_CLIENT))
        threading.Thread(target=self.sending).start()
        threading.Thread(target=self.receiving).start()

    def receiving(self):
        while True:
            receive = self.ins.recv(8)
            if receive:
                message = Message.decode(receive)
                if message:
                    if message.message_type == CREATE_VAR and message.id not in self.variables: # TODO: make message receive logic for each message type
                        ...

    def sending(self):
        while True:
            if len(self.messages) != 0:
                message = self.messages.pop(0)
                self.outs.send(message.get_bytes())

    # TODO: add a function to create message query for each type
    def new_var(self, id, new, data_type):
        self.messages.append(Message(CREATE_VAR, new, data_type, id))

    def update_var(self, id, var, data_type):
        self.messages.append(Message(UPDATE_VAR, var, data_type, id))

if __name__ == '__main__':
    client = Client(socket.gethostname())
    client.run()
    client.update_var(2, 5, NUMBER)
    sleep(1)
    print(client.variables)