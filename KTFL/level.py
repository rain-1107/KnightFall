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
        self.objects = []

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
                        image_data[state]["images"][i] = image_data[state]["images"][i]
                _sprite = AnimatedSprite(sprite["size"], sprite["position"], sprite["image_data"], id=sprite["id"])
            else:
                _sprite = Sprite(sprite["size"], sprite["position"],
                                 sprite["image_data"], id=sprite["id"], tag=sprite["tag"])
            self.add_sprite(_sprite)
        for object in self.physics_data["objects"]:
            self.objects.append(Object(pygame.rect.Rect(*object["rect"]), object["id"], object["static"], object["tag"]))

    def get_sprite_by_tag(self, tag):
        _list = []
        for sprite in self.sprites:
            if sprite.tag == tag:
                _list.append(sprite)
        return _list

    def add_sprite(self, sprite: Sprite):
        self.sprites.append(sprite)
        sprite.level = self

    def add_object(self, rect, id, static=True, tag=""):
        self.objects.append(Object(rect, id, static, tag))

    def delete_sprite(self, id):
        _sprite = self.get_sprite_by_id(id)
        if _sprite:
            self.sprites.remove(_sprite)

    def delete_object(self, id):
        _object = self.get_object_by_id(id)
        if _object:
            self.objects.remove(_object)

    def get_sprite_by_id(self, id):
        for sprite in self.sprites:
            if sprite.id == id:
                return sprite
        return None

    def get_object_by_id(self, id):
        for object in self.objects:
            if object.id == id:
                return object
        return None

    def get_sprites_with_tag(self, tag):
        _list = []
        for sprite in self.sprites:
            if sprite.tag == tag:
                _list.append(sprite)
        return _list

    def get_objects_with_tag(self, tag):
        _list = []
        for obj in self.objects:
            if obj.tag == tag:
                _list.append(obj)
        return _list

    @property
    def physics_rects(self):
        _list = []
        for obj in self.objects:
            _list.append(obj.rect)
        return _list

    def update_raw(self):
        self.physics_data["objects"] = []
        for object in self.objects:
            self.physics_data["objects"].append({"rect": [object.rect.left, object.rect.top, object.rect.width, object.rect.height], "static": object.static, "id": object.id, "tag": object.tag})
        sprite_data = []
        for sprite in self.sprites:
            try:
                sprite_data.append(
                    {"id": sprite.id, "position": sprite.top_left.list, "size": sprite.size.list, "animated": True,
                     "image_data": sprite.raw_data})
            except AttributeError:
                sprite_data.append(
                    {"id": sprite.id, "position": sprite.top_left.list, "size": sprite.size.list, "animated": False,
                     "image_data": sprite.image_file, "tag": sprite.tag})
        self.raw = {"meta": self.meta, "physics": self.physics_data, "sprites": sprite_data}


class Object:
    def __init__(self, rect, id, static, tag=""):
        self.rect = rect
        self.id = id
        self.static = static
        self.tag = tag
