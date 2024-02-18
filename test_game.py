import socket
import math
import KTFL
from OpenGL.GL import *

screen = KTFL.display.Display(fps=60, size=(800, 450), fullscreen=False)
game_cam = KTFL.display.Camera((256, 144))
screen.add_camera(game_cam)

sprite = KTFL.sprite.Sprite((0, 0), (10, 10), "images/image2.png")

text = KTFL.draw.Text("Hi", screen.size.list)
text.load(screen.shader)
screen.load_quads()

while True:
    # game_cam.draw_sprite(sprite)
    text.draw(game_cam, position=(10, 10))
    screen.update()
