import pygame
import sys
import KTFL.control
import KTFL.sprite
from .util import *


class Display:
    def __init__(self, size=(500, 500), fullscreen=False, fps=60):
        if fullscreen:
            self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.size = KTFL.util.Vector2.list_to_vec(self.surface.get_size())
        else:
            self.surface = pygame.display.set_mode(size)
            self.size = KTFL.util.Vector2.list_to_vec(size)
        self.cameras = []
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.control = KTFL.control.Input()
        self.delta_time = 0.0000001

    def update(self):  # TODO: add drawing code here for all sprites for optimisation (OpenGL); use batching etc.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        for camera in self.cameras:
            camera.update()
        pygame.display.flip()
        self.clock.tick(self.fps)
        self.delta_time = 1 / (self.clock.get_fps()+1)
        self.control.update()

    def add_camera(self, camera):
        camera.display = self
        self.cameras.append(camera)

    def add_cameras(self, cameras):
        for camera in cameras:
            self.add_camera(camera)


class Camera:
    def __init__(self, size, display_size=0, position=(0, 0)):  # TODO: add relevant variables for drawing in OpenGL
        self.size = Vector2.list_to_vec(size)
        self.display = None
        self.display_size = display_size
        self.position = Vector2.list_to_vec(position)
        self.surface = pygame.surface.Surface(size, pygame.SRCALPHA)
        self.surface.set_clip((0, 0, self.size.x, self.size.y))
        self.draw_offset = Vector2(0, 0)
        self.world_pos = Vector2(0, 0)

    def update(self):
        surf = self.surface
        if self.display_size:
            self.display.surface.blit(pygame.transform.scale(surf, self.display_size), self.position.list)
            return
        self.display.surface.blit(pygame.transform.scale(surf, self.display.size.list), self.position.list)

    def lock_to(self, sprite):
        self.lock_x_to(sprite)
        self.lock_y_to(sprite)

    def lock_x_to(self, sprite):
        self.world_pos.x = round(sprite.top_left.x) + sprite.size.x / 2 - self.size.x / 2

    def lock_y_to(self, sprite):
        self.world_pos.y = round(sprite.top_left.y - sprite.size.y / 2 - self.size.y / 2)

    def draw_sprite(self, sprite: KTFL.sprite.Sprite):
        new_pos = sprite.top_left + self.draw_offset - self.world_pos
        self.surface.blit(sprite.image, new_pos.list)

    def draw_surf(self, surf, position, parallax=Vector2(1, 1)):
        position = Vector2.list_to_vec(position) + self.draw_offset - (self.world_pos*parallax)
        self.surface.blit(surf, position.list)

    def delete(self):
        self.display.cameras.remove(self)
        del self

    def clear(self, colour=None):
        if colour:
            self.surface.fill(colour)
            return
        self.surface.fill((0, 0, 0, 0))

    def set_size(self, new):
        self.size = new
        self.surface = pygame.surface.Surface(self.size.list, pygame.SRCALPHA)