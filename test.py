import sys

import pygame

import KTFL

screen = KTFL.display.Display(fullscreen=True)
camera = KTFL.display.Camera((854, 480), position=(0, 0))
screen.add_camera(camera)
gui = KTFL.display.Camera((1920, 1080))
screen.add_camera(gui)
sprite = KTFL.sprite.Sprite((50, 50), (50, 50))


while True:
    camera.surface.fill((200, 200, 200))
    camera.draw_to(sprite)
    gui.draw_surf(KTFL.gui.get_text_surf("Hello"), (100, 100))
    screen.update()