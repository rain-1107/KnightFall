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
line = KTFL.physics.Line.get_vector_line((0, 0), (200, 200))

while True:
    inp.update()
    camera.surface.fill((255, 255, 255))
    pygame.draw.line(camera.surface, (0, 0, 0), line.start.list(), line.end.list(), 100)
    if inp.on_action("next"):
        print("next")
    button.update(camera.surface, inp)
    screen.update()
