import socket
import threading
try:
    from .data import *
except ImportError:
    from data import *


class Server:
    def __init__(self):
        self.outs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ins = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outs.bind((socket.gethostname(), PORT_TO_CLIENT))
        self.ins.bind((socket.gethostname(), PORT_TO_SERVER))
        self.variables = {}

    def run(self):
        self.outs.listen(1)
        self.ins.listen(1)
        while True:
            cin, addrin = self.ins.accept()
            cout, addrout = self.outs.accept()
            print(addrin, addrout)
            if addrin[0] == addrout[0]:
                threading.Thread(target=self.handle, args=(cin, cout,)).start()

    def handle(self, cin, cout):
        while True:
            received = cin.recv(8)
            message = Message.decode(received)
            print(message.data)


if __name__ == '__main__':
    server = Server()
    server.run()