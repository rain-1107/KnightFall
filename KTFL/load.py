import random

import pygame
import json

from .gui import get_text_surf
from .util import *
from .draw import Sprite, AnimatedSprite


class Level:
    def __init__(self, file):
        self.file = file
        self.raw = {}
        self.meta = {}
        self.layer_data = {}
        self.layers = []

    def load(self):
        try:
            self.raw = json.load(open(self.file, "r"))
        except FileNotFoundError:
            print("unable to find level file")
            return
        self.meta = self.raw["meta"]
        self.layer_data = self.raw["layers"]
        self.layers = []
        for layer in self.layer_data:
            sprites = []
            for s in layer["sprites"]:
                if s["animated"]:
                    sprites.append(AnimatedSprite(s["size"], s["position"], s["image_data"], id=s["id"], tag=s["tag"]))
                sprites.append(Sprite(s["size"], s["position"], s["image_data"], id=s["id"], tag=s["tag"]))
            objects = []
            for obj in layer["objects"]:
                objects.append(Object(pygame.rect.Rect(*obj["rect"]), obj["id"], obj["static"], obj["id"]))
            self.layers.append(Layer(layer["meta"], sprites, objects))

    def draw(self, camera):
        for layer in self.layers:
            layer.draw(camera)

    def update_raw(self):
        _layer_data = []
        for layer in self.layers:
            _layer_data.append(layer.raw)
        self.raw["layers"] = _layer_data
        self.raw["meta"] = self.meta

    def new_layer(self):
        self.layers.append(Layer(self.layers[0].meta, [], []))

    def delete_layer(self, layer):
        self.layers.remove(layer)


    @property
    def sprites(self):
        _list = []
        for layer in self.layers:
            _list.extend(layer.sprites)
        return _list

    @property
    def objects(self):
        _list = []
        for layer in self.layers:
            _list.extend(layer.objects)
        return _list

    @property
    def physics_rects(self):
        _list = []
        for layer in self.layers:
            _list.extend(layer.physics_rects)
        return _list


class Layer:
    def __init__(self, meta, sprites, objects):
        self.meta = meta
        self.sprites = sprites
        self.objects = objects
        self.used_sprite_ids = []
        for s in self.sprites:
            self.used_sprite_ids.append(s.id)
        self.used_object_ids = []
        for obj in self.objects:
            self.used_object_ids.append(obj.id)
        self.size = Vector2.list_to_vec(meta["size"])
        self.position = Vector2.list_to_vec(meta["position"])
        self.parallax = Vector2.list_to_vec(meta["parallax"])
        self.surf = pygame.surface.Surface(self.size.list, pygame.SRCALPHA)

    def draw(self, camera, absolute=False):
        self.surf.fill((0, 0, 0, 0))
        for s in self.sprites:
            s.draw_to(camera)
        camera.draw_surf(self.surf, self.position, parallax=self.parallax)

    def get_sprite_by_tag(self, tag):
        _list = []
        for sprite in self.sprites:
            if sprite.tag == tag:
                _list.append(sprite)
        return _list

    def add_sprite(self, sprite):
        self.sprites.append(sprite)
        sprite.level = self
        self.used_sprite_ids.append(sprite.id)

    def add_object(self, rect, id, static=True, tag=""):
        obj = Object(rect, id, static, tag)
        self.objects.append(obj)
        self.used_object_ids.append(obj.id)

    def delete_sprite(self, id):
        _sprite = self.get_sprite_by_id(id)
        if _sprite:
            self.sprites.remove(_sprite)
            self.used_sprite_ids.remove(id)

    def delete_object(self, id):
        _object = self.get_object_by_id(id)
        if _object:
            self.objects.remove(_object)
            self.used_object_ids.remove(id)

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

    def get_unused_sprite_id(self):
        id = 1
        while id in self.used_sprite_ids:
            id += 1
        return id

    def get_unused_object_id(self):
        id = 1
        while id in self.used_object_ids:
            id += 1
        return id

    def change_sprite_draw_priority(self, id, n=1):
        sprite = self.get_sprite_by_id(id)
        if not sprite:
            return
        try:
            original_index = self.sprites.remove(sprite)
            self.sprites.insert(original_index, 0)
        except ValueError:
            return
        index = n + original_index
        self.sprites.insert(index, sprite)
        self.sprites.remove(0)

    def set_meta(self, new):
        self.meta = new
        self.size = Vector2.list_to_vec(self.meta["size"])
        self.position = Vector2.list_to_vec(self.meta["position"])
        self.parallax = Vector2.list_to_vec(self.meta["parallax"])
        self.surf = pygame.surface.Surface(self.size.list, pygame.SRCALPHA)

    @property
    def physics_rects(self):
        _list = []
        for obj in self.objects:
            _list.append(obj.rect)
        return _list

    @property
    def raw(self):
        dict = {"objects": [], "sprites": [], "meta": {}}
        for object in self.objects:
            dict["objects"].append({"rect": [object.rect.left, object.rect.top, object.rect.width, object.rect.height], "static": object.static, "id": object.id, "tag": object.tag})
        for sprite in self.sprites:
            try:
                dict["sprites"].append(
                    {"id": sprite.id, "position": sprite.top_left.list, "size": sprite.size.list, "animated": True,
                     "image_data": sprite.raw_data})
            except AttributeError:
                dict["sprites"].append(
                    {"id": sprite.id, "position": sprite.top_left.list, "size": sprite.size.list, "animated": False,
                     "image_data": sprite.image_file, "tag": sprite.tag})
        dict["meta"] = self.meta
        return dict


class Object:
    def __init__(self, rect, id: int, static: bool, tag=""):
        self.rect = rect
        self.id = id
        self.static = static
        self.tag = tag
