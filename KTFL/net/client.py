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
        self._vars = {}
        self.messages = []
        self.received_data = []
        self.connected = False
        self.id = 0

    def run(self):
        try:
            print("Trying to connect")
            self.outs.connect((self.ip, PORT_TO_SERVER))
            self.ins.connect((self.ip, PORT_TO_CLIENT))
        except ConnectionRefusedError:
            print("Failed to connect to client")
            return False
        self.connected = True
        threading.Thread(target=self.sending).start()
        threading.Thread(target=self.receiving).start()
        self.messages.append(Message(CLIENT_ID_REQUEST, 0, NUMBER, 0))
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
                if message.message_type == UPDATE_VAR and message.id in self._vars:
                    self._vars[message.id].value = message.data
                    if message.data_type == STRING:
                        string = self.ins.recv(int(message.data)).decode("utf-8")
                        message.string = string
                        self._vars[message.id].value = string
                elif message.message_type == CREATE_INTERPOLATED_VAR and message.id not in self._vars:
                    string = self.ins.recv(int(message.data)).decode("utf-8")
                    self._vars[message.id] = InterpolatedData(message.id, string, None, message.data_type)
                elif message.message_type == CREATE_VAR and message.id not in self._vars:
                    string = self.ins.recv(int(message.data)).decode("utf-8")
                    self._vars[message.id] = Data(message.id, string, None, message.data_type)
                elif message.message_type == DELETE_VAR and message.id in self._vars:
                    self._vars.pop(message.id)
                elif message.message_type == STRING_MESSAGE:
                    string = self.ins.recv(int(message.data)).decode("utf-8")
                    message.string = string
                    self.received_data.append(message)
                elif message.message_type == CLOSE_CONNECTION:
                    self.close_connection()
                elif message.message_type == CLIENT_ID_REQUEST:
                    self.id = int(message.data)
                elif message.message_type == UNUSED_ID_REQUEST:
                    self.received_data.append(message)
        print("Receiving loop ending")

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
        print("Sending loop ending")

    def close_connection(self):
        print("Closing connection")
        self.connected = False

    def create_variable(self, name: str, value, data_type, id=None):  # NOTE: This function will pause running to wait for a response
        if id is None:
            self.messages.append(Message(UNUSED_ID_REQUEST, 0, NUMBER, 0))
            waiting = True
            while waiting:
                for message in self.received_data:
                    if message.message_type == UNUSED_ID_REQUEST:
                        id = int(message.data)
                        self.received_data.remove(message)
                        waiting = False
        self.messages.append(Message(CREATE_VAR, name.__len__(), NUMBER, id, string=name))
        self.update_variable(id, value, data_type)
        waiting = True
        while waiting:
            if id in self.variables:
                return

    def update_variable(self, id, var, data_type):
        if data_type == STRING:
            msg = Message(UPDATE_VAR, var.__len__(), STRING, id)
            msg.string = var
            self.messages.append(msg)
            return
        self.messages.append(Message(UPDATE_VAR, var, data_type, id))

    def send_string_message(self, string):
        self.messages.append(Message(STRING_MESSAGE, string.__len__(), NUMBER, 0, string))

    def get_var_by_id(self, id):
        try:
            return self._vars[id]
        except KeyError:
            return None

    def get_var_by_name(self, name):
        for key in self._vars:
            if self._vars[key].name == name:
                return self._vars[key]
        return None

    @property
    def variables(self):
        return self._vars.copy()


if __name__ == '__main__':
    client = Client("local")
    client.run()
    while client.connected:
        input()
    print("Closing main thread")