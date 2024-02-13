import KTFL
import pygame
import json
import random

from KTFL.util import Vector2
from KTFL.gui import draw_grid

screen = KTFL.display.Display(size=(1600, 900))
menu_cam = KTFL.display.Camera(size=(1600, 900))
level_cam = KTFL.display.Camera(size=(1300, 900), position=(300, 0), display_size=(1300, 900))
screen.add_camera(level_cam)
screen.add_camera(menu_cam)
screen.control.load_controls("level editor/input.json")
text_surfaces = []
buttons = {}
inputs = {}
current_level = KTFL.load.Level("level editor/levels/default.json")
current_level.load()
current_layer_index = 0


zoom = 1
zoominfo = KTFL.gui.get_text_surf(f"Zoom amount : {zoom}")
original_size = Vector2(1300, 900)

selected_sprite = None
selected_sprite_offset = None

menu_max_scroll = 500


def create_menu():
    global selected_sprite_text_surface_index # this is so fucking dumb

    # ui for loading and saving level + moving level camera
    file_top = 35
    text_surfaces.append([KTFL.gui.get_text_surf("Load level from file"), (20, 35)])
    text_surfaces.append([KTFL.gui.get_text_surf("Save level"), (20, 95)])
    buttons["load"] = KTFL.gui.Button((75, 30), (120, 50), "level editor/bin/images/button0.png", "level editor/bin/images/button1.png",
                                      function=load_level, text="Load")
    buttons["save"] = KTFL.gui.Button((75, 30), (120, 110), "level editor/bin/images/button0.png", "level editor/bin/images/button1.png",
                                      function=save_level, text="Save")
    inputs["load"] = KTFL.gui.TextInput((75, 30), (20, 50), "level editor/bin/images/input.png", text="default")
    inputs["save"] = KTFL.gui.TextInput((75, 30), (20, 110), "level editor/bin/images/input.png", text="")

    buttons["up"] = KTFL.gui.Button((30, 30), (50, 170), "level editor/bin/images/2button0.png", "level editor/bin/images/2button1.png",
                                    function=move_cam_up, text="U")
    buttons["left"] = KTFL.gui.Button((30, 30), (20, 200), "level editor/bin/images/2button0.png", "level editor/bin/images/2button1.png",
                                    function=move_cam_left, text="L")
    buttons["down"] = KTFL.gui.Button((30, 30), (50, 230), "level editor/bin/images/2button0.png", "level editor/bin/images/2button1.png",
                                    function=move_cam_down, text="D")
    buttons["right"] = KTFL.gui.Button((30, 30), (80, 200), "level editor/bin/images/2button0.png", "level editor/bin/images/2button1.png",
                                    function=move_cam_right, text="R")

    buttons["zoom_in"] = KTFL.gui.Button((75, 30), (150, 180), "level editor/bin/images/button0.png",
                                      "level editor/bin/images/button1.png",
                                      function=zoom_in, text="Zoom in")
    buttons["zoom_out"] = KTFL.gui.Button((75, 30), (150, 220), "level editor/bin/images/button0.png",
                                      "level editor/bin/images/button1.png",
                                      function=zoom_out, text="Zoom out")

    # ui for grid drawing
    grid_top = 280
    inputs["gridsnapx"] = KTFL.gui.TextInput((75, 30), (100, grid_top), "level editor/bin/images/input.png", text="")
    inputs["gridsnapy"] = KTFL.gui.TextInput((75, 30), (180, grid_top), "level editor/bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Grid"), (20, grid_top+5)])

    buttons["grid"] = KTFL.gui.Switch((30, 30), (260, grid_top), "level editor/bin/images/off.png", "level editor/bin/images/on.png")

    # ui for creating sprites
    sprite_top = 340
    text_surfaces.append([KTFL.gui.get_text_surf("Sprite"), (20, sprite_top-5)])

    buttons["spriteID"] = KTFL.gui.Switch((30, 30), (260, sprite_top + 140), "level editor/bin/images/off.png",
                                      "level editor/bin/images/on.png")
    buttons["spriteTag"] = KTFL.gui.Switch((30, 30), (260, sprite_top + 180), "level editor/bin/images/off.png",
                                          "level editor/bin/images/on.png")

    inputs["file"] = KTFL.gui.TextInput((150, 30), (100, sprite_top+20), "level editor/bin/images/input1.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("File"), (20, sprite_top+25)])

    inputs["positionx"] = KTFL.gui.TextInput((75, 30), (100, sprite_top+60), "level editor/bin/images/input.png", text="")
    inputs["positiony"] = KTFL.gui.TextInput((75, 30), (180, sprite_top+60), "level editor/bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Position"), (20, sprite_top+65)])

    inputs["sizex"] = KTFL.gui.TextInput((75, 30), (100, sprite_top+100), "level editor/bin/images/input.png", text="")
    inputs["sizey"] = KTFL.gui.TextInput((75, 30), (180, sprite_top+100), "level editor/bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Size"), (20, sprite_top+105)])

    inputs["id"] = KTFL.gui.TextInput((75, 30), (100, sprite_top+140), "level editor/bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("ID"), (20, sprite_top+145)])

    inputs["tag"] = KTFL.gui.TextInput((150, 30), (100, sprite_top+180), "level editor/bin/images/input1.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Tag"), (20, sprite_top+185)])

    buttons["create"] = KTFL.gui.Button((75, 30), (20, sprite_top+220), "level editor/bin/images/button0.png", "level editor/bin/images/button1.png",
                                      function=create_sprite, text="Create")
    buttons["edit"] = KTFL.gui.Button((75, 30), (100, sprite_top+220), "level editor/bin/images/button0.png", "level editor/bin/images/button1.png",
                                        function=edit_sprite, text="Edit")
    buttons["delete"] = KTFL.gui.Button((75, 30), (180, sprite_top+220), "level editor/bin/images/button0.png", "level editor/bin/images/button1.png",
                                        function=delete_sprite, text="Delete")

    object_top = 630
    text_surfaces.append([KTFL.gui.get_text_surf("Object"), (20, object_top)])
    inputs["objpositionx"] = KTFL.gui.TextInput((75, 30), (100, object_top + 30), "level editor/bin/images/input.png",
                                             text="")
    inputs["objpositiony"] = KTFL.gui.TextInput((75, 30), (180, object_top + 30), "level editor/bin/images/input.png",
                                             text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Position"), (20, object_top + 35)])

    inputs["objsizex"] = KTFL.gui.TextInput((75, 30), (100, object_top + 70), "level editor/bin/images/input.png",
                                         text="")
    inputs["objsizey"] = KTFL.gui.TextInput((75, 30), (180, object_top + 70), "level editor/bin/images/input.png",
                                         text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Size"), (20, object_top + 75)])

    inputs["objid"] = KTFL.gui.TextInput((75, 30), (100, object_top + 110), "level editor/bin/images/input.png", text="")
    text_surfaces.append([KTFL.gui.get_text_surf("ID"), (20, object_top + 115)])

    inputs["objtag"] = KTFL.gui.TextInput((150, 30), (100, object_top + 150), "level editor/bin/images/input1.png",
                                       text="")
    text_surfaces.append([KTFL.gui.get_text_surf("Tag"), (20, object_top + 155)])
    buttons["objShowTag"] = KTFL.gui.Switch((30, 30), (260, object_top + 150), "level editor/bin/images/off.png",
                                           "level editor/bin/images/on.png")

    buttons["objcreate"] = KTFL.gui.Button((75, 30), (20, object_top + 190), "level editor/bin/images/button0.png",
                                        "level editor/bin/images/button1.png",
                                        function=create_object, text="Create")
    buttons["objedit"] = KTFL.gui.Button((75, 30), (100, object_top + 190), "level editor/bin/images/button0.png",
                                      "level editor/bin/images/button1.png",
                                      function=edit_object, text="Edit")
    buttons["objdelete"] = KTFL.gui.Button((75, 30), (180, object_top + 190), "level editor/bin/images/button0.png",
                                        "level editor/bin/images/button1.png",
                                        function=delete_object, text="Delete")

    # layer meta data
    layer_meta_top = 870
    text_surfaces.append([KTFL.gui.get_text_surf("Layer meta"), (20, layer_meta_top)])

    text_surfaces.append([KTFL.gui.get_text_surf("Size"), (20, layer_meta_top + 30)])
    inputs["layersizex"] = KTFL.gui.TextInput((75, 30), (100, layer_meta_top + 25), "level editor/bin/images/input.png",
                                          text="")
    inputs["layersizey"] = KTFL.gui.TextInput((75, 30), (180, layer_meta_top + 25), "level editor/bin/images/input.png",
                                          text="")

    text_surfaces.append([KTFL.gui.get_text_surf("Position"), (20, layer_meta_top + 70)])
    inputs["layerposx"] = KTFL.gui.TextInput((75, 30), (100, layer_meta_top+ 65), "level editor/bin/images/input.png",
                                              text="")
    inputs["layerposy"] = KTFL.gui.TextInput((75, 30), (180, layer_meta_top + 65), "level editor/bin/images/input.png",
                                              text="")

    text_surfaces.append([KTFL.gui.get_text_surf("Parallax"), (20, layer_meta_top + 110)])
    inputs["parallax_x"] = KTFL.gui.TextInput((75, 30), (100, layer_meta_top + 105), "level editor/bin/images/input.png",
                                              text="")
    inputs["parallax_y"] = KTFL.gui.TextInput((75, 30), (180, layer_meta_top + 105), "level editor/bin/images/input.png",
                                              text="")

    text_surfaces.append([KTFL.gui.get_text_surf("Draw index"), (18, layer_meta_top + 150)])
    inputs["layerindex"] = KTFL.gui.TextInput((75, 30), (100, layer_meta_top + 145), "level editor/bin/images/input.png",
                                             text="")

    buttons["newlayer"] = KTFL.gui.Button((75, 30), (20, layer_meta_top + 180), "level editor/bin/images/button0.png",
                                           "level editor/bin/images/button1.png", function=new_layer, text="New")
    buttons["layermeta"] = KTFL.gui.Button((75, 30), (100, layer_meta_top + 180), "level editor/bin/images/button0.png",
                                      "level editor/bin/images/button1.png", function=update_level_meta, text="Set")
    buttons["deletelayer"] = KTFL.gui.Button((75, 30), (180, layer_meta_top + 180), "level editor/bin/images/button0.png",
                                          "level editor/bin/images/button1.png", function=delete_layer, text="Delete")

    text_surfaces.append([KTFL.gui.get_text_surf("Select layer"), (110, layer_meta_top + 230)])
    buttons["prev_layer"] = KTFL.gui.Button((75, 30), (70, layer_meta_top + 250), "level editor/bin/images/button0.png",
                                      "level editor/bin/images/button1.png", function=prev_layer, text="<")
    buttons["next_layer"] = KTFL.gui.Button((75, 30), (155, layer_meta_top + 250), "level editor/bin/images/button0.png",
                                            "level editor/bin/images/button1.png", function=next_layer, text=">")
    prev_layer()

    # level meta data
    meta_top = 1170
    text_surfaces.append([KTFL.gui.get_text_surf("Level meta"), (20, meta_top)])

    text_surfaces.append([KTFL.gui.get_text_surf("Name"), (20, meta_top+30)])
    inputs["name"] = KTFL.gui.TextInput((150, 30), (102, meta_top+25), "level editor/bin/images/input1.png", text=current_level.meta["name"])

    text_surfaces.append([KTFL.gui.get_text_surf("Size"), (20, meta_top+70)])
    inputs["levelx"] = KTFL.gui.TextInput((75, 30), (100, meta_top+65), "level editor/bin/images/input.png", text=str(current_level.meta["size"][0]))
    inputs["levely"] = KTFL.gui.TextInput((75, 30), (180, meta_top+65), "level editor/bin/images/input.png",
                                        text=str(current_level.meta["size"][1]))
    text_surfaces.append([KTFL.gui.get_text_surf("Background "), (20, meta_top+105)])
    inputs["backgroundr"] = KTFL.gui.TextInput((75, 30), (20, meta_top+125), "level editor/bin/images/input.png", text="200")
    inputs["backgroundg"] = KTFL.gui.TextInput((75, 30), (100, meta_top+125), "level editor/bin/images/input.png", text="200")
    inputs["backgroundb"] = KTFL.gui.TextInput((75, 30), (180, meta_top+125), "level editor/bin/images/input.png", text="200")

    buttons["meta"] = KTFL.gui.Button((75, 30), (180, meta_top+170), "level editor/bin/images/button0.png",
                                      "level editor/bin/images/button1.png", function=update_meta, text="Set")


def move_cam_left():
    level_cam.draw_offset.x += 50


def move_cam_right():
    level_cam.draw_offset.x -= 50


def move_cam_up():
    level_cam.draw_offset.y += 50


def move_cam_down():
    level_cam.draw_offset.y -= 50


def load_level():
    global current_level
    current_level = KTFL.load.Level("level editor/levels/"+inputs["load"].text+".json")
    current_level.load()
    inputs["backgroundr"].text = str(current_level.meta["background"][0])
    inputs["backgroundg"].text = str(current_level.meta["background"][1])
    inputs["backgroundb"].text = str(current_level.meta["background"][2])


def save_level():
    global current_level
    f = open("level editor/levels/"+inputs["save"].text+".json", "w")
    current_level.update_raw()
    json.dump(current_level.raw, f, indent=2)
    current_level.file = "levels/"+inputs["save"].text+".json"
    inputs["load"].text = inputs["save"].text
    # current_level.load()

def zoom_out():
    global zoom
    zoom += 0.1
    zoom = round(zoom*10)/10
    level_cam.set_size(Vector2(original_size.x*zoom, original_size.y*zoom))


def zoom_in():
    global zoom
    zoom -= 0.1
    if zoom < 0.2:
        zoom = 0.1
    zoom = round(zoom*10)/10
    level_cam.set_size(Vector2(original_size.x*zoom, original_size.y*zoom))


def update_meta():
    name = inputs["name"].text
    try:
        size = [int(inputs["levelx"].text), int(inputs["levely"].text)]
    except TypeError:
        size = current_level.meta["size"]
    try:
        background = [int(inputs["backgroundr"].text), int(inputs["backgroundg"].text), int(inputs["backgroundb"].text)]
    except TypeError:
        background = current_level.meta["background"]
    current_level.meta = {"name": name, "size": size, "background": background}


def update_level_meta():
    global current_layer_index
    try:
        size = [int(inputs["layersizex"].text), int(inputs["layersizey"].text)]
    except TypeError:
        size = current_level.layers[current_layer_index].meta["size"]
    try:
        pos = [int(inputs["layerposx"].text), int(inputs["layerposy"].text)]
    except TypeError:
        pos = current_level.layers[current_layer_index].meta["position"]
    try:
        para = [float(inputs["parallax_x"].text), float(inputs["parallax_y"].text)]
    except TypeError:
        par = current_level.layers[current_layer_index].meta["parallax"]
    try:
        index = int(inputs["layerindex"].text)
    except TypeError:
        print("error")
        index = current_layer_index
    current_level.layers[current_layer_index].set_meta({"position": pos, "size":size, "parallax": para})
    if index != current_layer_index:
        layer = current_level.layers.pop(current_layer_index)
        print(layer)
        current_level.layers.insert(index, layer)
        current_layer_index = current_level.layers.index(layer)

def prev_layer():
    global current_layer_index
    current_layer_index -= 1
    if current_layer_index < 0:
        current_layer_index = 0

    inputs["layersizex"].text = str(int(current_level.layers[current_layer_index].size.x))
    inputs["layersizey"].text = str(int(current_level.layers[current_layer_index].size.y))
    inputs["layerposx"].text = str(int(current_level.layers[current_layer_index].position.x))
    inputs["layerposy"].text = str(int(current_level.layers[current_layer_index].position.y))
    inputs["parallax_x"].text = str(current_level.layers[current_layer_index].parallax.x)
    inputs["parallax_y"].text = str(current_level.layers[current_layer_index].parallax.y)
    inputs["layerindex"].text = str(current_layer_index)

def next_layer():
    global current_layer_index
    current_layer_index += 1
    if current_layer_index >= current_level.layers.__len__():
        current_layer_index = current_level.layers.__len__()-1

    inputs["layersizex"].text = str(int(current_level.layers[current_layer_index].size.x))
    inputs["layersizey"].text = str(int(current_level.layers[current_layer_index].size.y))
    inputs["layerposx"].text = str(int(current_level.layers[current_layer_index].position.x))
    inputs["layerposy"].text = str(int(current_level.layers[current_layer_index].position.y))
    inputs["parallax_x"].text = str(current_level.layers[current_layer_index].parallax.x)
    inputs["parallax_y"].text = str(current_level.layers[current_layer_index].parallax.y)
    inputs["layerindex"].text = str(current_layer_index)

def new_layer():
    global current_layer_index
    current_level.new_layer()
    current_layer_index = current_level.layers.__len__() - 1
    next_layer()

def delete_layer():
    global current_layer_index
    if current_level.layers.__len__() > 1:
        current_level.delete_layer(current_level.layers[current_layer_index])
        current_layer_index = 0
        prev_layer()

def update_level_cam():
    level_cam.clear(current_level.meta["background"])
    if inputs["gridsnapx"].text and inputs["gridsnapy"].text and buttons["grid"].on:
        draw_grid(level_cam, float(inputs["gridsnapx"].text), float(inputs["gridsnapy"].text), pygame.rect.Rect(0, 0, *current_level.meta["size"]))

    pygame.draw.rect(level_cam.surface, (0, 0, 0), (
        level_cam.draw_offset.x, level_cam.draw_offset.y, current_level.meta["size"][0] + 1,
        current_level.meta["size"][1] + 1), width=1)
    pygame.draw.rect(level_cam.surface, (0, 0, 200), (
        level_cam.draw_offset.x + current_level.layers[current_layer_index].position.x,
        level_cam.draw_offset.y + current_level.layers[current_layer_index].position.y,
        current_level.layers[current_layer_index].size.x + 1,
        current_level.layers[current_layer_index].size.y + 1), width=1)

    current_level.layers[current_layer_index].draw(level_cam, True)
    for sprite in current_level.layers[current_layer_index].sprites:
        pos = sprite.top_left.copy()
        if buttons["spriteID"].on:
            pos.x += 5 + current_level.layers[current_layer_index].position.x
            pos.y += 5 + current_level.layers[current_layer_index].position.y
            level_cam.draw_surf(KTFL.gui.get_text_surf(text=str(sprite.id)), position=pos.list)
        if sprite.tag and buttons["spriteTag"].on:
            tag_text = KTFL.gui.get_text_surf(f"{sprite.tag}")
            level_cam.surface.blit(tag_text, ((sprite.size.x / 2) - (tag_text.get_size()[0] / 2) + sprite.position.x + level_cam.draw_offset.x + current_level.layers[current_layer_index].position.x,
                                              sprite.size.y - (tag_text.get_size()[1] / 2) + sprite.position.y + level_cam.draw_offset.y + current_level.layers[current_layer_index].position.y))
    for obj in current_level.layers[current_layer_index].objects:
        rect = obj.rect
        pos = [rect.right - 15, rect.top + 5]
        pygame.draw.rect(level_cam.surface, (255, 255, 255), (rect.left + level_cam.draw_offset.x, rect.top + level_cam.draw_offset.y, rect.w, rect.h), width=1)
        level_cam.draw_surf(KTFL.gui.get_text_surf(text=str(obj.id), colour=(255, 255, 255)), position=pos)
        if obj.tag and buttons["objShowTag"].on:
            tag_text = KTFL.gui.get_text_surf(f"{obj.tag}",colour=(255, 255, 255))
            level_cam.surface.blit(tag_text, ((obj.rect.w / 2) - (tag_text.get_size()[0] / 2) + obj.rect.left + level_cam.draw_offset.x,
                                              obj.rect.h - (tag_text.get_size()[1] / 2) + obj.rect.top + level_cam.draw_offset.y - 10))


def update_menu():
    global selected_sprite, selected_sprite_offset, zoominfo
    menu_cam.clear()
    pygame.draw.rect(menu_cam.surface, (255, 255, 255), (0, 0, 300, 900))
    for surf in text_surfaces:
        menu_cam.draw_surf(surf[0], surf[1])
    for key in buttons:
        buttons[key].update(menu_cam)
    for key in inputs:
        inputs[key].update(menu_cam)

    mouse_pos = Vector2(*screen.control.mouse_pos(level_cam))
    if screen.control.on_action("delete"):
        delete_sprite()
    if screen.control.mouse_scroll()[1] > 0:
        if mouse_pos.x+level_cam.draw_offset.x >=0 and mouse_pos.y+level_cam.draw_offset.y >= 0:
            zoom_out()
        else:
            menu_cam.draw_offset.y -= 50
            if menu_cam.draw_offset.y < -menu_max_scroll:
                menu_cam.draw_offset.y = -menu_max_scroll
    elif screen.control.mouse_scroll()[1] < 0:
        if mouse_pos.x+level_cam.draw_offset.x >= 0 and mouse_pos.y+level_cam.draw_offset.y >= 0:
            zoom_in()
        else:
            menu_cam.draw_offset.y += 50
            if menu_cam.draw_offset.y > 0:
                menu_cam.draw_offset.y = 0

    if screen.control.on_action("level up"):
        move_cam_up()
    if screen.control.on_action("level down"):
        move_cam_down()
    if screen.control.on_action("level right"):
        move_cam_right()
    if screen.control.on_action("level left"):
        move_cam_left()

    pygame.draw.rect(menu_cam.surface, (current_level.meta["background"]), (menu_cam.size.x - zoominfo.get_width(), menu_cam.size.y - zoominfo.get_height(), zoominfo.get_width(), zoominfo.get_height()))
    zoominfo = KTFL.gui.get_text_surf(f"Zoom amount : {zoom}")
    menu_cam.surface.blit(zoominfo, (menu_cam.size.x - zoominfo.get_width(), menu_cam.size.y - zoominfo.get_height()))

    if screen.control.mouse_button(1) == "down":
        for sprite in current_level.layers[current_layer_index].sprites:
            if sprite.is_point_in_sprite(mouse_pos-current_level.layers[current_layer_index].position):
                selected_sprite = sprite
                selected_sprite_offset = mouse_pos - sprite.position
                inputs["file"].text = sprite.image_file
                inputs["positionx"].text = str(sprite.position.x)
                inputs["positiony"].text = str(sprite.position.y)
                inputs["sizex"].text = str(sprite.size.x)
                inputs["sizey"].text = str(sprite.size.y)
                inputs["id"].text = str(sprite.id)
                inputs["tag"].text = sprite.tag
    # sprite drag event
    elif screen.control.mouse_button(1) == "held" and selected_sprite:
        selected_sprite.position = mouse_pos - selected_sprite_offset
    # sprite release event
    elif not screen.control.mouse_button(1):
        if selected_sprite:
            if inputs["gridsnapx"].text and inputs["gridsnapy"].text and buttons["grid"].on:
                selected_sprite.position = Vector2(*selected_sprite.position.snap_to_grid(float(inputs["gridsnapx"].text), float(inputs["gridsnapy"].text)))
            inputs["positionx"].text = str(selected_sprite.position.x)
            inputs["positiony"].text = str(selected_sprite.position.y)
            selected_sprite = None
    pygame.draw.rect(menu_cam.surface, (0, 0, 0), (0, 0, 300, 900), width=3)


def create_sprite():
    file = inputs["file"].text
    try:
        position = [float(inputs["positionx"].text), float(inputs["positiony"].text)]
    except (TypeError, IndexError):
        return

    try:
        size = [float(inputs["sizex"].text), float(inputs["sizey"].text)]
    except (TypeError, IndexError):
        return

    if inputs["id"].text:
        try:
            id = int(inputs["id"].text)
        except TypeError:
            print("Invalid ID")
            return
    else:
        id = current_level.layers[current_layer_index].get_unused_sprite_id()


    if current_level.layers[current_layer_index].get_sprite_by_id(id):
        print("Can not have duplicate sprite IDs")
        return

    tag = inputs["tag"].text
    current_level.layers[current_layer_index].add_sprite(KTFL.sprite.Sprite(size, position, file, id=id, tag=tag))


def delete_sprite():
    id = int(inputs["id"].text)
    if id:
        current_level.layers[current_layer_index].delete_sprite(id)


def edit_sprite():
    try:
        id = int(inputs["id"].text)
    except ValueError:
        print("Invalid id")
        return
    sprite = current_level.layers[current_layer_index].get_sprite_by_id(id)
    if not sprite:
        edit_object()
        return
    try:
        if inputs["positionx"].text and inputs["positiony"]:
            position = [float(inputs["positionx"].text), float(inputs["positiony"].text)]
            sprite.position = position
        if inputs["sizex"].text and inputs["sizey"].text:
            size = [float(inputs["sizex"].text), float(inputs["sizey"].text)]
            sprite.size = size
    except ValueError:
        print("Invalid pos and size")
        return
    if inputs["file"].text:
        sprite.image = inputs["file"].text
    sprite.tag = inputs["tag"].text

def create_object():
    try:
        position = [float(inputs["objpositionx"].text), float(inputs["objpositiony"].text)]
    except (TypeError, IndexError):
        print("Invalid position try: 'x,y' where x and y are numbers")
        return

    try:
        size = [float(inputs["objsizex"].text), float(inputs["objsizey"].text)]
    except (TypeError, IndexError):
        print("Invalid position try: 'x,y' where x and y are numbers")
        return

    if inputs["objid"].text:
        try:
            id = int(inputs["objid"].text)
        except TypeError:
            print("Invalid ID")
            return
    else:
        id = current_level.layers[current_layer_index].get_unused_object_id()

    tag = inputs["objtag"].text
    current_level.layers[current_layer_index].add_object(pygame.rect.Rect(position[0], position[1], size[0], size[1]), id, True, tag=tag)


def edit_object():
    try:
        id = int(inputs["objid"].text)
    except ValueError:
        print("Invalid id")
        return
    obj = current_level.layers[current_layer_index].get_object_by_id(id)
    if not obj:
        return
    position = [obj.rect.x, obj.rect.y]
    try:
        if inputs["objpositionx"].text and inputs["objpositiony"]:
            position = [float(inputs["objpositionx"].text), float(inputs["objpositiony"].text)]
        size = [obj.rect.w, obj.rect.h]
        if inputs["objsizex"].text and inputs["objsizey"].text:
            size = [float(inputs["objsizex"].text), float(inputs["objsizey"].text)]
    except ValueError:
        print("Invalid size or position")
        return
    if inputs["objtag"].text:
        obj.tag = inputs["objtag"].text
    obj.rect.update(*position, *size)

def delete_object():
    id = int(inputs["objid"].text)
    if id:
        current_level.layers[current_layer_index].delete_object(id)

def draw_layer(index):
    layer = current_level.layers[index]
    layer.draw(level_cam, True)


create_menu()
update_level_cam()

while True:
    update_menu()
    update_level_cam()
    screen.update()
