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

    buttons["up"] = KTFL.gui.Button((30, 30), (100, 170), "bin/images/2button0.png", "bin/images/2button1.png", function=move_cam_up, text="up")
    buttons["left"] = KTFL.gui.Button((30, 30), (70, 200), "bin/images/2button0.png", "bin/images/2button1.png",
                                    function=move_cam_left, text="L")
    buttons["down"] = KTFL.gui.Button((30, 30), (100, 230), "bin/images/2button0.png", "bin/images/2button1.png",
                                    function=move_cam_down, text="down")
    buttons["right"] = KTFL.gui.Button((30, 30), (130, 200), "bin/images/2button0.png", "bin/images/2button1.png",
                                    function=move_cam_right, text="R")

    inputs["file"] = KTFL.gui.TextInput((150, 30), (100, 300), "bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("File"), (20, 305)])

    inputs["position"] = KTFL.gui.TextInput((75, 30), (100, 350), "bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Position"), (20, 355)])

    inputs["size"] = KTFL.gui.TextInput((75, 30), (100, 400), "bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Size"), (20, 405)])

    inputs["id"] = KTFL.gui.TextInput((75, 30), (100, 450), "bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("ID"), (20, 455)])

    buttons["create"] = KTFL.gui.Button((75, 30), (200, 350), "bin/images/button0.png", "bin/images/button1.png",
                                      function=create_sprite, text="Create")
    buttons["edit"] = KTFL.gui.Button((75, 30), (200, 400), "bin/images/button0.png", "bin/images/button1.png",
                                        function=edit_sprite, text="Edit")
    buttons["delete"] = KTFL.gui.Button((75, 30), (200, 450), "bin/images/button0.png", "bin/images/button1.png",
                                        function=delete_sprite, text="Delete")


def move_cam_left():
    level_cam.sprite_offset.x += 50
    update_level_cam()


def move_cam_right():
    level_cam.sprite_offset.x -= 50
    update_level_cam()


def move_cam_up():
    level_cam.sprite_offset.y += 50
    update_level_cam()


def move_cam_down():
    level_cam.sprite_offset.y -= 50
    update_level_cam()


def load_level():
    global current_level
    current_level = KTFL.level.Level("levels/"+inputs["load"].text+".json")
    current_level.load()
    update_level_cam()


def save_level():
    global current_level
    f = open("levels/"+inputs["save"].text+".json", "w")
    current_level.update_raw()
    json.dump(current_level.raw, f, indent=2)
    current_level.file = "levels/"+inputs["save"].text+".json"
    # current_level.load()
    update_level_cam()


def update_level_cam():
    level_cam.clear(current_level.meta["background"])
    pygame.draw.rect(level_cam.surface, (0, 0, 0), (
    level_cam.sprite_offset.x, level_cam.sprite_offset.y, current_level.meta["size"][0], current_level.meta["size"][1]), width=2)
    for sprite in current_level.sprites:
        level_cam.draw_to(sprite)
        level_cam.draw_surf(KTFL.gui.get_text_surf(text=str(sprite.id)), position=sprite.top_left.list)
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
    print("new sprite")
    file = inputs["file"].text
    position = inputs["position"].text.split(",")
    position = [float(position[0]), float(position[1])]
    size = inputs["size"].text.split(",")
    size = [float(size[0]), float(size[1])]
    id = int(inputs["id"].text)
    current_level.add_sprite(KTFL.sprite.Sprite(size, position, file, id=id))
    update_level_cam()


def delete_sprite():
    try:
        id = int(inputs["id"].text)
        current_level.delete_sprite(id)
        update_level_cam()
    except:
        print("error deleting sprite")


def edit_sprite():
    try:
        id = int(inputs["id"].text)
        sprite = current_level.get_sprite(id)
        if inputs["position"].text:
            position = inputs["position"].text.split(",")
            position = [float(position[0]), float(position[1])]
            sprite.set_position(position)
        if inputs["size"].text:
            size = inputs["size"].text.split(",")
            size = [float(size[0]), float(size[1])]
            sprite.set_size(size)
        if inputs["file"].text:
            sprite.set_image(inputs["file"].text)
        update_level_cam()
    except:
        print("error editing sprite")

create_menu()
update_level_cam()

while True:
    update_menu()
    screen.update()

