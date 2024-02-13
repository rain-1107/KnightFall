import pygame
import json
import math

class Input:
    def __init__(self, keyboard_config="", allow_controller=False):
        self.log = {"input_type": "keyboard", "actions": {}, "mouse": {}, "keys": {}}
        try:
            self.keyboard = json.load(open(keyboard_config, "r"))
        except FileNotFoundError:
            try:
                self.keyboard = json.load(open("KTFL/bin/default/keyboard_controls.json", "r"))
            except FileNotFoundError:
                self.keyboard = None
                self.log["input_type"] = None
        except TypeError:
            try:
                self.keyboard = json.load(open("KTFL/bin/default/keyboard_controls.json", "r"))
            except FileNotFoundError:
                self.keyboard = None
                self.log["input_type"] = None
        self.mouse_pressed = pygame.mouse.get_pressed(5)
        self.prev_mouse = self.mouse_pressed
        new_mouse = []  # consistent implementation of self.log["mouse"] ..... (revert if u want but pycharm wouldn't shut up) (omg it's still complaining pls help)
        for i, button in enumerate(self.mouse_pressed):
            if button:
                if self.prev_mouse[i]:
                    new_mouse.append("held")
                else:
                    new_mouse.append("down")
            else:
                new_mouse.append(False)
        self.log["mouse"] = {"position": pygame.mouse.get_pos(), "buttons": new_mouse,
                             "scroll": 0, "scroll_delta": 0}

    def load_controls(self, config, type="keyboard"):
        try:
            self.keyboard = json.load(open(config, "r"))
            self.log["input_type"] = "keyboard"
            self.log["actions"] = {}
        except FileNotFoundError:
            print(f"Error: {config} not found")

    def update(self):
        if self.log["input_type"] == "keyboard":
            self.u_keyboard()

    def u_keyboard(self):
        self.log["keys"] = {}
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
        for event in pygame.event.get(eventtype=pygame.KEYDOWN):
            if event.type == pygame.KEYDOWN:
                self.log["actions"][self.get_action(pygame.key.name(event.key))] = "down"
                self.log["keys"][event.key] = ["down", event.mod]
        new_mouse = []
        for i, button in enumerate(self.mouse_pressed):
            if button:
                if self.prev_mouse[i]:
                    new_mouse.append("held")
                else:
                    new_mouse.append("down")
            else:
                new_mouse.append(False)
        old_scroll = self.log["mouse"]["scroll"]
        new_scroll = self.log["mouse"]["scroll"]
        for event in pygame.event.get(eventtype=[pygame.MOUSEWHEEL]):
            new_scroll = new_scroll+event.y
        if new_scroll > 100:
            new_scroll = 100
        elif new_scroll < -100:
            new_scroll = -100
        self.log["mouse"] = {"position": pygame.mouse.get_pos(), "buttons": new_mouse, "scroll": new_scroll,
                             "scroll_delta": old_scroll-new_scroll}
        self.prev_mouse = self.mouse_pressed

    def get_action(self, key):
        try:
            return self.keyboard[key]
        except KeyError:
            return None

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

    def mouse_pos(self, camera=None):
        if camera:
            screen_size = camera.display.surface.get_size()
            if camera.display_size:
                xcoeff = camera.size.x / camera.display_size[0]
                ycoeff = camera.size.y / camera.display_size[1]
            else:
                xcoeff = camera.size.x / screen_size[0]
                ycoeff = camera.size.y / screen_size[1]
            return [math.trunc(((self.log["mouse"]["position"][0]-camera.position.x)*xcoeff) - camera.draw_offset.x + camera.world_pos.x),
                    math.trunc(((self.log["mouse"]["position"][1]-camera.position.y)*ycoeff) - camera.draw_offset.y + camera.world_pos.y)]
        else:
            return self.log["mouse"]["position"]

    def mouse_button(self, n):
        try:
            return self.log["mouse"]["buttons"][n-1]
        except KeyError:
            return False

    def mouse_scroll(self):
        return self.log["mouse"]["scroll"], self.log["mouse"]["scroll_delta"]