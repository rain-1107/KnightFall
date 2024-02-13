import pygame
import KTFL.sprite
from .util import *
import json


class OverheadPlayer:
    def __init__(self, config_file=""):
        try:
            self.data = json.load(open(config_file, "r"))
        except FileNotFoundError:
            self.data = json.load(open("KTFL/bin/entities/player.json", "r"))
        self.size = Vector2.list_to_vec(self.data["size"])
        self.position = Vector2.list_to_vec(self.data["position"])
        self.rect = pygame.rect.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
        self.sprite = KTFL.sprite.AnimatedSprite(self.size, self.position, self.data["image_data"], centered=True)
        self.speed = 100
        self.level = None

    def update(self, camera):
        dt = camera.display.delta_time
        self.move(camera.display.control, dt)
        self.sprite.centre = self.centre
        self.sprite.update_animation(dt)
        camera.draw_sprite(self.sprite)

    def move(self, control: KTFL.control.Input, dt):
        velocity = Vector2(0, 0)
        if not control.is_action("left") or not control.is_action("right"):
            if control.is_action("left"):
                velocity.x = -(self.speed * dt)
            if control.is_action("right"):
                velocity.x = self.speed * dt
        if not control.is_action("up") or not control.is_action("down"):
            if control.is_action("up"):
                velocity.y = -(self.speed * dt)
            if control.is_action("down"):
                velocity.y = self.speed * dt
        if self.level:
            self.check_collision(velocity)
            self.rect.update(self.position.x, self.position.y, self.size.x, self.size.y)
            return
        self.rect.update(self.position.x+velocity.x, self.position.y+velocity.y, self.size.x, self.size.y)

    def check_collision(self, vector):
        self.position.x += vector.x
        self.rect.update(self.position.x, self.position.y, self.rect.width, self.rect.height)
        hit_list = rect_collision_list(self.rect, self.level.physics_rects)
        for rect in hit_list:
            if vector.x > 0:
                self.position.x = rect.x - self.size.x
            if vector.x < 0:
                self.position.x = rect.x + rect.w
        self.position.y += vector.y
        self.rect.update(self.position.x, self.position.y, self.rect.width, self.rect.height)
        hit_list = rect_collision_list(self.rect, self.level.physics_rects)
        for rect in hit_list:
            if vector.y > 0:
                self.position.y = rect.y - self.size.y
            if vector.y < 0:
                self.position.y = rect.y + rect.h

    def add_to_level(self, level):
        self.level = level

    @property
    def centre(self):
        return Vector2(self.rect.x + self.size.x/2, self.rect.y + self.size.y/2)


class SidePlayer:
    def __init__(self, config_file=""):
        try:
            self.data = json.load(open(config_file, "r"))
        except FileNotFoundError:
            self.data = json.load(open("KTFL/bin/entities/player.json", "r"))
        self.size = Vector2.list_to_vec(self.data["size"])
        self.position = Vector2.list_to_vec(self.data["position"])
        self.rect = pygame.rect.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
        self.sprite = KTFL.sprite.AnimatedSprite(self.size, self.position, self.data["image_data"], centered=True)
        self.velocity = Vector2(0, 0)
        self.speed = 100
        self.gravity = 300
        self.jump_f = 100
        self.on_ground = False
        self.level = None

    def update(self, camera):
        dt = camera.display.delta_time
        self.move(camera.display.control, dt)
        self.sprite.centre = self.centre
        self.sprite.update_animation(dt)
        camera.draw_sprite(self.sprite)

    def move(self, control: KTFL.control.Input, dt):
        self.velocity.x = 0
        if dt > 0.1:  # NOTE: without this player will likely phase through floor, look for other solutions
            dt = 0.1
        if not self.on_ground:
            self.velocity.y += self.gravity * dt
        if not control.is_action("left") or not control.is_action("right"):
            if control.is_action("left"):
                self.velocity.x = -self.speed
            if control.is_action("right"):
                self.velocity.x = self.speed
        if control.is_action("up"):
            print(self.on_ground)
            if self.on_ground:
                self.velocity.y = -self.jump_f
        if self.level:
            self.on_ground = False
            self.check_collision(self.velocity*dt)
            self.rect.update(self.position.x, self.position.y, self.size.x, self.size.y)
            return
        self.rect.update(self.position.x + self.velocity.x*dt, self.position.y + self.velocity.y*dt, self.size.x, self.size.y)

    def check_collision(self, vector):
        self.position.x += vector.x
        self.rect.update(self.position.x, self.position.y, self.rect.width, self.rect.height)
        hit_list = rect_collision_list(self.rect, self.level.physics_rects)
        for rect in hit_list:
            if vector.x > 0:
                self.position.x = rect.x - self.size.x
            if vector.x < 0:
                self.position.x = rect.x + rect.w
        self.position.y += vector.y
        self.rect.update(self.position.x, self.position.y, self.rect.width, self.rect.height)
        hit_list = rect_collision_list(self.rect, self.level.physics_rects)
        for rect in hit_list:
            if vector.y > 0:
                self.position.y = rect.y - self.size.y
                self.on_ground = True
            if vector.y < 0:
                self.position.y = rect.y + rect.h

    def add_to_level(self, level):
        self.level = level

    @property
    def centre(self):
        return Vector2(self.rect.x + self.size.x / 2, self.rect.y + self.size.y / 2)