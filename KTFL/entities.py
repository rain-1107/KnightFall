import pygame
import KTFL.sprite
from KTFL.util import Vector2
import json


class OverheadPlayer:
    def __init__(self, config_file=""):
        try:
            self.data = json.load(open(config_file, "r"))
        except FileNotFoundError:
            self.data = json.load(open("KTFL/bin/entities/player.json", "r"))
        self.size = Vector2.list_to_vec(self.data["size"])
        self.position = Vector2.list_to_vec(self.data["position"])
        self.sprite = KTFL.sprite.AnimatedSprite(self.size, self.position, self.data["image_data"])
        self.speed = 300
        self.level = None

    def update(self, camera, dt=1/60):
        self.sprite.update_animation(dt)
        self.sprite.draw_to(camera.surface)
        self.move(camera.display.control, dt, camera.surface)

    def move(self, control: KTFL.control.Input, dt, surf):
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
            velocity = self.check_collision(velocity)
        self.position.set(self.position+velocity)

    def check_collision(self, vector):
        # collision detection here
        return vector

    def add_to_level(self, level):
        self.level = level