from time import time, sleep, process_time
from math import trunc


# message types
EVENT = 0
VARIABLE = 1

# message data types
BOOL = 0
NUMBER = 1
VECTOR = 2


PORT_TO_CLIENT = 25565
PORT_TO_SERVER = 65526


class Interpolated:
    def __init__(self, start_val):
        self.data_type = type(start_val)
        self.current_val = [start_val, time()]
        self.prev_val = [start_val, time()]

    @property
    def value(self):
        if self.current_val[1]-self.prev_val[1] == 0:
            return self.current_val[0]
        val = ((time()-self.current_val[1])*(self.current_val[0]-self.prev_val[0])/(self.current_val[1]-self.prev_val[1]))
        if abs(val) > abs(self.current_val[0] - self.prev_val[0]):
            return self.current_val[0]
        return self.prev_val[0] + val

    @value.setter
    def value(self, other):
        self.prev_val = self.current_val
        self.current_val = [other, time()]


class Message:
    def __init__(self, message_type: int, data, data_type: int, data_id):
        self.message_type = message_type
        self.data = data
        self.data_type = data_type
        self.id = data_id
        self._bytes = None

    def get_bytes(self):
        if self._bytes:
            return self._bytes
        final = bytearray(bytes(8))
        final[0] = self.message_type * 16 + self.data_type
        final[1] = self.id
        if self.data_type == VECTOR:
            data = [trunc(self.data[0] * 25600), trunc(self.data[1] * 25600)]
            byte_i = 2
            for axis in data:
                for i in range(3, 0, -1):
                    bit_strength = 2**(i*8)
                    byte = axis // bit_strength
                    axis = axis % bit_strength
                    final[byte_i] = byte
                    byte_i += 1

            self._bytes = final
            return final
        if self.data_type == NUMBER:
            data = trunc(self.data * 256000)
            byte_i = 2
            for i in range(6, 0, -1):
                bit_strength = 2 ** (i * 8)
                byte = data // bit_strength
                data = data % bit_strength
                final[byte_i] = byte
                byte_i += 1
            self._bytes = final
            return final

    @staticmethod
    def decode(binary):
        message_type = binary[0] // 16
        variable_type = binary[0] % 16
        id = binary[1]
        if variable_type == VECTOR:
            data = [int.from_bytes(bytes(binary[2:5]), "big", signed=False)/100,
                    int.from_bytes(bytes(binary[5:8]), "big", signed=False)/100]
        elif variable_type == NUMBER:
            data = int.from_bytes(bytes(binary[2:8]), "big", signed=False)/1000
        return Message(message_type, data, variable_type,  id)
