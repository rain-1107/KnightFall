import pygame

from .util import *
from copy import deepcopy


# TODO: this file can be renamed to draw.py since a lot of draw logic will have to be added here
# TODO: add ability to draw lines

class Sprite:
    def __init__(self, size, position, image=None, colour=(255, 255, 255), centered=False, id=0, tag="", level=None):
        self.id = id
        self.centered = centered
        self._size = Vector2.list_to_vec(size)
        self.top_left = Vector2(0, 0)
        self.position = position
        self.image_file = image
        self._tag = tag
        self.level = level

        if image:
            self._image = load_image(image, self._size.list)
        else:
            self._image = pygame.surface.Surface(self.size.list)
            self._image.fill(colour)
        self.size = self.image.get_size()

    def draw_to(self, surf: pygame.surface.Surface):  # TODO: abstract this to add to draw list
        surf.blit(self.image, self.top_left.list)

    def is_point_in_sprite(self, point):
        point = Vector2.list_to_vec(point)
        if self.top_left.x < point.x < self.top_left.x + self.size.x:
            if self.top_left.y < point.y < self.top_left.y + self.size.y:
                return True
        return False

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, new):
        self._tag = new

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new):
        self.image_file = new
        load_image(new, self.size.list)

    @property
    def size(self) -> Vector2:
        return self._size

    @size.setter
    def size(self, new):
        self._size = Vector2.list_to_vec(new)

    @property
    def position(self) -> Vector2:
        if self.centered:
            return self.centre
        return self.top_left

    @position.setter
    def position(self, new):
        if self.centered:
            self.centre = new
            return
        self.top_left = Vector2.list_to_vec(new)

    @property
    def centre(self) -> Vector2:
        return Vector2(self.top_left.x + (self.size.x / 2), self.top_left.y + (self.size.y / 2))

    @centre.setter
    def centre(self, new):
        _centre = Vector2.list_to_vec(new)
        self.top_left.set(Vector2(_centre.x-self.size.x/2, _centre.y-self.size.y/2))


class AnimatedSprite(Sprite):
    def __init__(self, size, position, image_data: dict, centered=False, id=0, tag=""):
        super().__init__(size, position, id=id, centered=centered, tag=tag)
        self.raw_data = deepcopy(image_data)
        self.image_data = deepcopy(image_data)
        for list in self.image_data:
            temp = []
            for image in self.image_data[list]["images"]:
                image = load_image(image, self.size.list)
                temp.append(image)
            self.image_data[list]["images"] = temp
        self.index = 0
        self.tick = 0
        self.state = next(iter(self.image_data))
        self.previous_state = next(iter(self.image_data))

    def update_animation(self, delta_time: float = 1 / 60):
        self.tick -= delta_time
        if self.tick < 0:
            self.tick = self.image_data[self.state]["tick"]
            self.index += 1
            if self.index > self.image_data[self.state]["images"].__len__() - 1:
                if self.image_data[self.state]["loop"]:
                    self.index = 0
                else:
                    self.change_state(self.previous_state)
            self._image = self.image_data[self.state]["images"][self.index]
            self.size = self.image.get_size()

    def change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state
        self.index = -1
        self.tick = 0
