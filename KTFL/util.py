import math
import pygame
import random
from .gui import get_text_surf

IMAGE_CACHE = {}


def load_image(img, size=[50,50]):
    if type(img) == str:
        if img in IMAGE_CACHE:
            return IMAGE_CACHE[img]
        try:
            _image = pygame.image.load(img).convert_alpha()
            IMAGE_CACHE[img] = _image
        except FileNotFoundError:
            _surf = pygame.surface.Surface(size)
            _surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            text = get_text_surf(f"{img}")
            _surf.blit(text,
                       ((size[0] / 2) - (text.get_size()[0] / 2), (size[1] / 2) - (text.get_size()[1] / 2)))
            _image = _surf.convert()
        return _image
    return img


def rect_collision_list(obj, obj_list):
    hit_list = []
    for rect in obj_list:
        if obj.colliderect(rect):
            hit_list.append(rect)
    return hit_list


def point_in_rects(point, obj_list):
    point = Vector2.list_to_vec(point)
    _list = []
    for obj in obj_list:
        if obj.left <= point.x < obj.right:
            if obj.top <= point.y < obj.bottom:
                _list.append(obj)
    return _list


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def normalise(self):
        dist = math.sqrt(self.x**2+self.y**2)
        self.x = self.x/dist
        self.y = self.y/dist

    def set(self, other):
        self.x = other.x
        self.y = other.y

    def __add__(self, other):
        return Vector2(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Vector2(self.x-other.x, self.y-other.y)

    def __mul__(self, other):
        if type(other) == Vector2:
            return Vector2(self.x*other.x, self.y*other.y)
        return Vector2(self.x*other, self.y*other)

    def __truediv__(self, other):
        return Vector2(self.x/other.x, self.y/other.y)

    def __str__(self):
        return "x: {x}, y: {y}".format(x=self.x, y=self.y)

    def snap_to_grid(self, grid_size_x, grid_size_y, apply=False):
        snapped_x = round(self.x / grid_size_x) * grid_size_x
        snapped_y = round(self.y / grid_size_y) * grid_size_y
        if apply:
            self.x = snapped_x
            self.y = snapped_y
        return snapped_x, snapped_y

    def copy(self):
        return Vector2(self.x, self.y)

    @property
    def list(self):
        return [self.x, self.y]

    @property
    def tuple(self):
        return (self.x, self.y)

    @staticmethod
    def list_to_vec(lst):
        if type(lst) == tuple or type(lst) == list:
            return Vector2(*lst)
        return lst


class Line:
    def __init__(self, start, end):
        self.point1 = Vector2.list_to_vec(start)
        self.point1 = Vector2(round(self.point1.x*10)/10, round(self.point1.y*10)/10)
        self.point2 = Vector2.list_to_vec(end)
        self.point2 = Vector2(round(self.point2.x * 10) / 10, round(self.point2.y * 10) / 10)

    def get_intersection(self, other):
        xdiff = (self.point1.x - self.point2.x, other.point1.x - other.point2.x)
        ydiff = (self.point1.x - self.point2.y, other.point1.y - other.point2.y)

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            return False

        d = (det(self.point1.list, self.point2.list), det(other.point1.list, other.point2.list))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div

        if self.leftmost.x <= x <= self.rightmost.x and other.leftmost.x <= x <= other.rightmost.x:
            if self.lowest.y <= y <= self.highest.y and other.lowest.y <= y <= other.highest.y:
                return x, y
        return False

    @property
    def leftmost(self):
        if self.point1.x < self.point2.x:
            return self.point1
        return self.point2

    @property
    def rightmost(self):
        if self.point1.x > self.point2.x:
            return self.point1
        return self.point2

    @property
    def highest(self):
        if self.point1.y < self.point2.y:
            return self.point1
        return self.point2

    @property
    def lowest(self):
        if self.point1.y > self.point2.y:
            return self.point1
        return self.point2
