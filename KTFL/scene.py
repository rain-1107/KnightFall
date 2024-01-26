import pygame
from KTFL.display import Camera


class Scene:
    def __init__(self, display):
        self.camera = Camera((640, 360))
        display.add_camera(self.camera)

    def update(self):
        pygame.draw.rect(self.camera.surface, (255, 255, 255), (100, 100, 150, 150))