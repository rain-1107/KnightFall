import pygame
import random
from KTFL.gui import get_text_surf
from KTFL.util import Vector2
from copy import deepcopy


class Sprite:
    def __init__(self, size, position, image=None, colour=(255, 255, 255), centered=False, id=0, tag="", level=None):
        self.id = id
        self.centered = centered
        self.size = Vector2.list_to_vec(size)
        self.top_left = Vector2.list_to_vec(position)
        self.image_file = image
        self.tag = tag
        self.level = level

        if image:
            try:
                self.image = pygame.image.load(image).convert_alpha()
            except FileNotFoundError:
                _surf = pygame.surface.Surface(self.size.list)
                _surf.fill((random.randint(0, 255), random.randint(0, 255),random.randint(0, 255)))
                text = get_text_surf(f"{image}")
                _surf.blit(text, ((self.size.x / 2) - (text.get_size()[0] / 2), (self.size.y / 2) - (text.get_size()[1] / 2)))
                self.image = _surf.convert()
        else:
            self.image = pygame.surface.Surface(self.size.list)
            self.image.fill(colour)

    def set_tag(self, tag):  # TODO : encapsulate this variable (note to leo : https://stackoverflow.com/questions/48391851/call-python-method-on-class-attribute-change)
        if self.level:
            self.level.tags_index[self.tag][self.id] = None
            self.tag = tag
            self.level.tags_index[self.tag][self.id] = self
        else:
            self.tag = tag

    def draw_to(self, surf: pygame.surface.Surface):
        surf.blit(self.image, self.position.list)

    def set_position(self, new):
        self.top_left = Vector2.list_to_vec(new)

    def set_size(self, new):
        self.size = Vector2.list_to_vec(new)

    def set_image(self, file):
        self.image_file = file
        try:
            self.image = pygame.image.load(self.image_file).convert_alpha()
        except FileNotFoundError:
            _surf = pygame.surface.Surface(self.size.list)
            _surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            text = get_text_surf(f"{self.image_file}")
            _surf.blit(text,
                       ((self.size.x / 2) - (text.get_size()[0] / 2), (self.size.y / 2) - (text.get_size()[1] / 2)))
            self.image = _surf.convert()

    def is_point_in_sprite(self, point):
        point = Vector2.list_to_vec(point)
        if self.top_left.x < point.x < self.top_left.x + self.size.x:
            if self.top_left.y < point.y < self.top_left.y + self.size.y:
                return True
        return False
    
    @property
    def position(self):
        if self.centered:
            return Vector2(self.top_left.x - (self.size.x / 2), self.top_left.y)
        return self.top_left

    @property
    def centre(self):
        return Vector2(self.top_left.x - (self.size.x / 2), self.top_left.y)


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
