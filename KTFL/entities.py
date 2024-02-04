import pygame
import KTFL.sprite
from KTFL.util import Vector2
import json


def collision_list(obj, obj_list):
    hit_list = []
    for rect in obj_list:
        if obj.colliderect(rect):
            hit_list.append(rect)
    return hit_list


class OverheadPlayer:
    def __init__(self, config_file=""):
        try:
            self.data = json.load(open(config_file, "r"))
        except FileNotFoundError:
            self.data = json.load(open("KTFL/bin/entities/player.json", "r"))
        self.size = Vector2.list_to_vec(self.data["size"])
        self.position = Vector2.list_to_vec(self.data["position"])
        self.rect = pygame.rect.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
        self.sprite = KTFL.sprite.AnimatedSprite(self.size, self.position, self.data["image_data"])
        self.speed = 300
        self.level = None

    def update(self, camera, dt=1/60):
        self.sprite.update_animation(dt)
        self.sprite.draw_to(camera.surface)
        self.move(camera.display.control, dt)

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
            self.position.set(self.check_collision(velocity))
            return
        self.position.set(self.position+velocity)
        self.rect.update(self.position.x, self.position.y, self.size.x, self.size.y)

    def check_collision(self, vector):
        self.rect.update(self.rect.left+vector.x, self.rect.top, self.rect.width, self.rect.height)
        hit_list = collision_list(self.rect, self.level.physics_objects)
        for rect in hit_list:
            if vector.x > 0:
                self.rect.right = rect.left
            if vector.x < 0:
                self.rect.left = rect.right
        self.rect.update(self.rect.left, self.rect.top+vector.y, self.rect.width, self.rect.height)
        hit_list = collision_list(self.rect, self.level.physics_objects)
        for rect in hit_list:
            if vector.y > 0:
                self.rect.bottom = rect.top
            if vector.y < 0:
                self.rect.top = rect.bottom
        new_pos = Vector2(self.rect.x, self.rect.y)
        return new_pos

    def add_to_level(self, level):
        self.level = level