import math


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def normalise(self):
        dist = math.sqrt(self.x**2+self.y**2)
        self.x = self.x/dist
        self.y = self.y/dist

    def __add__(self, other):
        return Vector2(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Vector2(self.x-other.x, self.y-other.y)

    def __mul__(self, other):
        return Vector2(self.x*other.x, self.y*other.y)
    
    def __str__(self):
        return "x: {x}, y: {y}".format(x=self.x, y=self.y)
        
    @property
    def list(self):
        return [self.x, self.y]

    @staticmethod
    def list_to_vec(lst):
        if type(lst) == tuple or type(lst) == list:
            return Vector2(*lst)
        return lst

    