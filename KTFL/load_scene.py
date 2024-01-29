import pygame
from KTFL.display import Camera


class SceneController:
    def __init__(self):
        self.scenes = {}
        self.current_scene = None

    def set_scene(self, scene):
        self.current_scene = scene

    def get_cameras(self):
        ...


class Menu:
    def __init__(self):
        ...