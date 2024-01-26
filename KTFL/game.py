import pygame
from KTFL.display import Camera


class Scene:
    def __init__(self, file):
        self.file = file

    def load(self, display):
        ...

    @staticmethod
    def load_from_file(file, display):
        ...