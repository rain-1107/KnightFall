import KTFL
import pygame
from KTFL.physics import Vector2
import random

screen = KTFL.display.Display((1000, 1000), fullscreen=False)
camera = KTFL.display.Camera((1000, 1000), position=(0, 0))
screen.add_camera(camera)
inp = KTFL.control.Input()


def cool():
    print("cool")


button = KTFL.gui.Button((100, 50), (50, 50), cool, "dark", "selected")


while True:
    inp.update()
    camera.surface.fill((255, 255, 255))
    button.update(camera.surface, inp)
    screen.update()
