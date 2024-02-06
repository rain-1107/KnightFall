import pygame
import random
from KTFL.gui import get_text_surf
from KTFL.util import Vector2
from copy import deepcopy


class Sprite:
    def __init__(self, size, position, image=None, colour=(255, 255, 255), centered=False, id=0, tag="", level=None):
        self.id = id
        self.centered = centered
        self._size = Vector2.list_to_vec(size)
        self.top_left = Vector2.list_to_vec(position)
        self.image_file = image
        self._tag = tag
        self.level = level

        if image:
            try:
                self._image = pygame.image.load(image).convert_alpha()
            except FileNotFoundError:
                _surf = pygame.surface.Surface(self.size.list)
                _surf.fill((random.randint(0, 255), random.randint(0, 255),random.randint(0, 255)))
                text = get_text_surf(f"{image}")
                _surf.blit(text, ((self.size.x / 2) - (text.get_size()[0] / 2), (self.size.y / 2) - (text.get_size()[1] / 2)))
                self._image = _surf.convert()
        else:
            self._image = pygame.surface.Surface(self.size.list)
            self._image.fill(colour)

    def draw_to(self, surf: pygame.surface.Surface):
        surf.blit(self.image, self.position.list)

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
        try:
            self._image = pygame.image.load(self.image_file).convert_alpha()
        except FileNotFoundError:
            _surf = pygame.surface.Surface(self.size.list)
            _surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            text = get_text_surf(f"{self.image_file}")
            _surf.blit(text,
                       ((self.size.x / 2) - (text.get_size()[0] / 2), (self.size.y / 2) - (text.get_size()[1] / 2)))
            self._image = _surf.convert()

    @property
    def size(self) -> Vector2:
        return self._size

    @size.setter
    def size(self, new):
        self._size = Vector2.list_to_vec(new)

    @property
    def position(self) -> Vector2:
        if self.centered:
            return Vector2(self.top_left.x - (self.size.x / 2), self.top_left.y)
        return self.top_left

    @position.setter
    def position(self, new):
        if self.centered:
            self.centre = new
            return
        self.top_left = Vector2.list_to_vec(new)

    @property
    def centre(self) -> Vector2:
        return Vector2(self.top_left.x - (self.size.x / 2), self.top_left.y)

    @centre.setter
    def centre(self, new):
        _centre = Vector2.list_to_vec(new)
        self.top_left.set(Vector2(_centre.x-self.size.x/2, _centre.y-self.size.y/2))


class AnimatedSprite(Sprite):
    def __init__(self, size, position, image_data: dict, centered=False, id=0):
        super().__init__(size, position, id=id, centered=centered)
        self.raw_data = deepcopy(image_data)
        self.image_data = deepcopy(image_data)
        for list in self.image_data:
            temp = []
            for image in self.image_data[list]["images"]:
                try:
                    temp.append(pygame.image.load(image).convert_alpha())
                except FileNotFoundError:
                    print(f"Error: File not found at {image}")
                    _surf = pygame.surface.Surface(self.size.list)
                    _surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                    text = get_text_surf(f"{image}")
                    _surf.blit(text, ((self.size.x / 2) - (text.get_size()[0]/2), (self.size.y / 2) - (text.get_size()[1]/2)))
                    temp.append(_surf)
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
            self.image = self.image_data[self.state]["images"][self.index]

    def change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state
        self.index = -1
        self.tick = 0
