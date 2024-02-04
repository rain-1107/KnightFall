import KTFL
import pygame
import json

screen = KTFL.display.Display(size=(1600, 900))
ui_cam = KTFL.display.Camera(size=(1600, 900))
level_cam = KTFL.display.Camera(size=(1300, 900), position=(300, 0), display_size=(1300, 900))
screen.add_camera(level_cam)
screen.add_camera(ui_cam)
screen.control.load_controls("input.json")
text_surfaces = []
buttons = {}
inputs = {}
current_level = KTFL.level.Level("levels/default.json")
current_level.load()


def create_menu():
    text_surfaces.append([KTFL.gui.get_text_surf("Load level from file"), (20, 35)])
    text_surfaces.append([KTFL.gui.get_text_surf("Save level"), (20, 95)])
    buttons["load"] = KTFL.gui.Button((75, 30), (120, 50), "bin/images/button0.png", "bin/images/button1.png",
                                      function=load_level, text="Load")
    buttons["save"] = KTFL.gui.Button((75, 30), (120, 110), "bin/images/button0.png", "bin/images/button1.png",
                                      function=save_level, text="Save")
    inputs["load"] = KTFL.gui.TextInput((75, 30), (20, 50), "bin/images/input.png", text="default")
    inputs["save"] = KTFL.gui.TextInput((75, 30), (20, 110), "bin/images/input.png", text="default")

    buttons["up"] = KTFL.gui.Button((30, 30), (130, 200), "bin/images/2button0.png", "bin/images/2button1.png", function=move_cam_up, text="up")
    buttons["left"] = KTFL.gui.Button((30, 30), (100, 230), "bin/images/2button0.png", "bin/images/2button1.png",
                                    function=move_cam_left, text="L")
    buttons["down"] = KTFL.gui.Button((30, 30), (130, 260), "bin/images/2button0.png", "bin/images/2button1.png",
                                    function=move_cam_down, text="down")
    buttons["right"] = KTFL.gui.Button((30, 30), (160, 230), "bin/images/2button0.png", "bin/images/2button1.png",
                                    function=move_cam_right, text="R")


def move_cam_left():
    level_cam.sprite_offset.x += 50


def move_cam_right():
    level_cam.sprite_offset.x -= 50


def move_cam_up():
    level_cam.sprite_offset.y += 50


def move_cam_down():
    level_cam.sprite_offset.y -= 50


def load_level():
    global current_level
    current_level = KTFL.level.Level("levels/"+inputs["load"].text+".json")
    current_level.load()


def save_level():
    global current_level
    f = open("levels/"+inputs["save"].text+".json", "w")
    json.dump(current_level.raw, f)
    current_level.file = "levels/"+inputs["save"].text+".json"
    # current_level.load()


def update_level_cam():
    level_cam.clear(current_level.meta["background"])
    pygame.draw.rect(level_cam.surface, (0, 0, 0), (
    level_cam.sprite_offset.x, level_cam.sprite_offset.y, current_level.meta["size"][0], current_level.meta["size"][1]), width=2)
    for sprite in current_level.sprites:
        level_cam.draw_to(sprite)
    for rect in current_level.physics_objects:
        pygame.draw.rect(level_cam.surface, (20, 20, 20), (rect.left+level_cam.sprite_offset.x, rect.top+level_cam.sprite_offset.y, rect.w, rect.h), width=3)


def update_menu():
    pygame.draw.rect(ui_cam.surface, (255, 255, 255), (0, 0, 300, 900))
    pygame.draw.rect(ui_cam.surface, (0, 0, 0), (0, 0, 300, 900), width=3)
    for surf in text_surfaces:
        ui_cam.draw_surf(surf[0], surf[1])
    for key in buttons:
        buttons[key].update(ui_cam)
    for key in inputs:
        inputs[key].update(ui_cam)

def create_sprite():
    pass


create_menu()

while True:
    update_level_cam()
    update_menu()
    screen.update()

