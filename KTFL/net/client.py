import socket
import threading
try:
    from .data import *
except ImportError:
    from data import *
from time import sleep


class Client:
    def __init__(self, ip):
        if ip == "local":
            ip = socket.gethostname()
        self.outs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ins = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.variables = {}
        self.messages = []
        self.received_strings = []
        self.connected = False

    def run(self):
        try:
            self.outs.connect((self.ip, PORT_TO_SERVER))
            self.ins.connect((self.ip, PORT_TO_CLIENT))
        except ConnectionRefusedError:
            print("Failed to connect to client")
            return False
        self.connected = True
        threading.Thread(target=self.sending).start()
        threading.Thread(target=self.receiving).start()
        return True

    def receiving(self):
        while self.connected:
            try:
                receive = self.ins.recv(8)
            except ConnectionResetError:
                self.close_connection()
                return
            message = Message.decode(receive)
            if message:
                if message.message_type == UPDATE_VAR and message.id in self.variables:
                    self.variables[message.id].value = message.data
                    if message.data_type == STRING:
                        string = self.ins.recv(int(message.data)).decode("utf-8")
                        message.string = string
                        self.variables[message.id].value = string
                elif message.message_type == CREATE_INTERPOLATED_VAR and message.id not in self.variables:
                    string = self.ins.recv(int(message.data)).decode("utf-8")
                    self.variables[message.id] = InterpolatedData(message.id, string, None, message.data_type)
                elif message.message_type == CREATE_VAR and message.id not in self.variables:
                    string = self.ins.recv(int(message.data)).decode("utf-8")
                    self.variables[message.id] = Data(message.id, string, None, message.data_type)
                elif message.message_type == DELETE_VAR and message.id in self.variables:
                    self.variables.pop(message.id)
                elif message.message_type == STRING_MESSAGE:
                    string = self.ins.recv(int(message.data)).decode("utf-8")
                    print(string)
                    self.received_strings.append(string)
                elif message.message_type == CLOSE_CONNECTION:
                    self.close_connection()

    def sending(self):
        while self.connected:
            if len(self.messages) != 0:
                message = self.messages.pop(0)
                try:
                    self.outs.send(message.get_bytes())
                except ConnectionResetError:
                    self.close_connection()
                    return
                if message.string:
                    self.outs.send(message.get_string_bytes())

    def close_connection(self):
        self.connected = False

    # TODO: add a function to create message query for each type
    def new_var(self, id, name: str, value, data_type):
        self.messages.append(Message(CREATE_VAR, name.__len__(), NUMBER, id, string=name))
        self.messages.append(Message(UPDATE_VAR, value, data_type, id))

    def update_var(self, id, var, data_type):
        if data_type == STRING:
            msg = Message(UPDATE_VAR, var.__len__(), STRING, id)
            msg.string = var
            self.messages.append(msg)
            return
        self.messages.append(Message(UPDATE_VAR, var, data_type, id))

    def send_string(self, string):
        self.messages.append(Message(STRING_MESSAGE, string.__len__(), NUMBER, 0, string))

    def get_var_by_id(self, id):
        try:
            return self.variables[id]
        except KeyError:
            return None

    def get_var_by_name(self, name):
        for key in self.variables:
            if self.variables[key][3] == name:
                return self.variables[key][3]
        return None


if __name__ == '__main__':
    client = Client("local")
    client.run()
    client.new_var(2, "Hello", 1, NUMBER)
    while True:
        val = client.get_var_by_id(2)
        if val:
            print(val.value)
        new = input()
        client.update_var(2, new, STRING)
