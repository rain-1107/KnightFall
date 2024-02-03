import pygame
import random
from KTFL.gui import get_text_surf
from KTFL.util import Vector2


class Sprite:
    def __init__(self, size, position, image=None, colour=(255, 255, 255), id=0):
        self.id = id
        self.size = Vector2.list_to_vec(size)
        self.position = Vector2.list_to_vec(position)
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

    def draw_to(self, surf: pygame.surface.Surface):
        surf.blit(self.image, self.position.list)


class AnimatedSprite(Sprite):
    def __init__(self, size, position, image_data: dict, id=0):
        super().__init__(size, position, id=id)
        self.image_data = image_data
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