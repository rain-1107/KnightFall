import pygame
import json
from KTFL.sprite import *


class Level:
    def __init__(self, file):
        self.file = file
        self.meta = {}
        self.sprite_data = {}
        self.sprites = []
        self.physics_data = {}
        self.physics_objects = []

    def load(self):
        raw = json.load(open(self.file, "r"))
        self.meta = raw["meta"]
        self.sprite_data = raw["sprites"]
        self.physics_data = raw["physics"]
        for sprite in self.sprite_data:
            if sprite["animated"]:
                _sprite = AnimatedSprite(sprite["size"], sprite["position"], sprite["image_data"])
            else:
                _sprite = Sprite(sprite["size"], sprite["position"], sprite["image_data"])
            self.sprites.append(_sprite)
        for object in self.physics_data["objects"]:
            if object["static"] == True:
                self.physics_objects.append(pygame.rect.Rect(*object["rect"]))
