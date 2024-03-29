from time import time, sleep, process_time
from math import trunc


# message types
CREATE_VAR = 0
CREATE_INTERPOLATED_VAR = 1
UPDATE_VAR = 2
DELETE_VAR = 3
CLOSE_CONNECTION = 4
STRING_MESSAGE = 5
CLIENT_ID_REQUEST = 6
UNUSED_ID_REQUEST = 7


# variable data types
BOOL = 0
NUMBER = 1
VECTOR = 2
STRING = 3


# standard ports for connection
PORT_TO_CLIENT = 65525
PORT_TO_SERVER = 65526


class Data:
    def __init__(self, id, name, value, data_type):
        self.id = id
        self.name = name
        self.value = value
        self.data_type = data_type
        self.interpolated = False
        self.owner = None


class InterpolatedData:
    def __init__(self, id, name, value, data_type):
        self.id = id
        self.name = name
        self.data_type = data_type
        self.current_val = [value, time()]
        self.prev_val = [value, time()]
        self.interpolated = True
        self.owner = None

    @property
    def value(self):
        try:
            if self.data_type == VECTOR:
                if self.current_val[1] == self.prev_val[1]:
                    return self.current_val[0]
                xval = ((time()-self.current_val[1])*(self.current_val[0][0]-self.prev_val[0][0]) /
                        (self.current_val[1]-self.prev_val[1]))
                if abs(xval) > abs(self.current_val[0][0] - self.prev_val[0][0]):
                    xval = self.current_val[0][0] - self.prev_val[0][0]
                yval = ((time() - self.current_val[1]) * (self.current_val[0][1] - self.prev_val[0][1]) /
                        (self.current_val[1] - self.prev_val[1]))
                if abs(yval) > abs(self.current_val[0][1] - self.prev_val[0][1]):
                    yval = self.current_val[0][1] - self.prev_val[0][1]
                return xval + self.prev_val[0][0], yval + self.prev_val[0][1]
            if self.current_val[1] == self.prev_val[1]:
                return self.current_val[0]
            val = ((time()-self.current_val[1])*(self.current_val[0]-self.prev_val[0])/(self.current_val[1]-self.prev_val[1]))
            if abs(val) > abs(self.current_val[0] - self.prev_val[0]):
                return self.current_val[0]
        except TypeError:
            return 0
        return self.prev_val[0] + val

    @value.setter
    def value(self, other):
        self.prev_val = self.current_val
        self.current_val = [other, time()]


class Message:
    def __init__(self, message_type: int, data, data_type: int, data_id, string=""):
        self.message_type = message_type
        self.data = data
        self.data_type = data_type
        self.id = data_id
        self._bytes = None
        self.string = string

    def get_bytes(self):
        if self._bytes:
            return self._bytes
        if self.message_type in [CREATE_VAR]:
            pass
        byte_list = bytearray(bytes(8))
        byte_list[0] = self.message_type * 16 + self.data_type
        byte_list[1] = self.id
        if self.data_type == VECTOR:
            data = [trunc(self.data[0] * 100), trunc(self.data[1] * 100)]
            data = [data[0].to_bytes(3, "big", signed=True), data[1].to_bytes(3, "big", signed=True)]
            byte_i = 2
            for axis in data:
                for i in range(0, 3):
                    byte_list[byte_i] = axis[i]
                    byte_i += 1

            self._bytes = byte_list
        if self.data_type == NUMBER or self.data_type == STRING:
            data = trunc(self.data * 1000)
            data = data.to_bytes(6, "big", signed=True)
            byte_i = 2
            for i in range(0, 6):
                byte_list[byte_i] = data[i]
                byte_i += 1
            self._bytes = byte_list
        if self.data_type == BOOL:
            data = 0
            if self.data: data += 1
            byte_list[8] = self.data
        return byte_list

    def get_string_bytes(self):
        return self.string.encode("utf-8")

    @staticmethod
    def decode(binary):
        try:
            message_type = binary[0] // 16
            variable_type = binary[0] % 16
            id = binary[1]
            if variable_type == VECTOR:
                data = [int.from_bytes(bytes(binary[2:5]), "big", signed=True)/100,
                        int.from_bytes(bytes(binary[5:8]), "big", signed=True)/100]
            elif variable_type == NUMBER or variable_type == STRING:
                data = int.from_bytes(bytes(binary[2:8]), "big", signed=True)/1000
            try:
                return Message(message_type, data, variable_type,  id)
            except UnboundLocalError:
                print(message_type, variable_type)
        except:
            return None
