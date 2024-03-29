import socket
import random
import sys
import threading
try:
    from .data import *
except ImportError:
    from data import *


class ServerClient:
    def __init__(self, ins, outs, ip):
        self.ins = ins
        self.outs = outs
        self.ip = ip
        self.id = 0
        self.messages = []
        self.threads = []
        self.alive = True

    def get_message(self):
        if self.messages.__len__() != 0:
            return self.messages.pop(0)


class Server:
    def __init__(self, size, variables={}):
        self.size = size
        self.variables = variables
        self.taken_ids = []
        self.free_ids = []
        self.running = False
        for i in range(256):
            self.free_ids.append(i)
        self.outs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ins = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ""
        self.outs.bind((host, PORT_TO_CLIENT))
        self.ins.bind((host, PORT_TO_SERVER))
        print("Binding to ports")
        self.clients = []

    def run(self):
        self.running = True
        self.outs.listen(self.size)
        self.ins.listen(self.size)
        print("Listening for connection")
        while self.running:
            try:
                cin, addrin = self.ins.accept()
                cout, addrout = self.outs.accept()
            except OSError:
                break
            print(f"Handling connection from {addrin[0]}")
            if addrin[0] == addrout[0]:
                client = ServerClient(cin, cout, addrin[0])
                client.id = self.clients.__len__()
                self.clients.append(client)
                client.threads.append(threading.Thread(target=self.handle_recv, args=(client,)))
                client.threads.append(threading.Thread(target=self.handle_send, args=(client,)))
                for thread in client.threads:
                    thread.start()
        print("Stopped listening for connections")

    def handle_recv(self, client: ServerClient):
        while client.alive:
            try:
                received = client.ins.recv(8)
            except ConnectionResetError:
                self.close_connection(client)
                return
            except ConnectionAbortedError:
                break
            try:
                message = Message.decode(received)
            except:
                print("Error decoding message")
                message = None
            if message:
                if message.message_type == UPDATE_VAR:
                    if message.id in self.variables and \
                            (self.variables[message.id].owner is None or self.variables[message.id].owner == client):
                        self.variables[message.id].value = message.data
                        self.variables[message.id].data_type = message.data_type
                        if message.data_type == STRING:
                            string = client.ins.recv(int(message.data)).decode("utf-8")
                            message.string = string
                            self.variables[message.id].value = string
                        for c in self.clients:
                            c.messages.append(message)
                elif message.message_type == CREATE_INTERPOLATED_VAR and message.id not in self.variables:
                    string = client.ins.recv(int(message.data)).decode("utf-8")
                    message.string = string
                    self.free_ids.remove(message.id)
                    self.taken_ids.append(message.id)
                    self.variables[message.id] = Data(message.id, string, message.data, message.data_type)
                    self.variables[message.id].interpolated = True
                    self.variables[message.id].owner = client
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == CREATE_VAR and message.id not in self.variables:
                    string = client.ins.recv(int(message.data)).decode("utf-8")
                    message.string = string
                    self.free_ids.remove(message.id)
                    self.taken_ids.append(message.id)
                    self.variables[message.id] = Data(message.id, string, message.data, message.data_type)
                    self.variables[message.id].owner = client
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == STRING_MESSAGE and message.id not in self.variables:
                    string = client.ins.recv(int(message.data)).decode("utf-8")
                    message.string = string
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == DELETE_VAR and message.id in self.variables and (self.variables[message.id].owner is None or self.variables[message.id].owner == client):
                    self.variables.pop(message.id)
                    self.taken_ids.pop(message.id)
                    self.free_ids.append(message.id)
                    for c in self.clients:
                        c.messages.append(message)
                elif message.message_type == CLOSE_CONNECTION:
                    self.close_connection(client)
                elif message.message_type == CLIENT_ID_REQUEST:
                    client.messages.append(Message(CLIENT_ID_REQUEST, client.id, NUMBER, 0))
                elif message.message_type == UNUSED_ID_REQUEST:
                    client.messages.append(Message(UNUSED_ID_REQUEST, random.choice(self.free_ids), NUMBER, 0))
        print(f"Receiving loop ended for {client.ip}")
        return

    def handle_send(self, client: ServerClient):
        for id in self.variables:
            var = self.variables[id]
            create_type = CREATE_VAR
            if var.interpolated:
                create_type = CREATE_INTERPOLATED_VAR
            create_msg = Message(create_type, var.name.__len__(), NUMBER, id, string=var.name)
            client.outs.send(create_msg.get_bytes())
            client.outs.send(create_msg.get_string_bytes())
            if var.data_type != STRING:
                msg = Message(UPDATE_VAR, var.value, var.data_type, id, string=var.value)
                client.outs.send(msg.get_bytes())
                client.outs.send(msg.get_bytes())
            else:
                client.outs.send(Message(UPDATE_VAR, var.value, var.data_type, id).get_bytes())
        while client.alive:
            msg = client.get_message()
            if msg:
                try:
                    client.outs.send(msg.get_bytes())
                    if msg.string:
                        client.outs.send(msg.get_string_bytes())
                except ConnectionResetError:
                    self.close_connection(client)
                except ConnectionAbortedError:
                    break
        print(f"Sending loop ended for {client.ip}")
        return

    def close_connection(self, client):
        try:
            print("Attempting to close connection")
            self.clients.remove(client)
            client.alive = False
            for id in self.variables.copy():
                if self.variables[id] == client:
                    self.variables.pop(id)
                    for c in self.clients:
                        c.messages.append(Message(DELETE_VAR, 0, NUMBER, id))
            print(f"Closing connection with {client.ip} [ID: {client.id}]")
            client.outs.send(Message(CLOSE_CONNECTION, 0, NUMBER, 0).get_bytes())
            client.ins.close()
            client.outs.close()
        except (ValueError, ConnectionResetError, OSError):
            pass

    def close(self):
        self.outs.close()
        self.ins.close()
        self.running = False
        for c in self.clients:
            print("Trying to close")
            self.close_connection(c)


if __name__ == '__main__':
    server = Server(0)
    run = threading.Thread(target=server.run)
    run.start()
    while True:
        com = input()
        if com == "exit":
            server.close()
            run.join(timeout=3)
            break
        for id in server.variables:
            print(f"{server.variables[id].name}: {server.variables[id].value}")
    print("Main thread ending")