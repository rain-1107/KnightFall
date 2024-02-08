import random
import pygame
try:
    import shapely
    SHAPELY = True
except ModuleNotFoundError:
    SHAPELY = False
from .util import *


class ParticleHandler:
    def __init__(self, images, position=[0,0], level=None):
        self.position = Vector2.list_to_vec(position)
        self.particles = []
        self.dead = []
        self.g_force = 200
        self.level = level
        self.images = []
        for image in images:
            self.images.append(load_image(image, size=[1,1]))

    def update(self, camera):
        dt = camera.display.delta_time
        for particle in self.dead:
            self.particles.remove(particle)
        self.dead = []
        for particle in self.particles:
            particle.update(camera, dt)

    def new_particle(self, start_pos, direction=None, speed=100, last_for=1, gravity=False):
        if not direction:
            direction = Vector2(random.random()-0.5, random.random()-0.5)
        direction.normalise()
        direction.set(Vector2(direction.x*speed, direction.y*speed))
        self.particles.append(Particle(self, start_pos, direction, last_for, gravity))


class Particle:
    def __init__(self, parent: ParticleHandler, position, velocity, last_for, gravity):
        self.position = Vector2.list_to_vec(position)
        self.velocity = Vector2.list_to_vec(velocity)
        self.parent = parent
        self.gravity = gravity
        self.anim_tick = last_for/self.parent.images.__len__()
        self.last_for = last_for
        self.index = 0
        self.parent = parent

    def update(self, camera, dt: int):
        if self.gravity:
            self.velocity.y += self.parent.g_force * dt
        else:
            self.velocity.y = self.velocity.y * (1 / (dt + 1))

        self.velocity.x = self.velocity.x * (1/(dt+1))
        if self.parent.level and SHAPELY:
            _list = point_in_rects(self.position + self.velocity*dt, (self.parent.level.physics_rects))
            for obj in _list:
                _vec = self.position + self.velocity * dt
                line = shapely.LineString([self.position.list, _vec.list])
                top = line.intersection(shapely.LineString([obj.topright, obj.topleft]))
                bottom = line.intersection(shapely.LineString([obj.bottomright, obj.bottomleft]))
                right = line.intersection(shapely.LineString([obj.topleft, obj.bottomleft]))
                left = line.intersection(shapely.LineString([obj.topright, obj.bottomright]))
                if top or bottom:
                    if top:
                        intersection = top
                    else:
                        intersection = bottom
                    intersection = Vector2(intersection.x, intersection.y)
                    # self.velocity.set(self.velocity-intersection)
                    self.position.set(intersection)
                    if self.gravity:
                        self.velocity.y = -self.velocity.y * 0.5
                    else:
                        self.velocity.y = -self.velocity.y * 0.8
                if left or right:
                    if left:
                        intersection = left
                    else:
                        intersection = right
                    intersection = Vector2(intersection.x, intersection.y)
                    # self.velocity.set(self.velocity-intersection)
                    self.position.set(intersection)
                    self.velocity.x = -self.velocity.x * 0.8

        self.position.set(self.position+self.velocity*dt)
        self.anim_tick -= dt
        if self.anim_tick < 0:
            self.index += 1
            self.anim_tick = self.last_for/self.parent.images.__len__()
            if self.index == self.parent.images.__len__():
                self.parent.dead.append(self)
                return
        camera.surface.blit(self.parent.images[self.index], self.position.list)