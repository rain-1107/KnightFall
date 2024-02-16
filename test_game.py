import socket
import math
import KTFL
import pygame
import sys
import random

screen = KTFL.display.Display(fps=60, size=(800, 450), fullscreen=True)
game_cam = KTFL.display.Camera((256, 144))
screen.add_camera(game_cam)
ui_cam = KTFL.display.Camera(size=(800, 400))
screen.add_camera(ui_cam)
level = KTFL.load.Level("level editor/levels/test.json")
level.load()
player = KTFL.entities.SidePlayer("bin/entity data/player/player.json")
player.add_to_level(level)
square = KTFL.sprite.Sprite([24, 35], (112, 118.5), centered=True, colour=(0, 0, 0))
particles = KTFL.particle.ParticleHandler(["images/particles/dot.png"], level=level)


while True:
    game_cam.clear((200, 200, 200))
    ui_cam.clear()
    level.draw(game_cam)
    particles.update(game_cam)
    player.update(game_cam)
    game_cam.world_pos.x = round(player.position.x - game_cam.size.x/2)
    if screen.control.mouse_button(1):
        particles.new_particle(screen.control.mouse_pos(game_cam), speed=50, last_for=3, gravity=True)
    ui_cam.draw_surf(KTFL.gui.get_text_surf(str(round(screen.clock.get_fps()))), (0, 0))
    screen.update()
