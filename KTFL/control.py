import pygame
import json


class Input:
    def __init__(self, keyboard_config=None, allow_controller=False):
        # self.actions = {"invalid": "N/A"}
        if keyboard_config:
            self.keyboard = json.load(open(keyboard_config, "r"))
        else:
            self.keyboard = json.load(open("KTFL/bin/default/keyboard_controls.json", "r"))
        # self.controller = {}
        self.log = {"input_type": "keyboard", "actions": {}}

    # pygame.key.key_code(name)
    def update(self):
        if self.log["input_type"] == "keyboard":
            self.u_keyboard()

    def u_keyboard(self):
        for action in self.log["actions"]:
            if self.log["actions"][action] == "down":
                self.log["actions"][action] = "held"
        for event in pygame.event.get(eventtype=[pygame.KEYUP, pygame.KEYDOWN]):
            if event.type == pygame.KEYDOWN:
                self.log["actions"][self.get_action(event.unicode)] = "held"
            elif event.type == pygame.KEYUP:
                try:
                    self.log["actions"].pop(self.get_action(event.unicode))
                except KeyError:
                    pass # print to log file

    def get_action(self, key):
        try:
            return self.keyboard[key]
        except KeyError:
            return self.keyboard["invalid"]

    def is_action(self, action):
        try:
            return self.log["actions"][action] == "held" or self.log["actions"][action] == "held"
        except KeyError:
            return False

    def load_controls(self, fp, type="keyboard"):
        if type == "keyboard":
            self.keyboard = json.load(open(fp, "r"))
