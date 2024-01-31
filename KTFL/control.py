import pygame
import json


class Input:
    def __init__(self, keyboard_config=None, allow_controller=False):
        # self.actions = {"invalid": "N/A"}
        try:
            self.keyboard = json.load(open(keyboard_config, "r"))
        except FileNotFoundError:
            self.keyboard = json.load(open("KTFL/bin/default/keyboard_controls.json", "r"))
        except TypeError:
            self.keyboard = json.load(open("KTFL/bin/default/keyboard_controls.json", "r"))
        # self.controller = {}
        self.log = {"input_type": "keyboard", "actions": {}, "mouse": {}}
        self.mouse_pressed = pygame.mouse.get_pressed(5)
        self.prev_mouse = self.mouse_pressed

    def load_controls(self, config, type="keyboard"):
        try:
            self.keyboard = json.load(open(config, "r"))
            self.log["actions"] = {}
        except FileNotFoundError:
            print(f"Error: {config} not found")

    def update(self):
        if self.log["input_type"] == "keyboard":
            self.u_keyboard()

    def u_keyboard(self):
        self.mouse_pressed = pygame.mouse.get_pressed(5)
        keys_pressed = pygame.key.get_pressed()
        for key in self.keyboard:
            if keys_pressed[pygame.key.key_code(key)]:
                self.log["actions"][self.get_action(key)] = "held"
            else:
                try:
                    self.log["actions"].pop(self.get_action(key))
                except KeyError:
                    pass
        for event in pygame.event.get(eventtype=[pygame.KEYUP, pygame.KEYDOWN]):
            if event.type == pygame.KEYDOWN:
                self.log["actions"][self.get_action(pygame.key.name(event.key))] = "down"
        new_mouse = []
        for i, button in enumerate(self.mouse_pressed):
            if button:
                if self.prev_mouse[i]:
                    new_mouse.append("held")
                else:
                    new_mouse.append("down")
            else:
                new_mouse.append(False)
        self.log["mouse"] = {"position": pygame.mouse.get_pos(), "buttons": new_mouse}
        self.prev_mouse = self.mouse_pressed

    def get_action(self, key):
        try:
            return self.keyboard[key]
        except KeyError:
            return self.keyboard["invalid"]

    def is_action(self, action):
        try:
            return self.log["actions"][action] == "down" or self.log["actions"][action] == "held"
        except KeyError:
            return False

    def on_action(self, action):
        try:
            return self.log["actions"][action] == "down"
        except KeyError:
            return False

    def mouse_pos(self):
        return self.log["mouse"]["position"]

    def mouse_button(self, n):
        return self.log["mouse"]["buttons"][n-1]