import sys

import pygame

import KTFL

test = KTFL.display.Display(fullscreen=True)
camera = KTFL.display.Camera((200, 200), position=(100, 0))
test.cameras.append(camera)




while True:
    camera.surface.fill((200, 200, 200))
    test.update()