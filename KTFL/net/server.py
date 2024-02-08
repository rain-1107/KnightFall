import socket
import threading
try:
    from .data import *
except ImportError:
    from data import *


class ServerClient:
    def __init__(self, cin, cout, ip):
        self.cin = cin
        self.cout = cout
        self.ip = ip
        self.messages = []

    def get_message(self):
        if self.messages.__len__() != 0:
            return self.messages.pop(0)


class Server:
    def __init__(self, size, variables: dict = {1: [0, False, NUMBER, None]}):
        self.size = size
        self.variables = variables
        self.outs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ins = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outs.bind((socket.gethostname(), PORT_TO_CLIENT))
        self.ins.bind((socket.gethostname(), PORT_TO_SERVER))
        print("Binding to ports")
        self.clients = []

    def run(self):
        self.outs.listen(self.size)
        self.ins.listen(self.size)
        print("Listening for connection")
        while True:
            cin, addrin = self.ins.accept()
            cout, addrout = self.outs.accept()
            print(f"Handling connection from {addrin[0]}")
            if addrin[0] == addrout[0]:
                client = ServerClient(cin, cout, addrin[0])
                self.clients.append(client)
                threading.Thread(target=self.handle_recv, args=(client,)).start()
                threading.Thread(target=self.handle_send, args=(client,)).start()

    def handle_recv(self, client: ServerClient):
        print(f"Created receiving thread for {client.ip}")
        while True:
            received = client.cin.recv(8)
            message = Message.decode(received)
            if message:
                print(f"Received message from {client.ip}")
                if message.message_type == CREATE_VAR and message.id not in self.variables: # TODO: add rest of type logic and handle disconnections and other errors
                    self.variables[message.id] = [message.data, False, message.data_type, client.cin]
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == CREATE_INTERPOLATED_VAR and message.id not in self.variables:
                    self.variables[message.id] = [message.data, True, message.data_type, client.cin]
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == UPDATE_VAR:
                    if message.id in self.variables and (self.variables[message.id][3] is None or self.variables[3] == client.cin):
                        self.variables[message.id][0] = message.data
                        for c in self.clients:
                            c.messages.append(message)

    def handle_send(self, client: ServerClient):
        print(f"Created sending thread for {client.ip}")
        for id in self.variables:
            var = self.variables[id]
            if var[2]:
                client.cout.send(Message(CREATE_INTERPOLATED_VAR, var[0], var[2], id).get_bytes())
            else:
                client.cout.send(Message(CREATE_VAR, var[0], var[2], id).get_bytes())
        while True:
            msg = client.get_message()
            if msg:
                print(f"Sending {client.ip} message")
                client.cout.send(msg.get_bytes())


if __name__ == '__main__':
    server = Server(1)
    server.run()