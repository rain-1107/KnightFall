import socket
import threading
try:
    from .data import *
except ImportError:
    from data import *


class Client:
    def __init__(self, ip):
        self.outs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ins = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outs.connect((ip, PORT_TO_SERVER))
        self.ins.connect((ip, PORT_TO_CLIENT))

    def update(self):
        while True:
            self.outs.send(Message(VARIABLE, 255, NUMBER, 1).get_bytes())


if __name__ == '__main__':
    client = Client(socket.gethostname())
    while True:
        client.update()