import sys

import pygame

import KTFL

screen = KTFL.display.Display(fullscreen=True)
camera = KTFL.display.Camera((854, 480), position=(0, 0))
screen.add_camera(camera)
gui = KTFL.display.Camera((1920, 1080))
screen.add_camera(gui)
sprite = KTFL.sprite.AnimatedSprite((50, 50), (0, 0), {
    "idle": {
      "tick": 0.5,
      "loop": True,
      "images": [
        "sprites/player/idle-00.png",
        "sprites/player/idle-01.png",
        "sprites/player/idle-02.png"
      ]
    },
    "run": {
      "tick": 0.1,
      "loop": False,
      "images": [
        "sprites/player/run-00.png",
        "sprites/player/run-01.png",
        "sprites/player/run-02.png",
        "sprites/player/run-03.png",
        "sprites/player/run-04.png",
        "sprites/player/run-05.png"
      ]
    }
  })


while True:
    camera.surface.fill((200, 200, 200))
    camera.draw_to(sprite)
    sprite.update_animation()
    gui.draw_surf(KTFL.gui.get_text_surf("Hello"), (100, 100))
    screen.update()