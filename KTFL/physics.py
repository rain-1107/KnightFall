import pygame
import random


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def list(self):
        return [self.x, self.y]


# two points with start being furthest left point and highest and lowest points to make intersection calculations easier
class Line:
    def __init__(self, point1, point2):
        if type(point1) == tuple or type(point1) == list:
            point1 = Vector2(*point1)
        if type(point2) == tuple or type(point2) == list:
            point2 = Vector2(*point2)
        if point1.x <= point2.x:
            self.start = point1
            self.end = point2
        else:
            self.start = point2
            self.end = point1
        if point1.y <= point2.y:
            self.highest = point2
            self.lowest = point1
        else:
            self.highest = point1
            self.lowest = point2

    @staticmethod
    def get_vector_line(point, vector):
        if type(point) == tuple or type(point) == list:
            point = Vector2(*point)
        if type(vector) == tuple or type(vector) == list:
            vector = Vector2(*vector)
        return Line(point, (point.x+vector.x, point.y+vector.y))


# a set of lines that make a shape
class Polygon:
    def __init__(self, points):
        self.points = points
        self.lines = []
        for i, point in enumerate(points):
            if i + 1 != len(points):
                self.lines.append(Line(Vector2(*point), Vector2(*points[i+1])))
            else:
                self.lines.append(Line(Vector2(*point), Vector2(*points[0])))

    def does_line_intersect(self, line):
        intersections = []
        for _line in self.lines:
            _inter = get_intersection(line, _line)
            if _inter:
                intersections.append(_inter)
        if intersections:
            return intersections
        return False


"""def get_intersection(line1: Line, line2: Line):
    try:
        m1 = (line1.start.y-line1.end.y)/(line1.start.x-line1.end.x)
    except ZeroDivisionError:
        m1 = 1000000000000
    try:
        m2 = (line2.start.y - line2.end.y) / (line2.start.x - line2.end.x)
    except ZeroDivisionError:
        m2 = 1000000000000
    if m1 == m2:
        return False
    c1 = line1.start.y - (m1*line1.start.x)
    c2 = line2.start.y - (m2 * line2.start.x)

    x = (c2-c1)/(m1-m2)
    y = x*m1+c1
    if line1.start.x <= x <= line1.end.x and line2.start.x <= x <= line2.end.x:
        if line1.lowest.y <= y <= line1.highest.y and line2.lowest.y <= y <= line2.highest.y:
            return x, y
    return False"""


# return intersection of two line segments (only returns coordinate if it is on both segments
def get_intersection(line1: Line, line2: Line):
    xdiff = (line1.start.x - line1.end.x, line2.start.x - line2.end.x)
    ydiff = (line1.start.y - line1.end.y, line2.start.y - line2.end.y)

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        return False

    d = (det(line1.start.list(), line1.end.list()), det(line2.start.list(), line2.end.list()))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div

    if line1.start.x < x < line1.end.x and line2.start.x < x < line2.end.x:
        if line1.lowest.y < y < line1.highest.y and line2.lowest.y < y < line2.highest.y:
            return x, y
    return False
