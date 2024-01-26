import pygame


class Sprite:
    def __init__(self, size, position, image=None, colour=(255, 255, 255)):
        self.size = size
        self.position = position
        if image:
            self.image = image
        else:
            self.image = pygame.surface.Surface(size)
            self.image.fill(colour)