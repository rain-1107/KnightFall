import pygame
import json
from .sprite import *
from .util import *


class Level:
    def __init__(self, file):
        self.file = file
        self.raw = {}
        self.meta = {}
        self.sprite_data = {}
        self.sprites = []
        self.physics_data = {}
        self.physics_objects = []

    def load(self):
        try:
            self.raw = json.load(open(self.file, "r"))
        except FileNotFoundError:
            print("unable to find level file")
            return
        self.meta = self.raw["meta"]
        self.sprite_data = self.raw["sprites"]
        self.physics_data = self.raw["physics"]
        for sprite in self.sprite_data:
            if sprite["animated"]:
                _sprite = AnimatedSprite(sprite["size"], sprite["position"], sprite["image_data"])
            else:
                _sprite = Sprite(sprite["size"], sprite["position"], sprite["image_data"])
            self.sprites.append(_sprite)
        for object in self.physics_data["objects"]:
            if object["static"] == True:
                self.physics_objects.append(pygame.rect.Rect(*object["rect"]))

    def add_sprite(self, sprite: Sprite):
        self.sprites.append(sprite)
        try:
            self.raw["sprites"].append({"id": sprite.id, "position": sprite.top_left.list, "size": sprite.size.list, "animated": True, "image_data": sprite.raw_data})
        except NameError:
            self.raw["sprites"].append(
                {"id": sprite.id, "position": sprite.top_left.list, "size": sprite.size.list, "animated": False,
                 "image_data": sprite.image_file})

    def add_object(self, rect, id=-1, static=True):
        self.physics_objects.append(rect)
        self.raw["physics"]["objects"].append({"rect": [rect.left, rect.top, rect.width, rect.height]})