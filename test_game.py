import socket
import math
import KTFL
from OpenGL.GL import *

screen = KTFL.display.Display(fps=60, size=(800, 450), fullscreen=False)
game_cam = KTFL.display.Camera((256, 144))
screen.add_camera(game_cam)

sprite = KTFL.sprite.Sprite((0, 0), (10, 10), "images/image2.png")

screen.load_quads()

while True:
    game_cam.draw_sprite(sprite)
    screen.update()
