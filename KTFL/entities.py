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
        position = Vector2.list_to_vec(self.data["position"])
        self.rect = pygame.rect.Rect(position.x, position.y, self.size.x, self.size.y)
        self.sprite = KTFL.sprite.AnimatedSprite(self.size, position, self.data["image_data"], centered=True)
        self.speed = 300
        self.level = None

    def update(self, camera, dt=1/60):
        self.move(camera.display.control, dt)
        self.sprite.centre = self.centre
        self.sprite.update_animation(dt)
        camera.draw_to(self.sprite)

    def move(self, control: KTFL.control.Input, dt):
        velocity = Vector2(0, 0)
        if not control.is_action("left") or not control.is_action("right"):
            if control.is_action("left"):
                velocity.x = -self.speed * dt
            if control.is_action("right"):
                velocity.x = self.speed * dt
        if not control.is_action("up") or not control.is_action("down"):
            if control.is_action("up"):
                velocity.y = -self.speed * dt
            if control.is_action("down"):
                velocity.y = self.speed * dt
        if self.level:
            new_pos = self.check_collision(velocity)
            self.rect.update(new_pos.x, new_pos.y, self.size.x, self.size.y)
            return
        self.rect.update(self.rect.x+velocity.x, self.rect.y+velocity.y, self.size.x, self.size.y)

    def check_collision(self, vector):
        self.rect.update(self.rect.left+vector.x, self.rect.top, self.rect.width, self.rect.height)
        hit_list = rect_collision_list(self.rect, self.level.physics_rects)
        for rect in hit_list:
            if vector.x > 0:
                self.rect.right = rect.left
            if vector.x < 0:
                self.rect.left = rect.right
        self.rect.update(self.rect.left, self.rect.top+vector.y, self.rect.width, self.rect.height)
        hit_list = rect_collision_list(self.rect, self.level.physics_rects)
        for rect in hit_list:
            if vector.y > 0:
                self.rect.bottom = rect.top
            if vector.y < 0:
                self.rect.top = rect.bottom
        new_pos = Vector2(self.rect.x, self.rect.y)
        return new_pos

    def add_to_level(self, level):
        self.level = level

    @property
    def centre(self):
        return Vector2(self.rect.x + self.size.x/2, self.rect.y + self.size.y/2)