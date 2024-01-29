import pygame
from KTFL.display import Camera


class GameController:
    def __init__(self):
        ...


class Level:
    def __init__(self, file):
        self.file = file
        self.entity_data = {}
        self.sprites = {}
        self.data = {}
        self.camera = None

    def load(self):
        ...

    def unload(self):
        ...

    @staticmethod
    def load_file(file):
        ...