import random
import pygame
from .util import *


class ParticleHandler:
    def __init__(self, images, position=[0,0]):
        self.position = Vector2.list_to_vec(position)
        self.particles = []
        self.dead = []
        self.g_force = 500
        self.images = []
        for image in images:
            if type(image) == str:
                try:
                    self.images.append(pygame.image.load(image).convert_alpha())
                except FileNotFoundError:
                    _surf = pygame.surface.Surface((10, 10))
                    _surf.fill((0, 0, 0))
                    self.images.append(_surf)
            else:
                self.images.append(image)

    def update(self, camera, dt=1/60):
        for particle in self.dead:
            self.particles.remove(particle)
        self.dead = []
        for particle in self.particles:
            particle.update(camera, dt)

    def new_particle(self, start_pos, direction = None, speed=100, last_for=1, bottom_y=None):
        if not direction:
            direction = Vector2(random.randint(-100, 100), random.randint(-100, 100))
        direction.normalise()
        direction.set(Vector2(direction.x*speed, direction.y*speed))
        self.particles.append(Particle(self, start_pos, direction, last_for))


class Particle:
    def __init__(self, parent: ParticleHandler, position, velocity, last_for):
        self.position = Vector2.list_to_vec(position)
        self.velocity = Vector2.list_to_vec(velocity)
        self.parent = parent
        self.anim_tick = last_for/self.parent.images.__len__()
        self.last_for = last_for
        self.index = 0
        self.parent = parent

    def update(self, camera, dt: int):
        self.position.set(self.position+self.velocity*dt)
        self.anim_tick -= dt
        if self.anim_tick < 0:
            self.index += 1
            self.anim_tick = self.last_for/self.parent.images.__len__()
            if self.index == self.parent.images.__len__():
                self.parent.dead.append(self)
                return
        camera.surface.blit(self.parent.images[self.index], self.position.list)