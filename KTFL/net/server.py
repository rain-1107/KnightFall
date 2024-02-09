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
        self.threads = []
        self.alive = True

    def get_message(self):
        if self.messages.__len__() != 0:
            return self.messages.pop(0)


class Server:
    def __init__(self, size, variables: dict = {1: Data(1, "Test", 0, NUMBER)}):
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
                client.threads.append(threading.Thread(target=self.handle_recv, args=(client,)).start())
                client.threads.append(threading.Thread(target=self.handle_send, args=(client,)).start())

    def handle_recv(self, client: ServerClient):
        while client.alive:
            try:
                received = client.cin.recv(8)
            except ConnectionResetError:
                self.close_connection(client)
                return
            message = Message.decode(received)
            if message:
                if message.message_type == UPDATE_VAR:
                    if message.id in self.variables and (
                            self.variables[message.id].owner is None or self.variables[message.id].owner == client):
                        self.variables[message.id].value = message.data
                        for c in self.clients:
                            c.messages.append(message)
                elif message.message_type == CREATE_INTERPOLATED_VAR and message.id not in self.variables:
                    string = client.cin.recv(int(message.data)).decode("utf-8")
                    message.string = string
                    self.variables[message.id] = Data(message.id, string, message.data, message.data_type)
                    self.variables[message.id].interpolated = True
                    self.variables[message.id].owner = client
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == CREATE_VAR and message.id not in self.variables:
                    string = client.cin.recv(int(message.data)).decode("utf-8")
                    message.string = string
                    self.variables[message.id] = Data(message.id, string, message.data, message.data_type)
                    self.variables[message.id].owner = client
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == STRING_MESSAGE and message.id not in self.variables:
                    string = client.cin.recv(int(message.data)).decode("utf-8")
                    message.string = string
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == DELETE_VAR:
                    if message.id in self.variables and (self.variables[message.id].owner is None or self.variables[message.id].owner == client):
                        self.variables.pop(message.id)
                        for c in self.clients:
                            c.messages.append(message)
                elif message.message_type == CLOSE_CONNECTION:
                    self.close_connection(client)

    def handle_send(self, client: ServerClient):
        for id in self.variables:
            var = self.variables[id]
            if var.interpolated:
                client.cout.send(Message(CREATE_INTERPOLATED_VAR, var.value, var.data_type, id).get_bytes())
            else:
                client.cout.send(Message(CREATE_VAR, var.value, var.data_type, id).get_bytes())
        while client.alive:
            msg = client.get_message()
            if msg:
                client.cout.send(msg.get_bytes())
                if msg.string:
                    client.cout.send(msg.get_string_bytes())

    def close_connection(self, client):
        print(f"Closing connection with {client.ip}")
        self.clients.remove(client)
        client.alive = False
        for thread in self.clients:
            thread.join()
        for id in self.variables.copy():
            if self.variables[id] == client:
                self.variables.pop(id)
                for c in self.clients:
                    c.messages.append(Message(DELETE_VAR, 0, NUMBER, id))


if __name__ == '__main__':
    server = Server(2)
    server.run()
    while True:
        input()
        for id in server.variables:
            print(f"{server.variables[id].name}: {server.variables[id].value}")