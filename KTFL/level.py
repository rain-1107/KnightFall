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
                image_data = sprite["image_data"]
                for state in image_data:
                    for i in range(len(image_data[state]["images"])):
                        image_data[state]["images"][i] = self.meta["image_folder"] + image_data[state]["images"][i]
                _sprite = AnimatedSprite(sprite["size"], sprite["position"], sprite["image_data"], id=sprite["id"])
            else:
                _sprite = Sprite(sprite["size"], sprite["position"],
                                         self.meta["image_folder"] + sprite["image_data"], id=sprite["id"])
            self.sprites.append(_sprite)
        for object in self.physics_data["objects"]:
            if object["static"] == True:
                self.physics_objects.append(pygame.rect.Rect(*object["rect"]))

    def add_sprite(self, sprite: Sprite):
        self.sprites.append(sprite)

    def delete_sprite(self, id):
        sprites = self.sprites.copy()
        for sprite in sprites:
            if sprite.id == id:
                self.sprites.remove(sprite)

    def get_sprite(self, id):
        for sprite in self.sprites:
            if sprite.id == id:
                return sprite
        return None

    def add_object(self, rect, id=-1, static=True):
        self.physics_objects.append(rect)
        # self.raw["physics"]["objects"].append({"rect": [rect.left, rect.top, rect.width, rect.height]})

    def update_raw(self):
        self.physics_data["objects"] = []
        for object in self.physics_objects:
            self.physics_data["objects"].append({"rect": [object.left, object.top, object.width, object.height], "static": False, "sprite_id": -1})

        sprite_data = []
        for sprite in self.sprites:
            try:
                sprite_data.append(
                    {"id": sprite.id, "position": sprite.top_left.list, "size": sprite.size.list, "animated": True,
                     "image_data": sprite.raw_data})
            except AttributeError:
                sprite_data.append(
                    {"id": sprite.id, "position": sprite.top_left.list, "size": sprite.size.list, "animated": False,
                     "image_data": sprite.image_file})
        self.raw = {"meta": self.meta, "physics": self.physics_data, "sprites": sprite_data}