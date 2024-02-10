import KTFL
import pygame
import json

screen = KTFL.display.Display()
screen.control.load_controls("bin/settings/controls.json")
camera = KTFL.display.Camera((500, 500))
screen.add_camera(camera)

player = KTFL.entities.OverheadPlayer("bin/entity data/player/player.json")
image_data = json.load(open("bin/entity data/player/player.json"))["image_data"]
other_sprite = KTFL.sprite.AnimatedSprite([24, 35], [100, 100], image_data, centered=True)

client = KTFL.net.client.Client("local")
client.run()

pygame.time.wait(200)

client.new_var(client.id, f"{client.id} pos", player.rect.topleft, KTFL.net.VECTOR)

while True:
    camera.clear()
    player.update(camera)
    for var in client.variables.copy():
        if "pos" in client.variables[var].name and client.variables[var].name != f"{client.id} pos":
            other_sprite.position = client.variables[var].value
        print(client.variables[var].value, client.variables[var].name[:-3])
    other_sprite.update_animation(screen.delta_time)
    camera.draw_sprite(other_sprite)
    var = client.get_var_by_name(f"{client.id} pos")
    if var:
        client.update_var(var.id, player.rect.topleft, KTFL.net.VECTOR)
    screen.update()