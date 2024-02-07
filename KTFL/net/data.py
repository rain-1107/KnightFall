from time import time, sleep


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