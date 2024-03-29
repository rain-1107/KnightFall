import KTFL
import pygame
import json

if __name__ == '__main__':
    ...

screen = KTFL.display.Display()
screen.control.load_controls("bin/settings/controls.json")
camera = KTFL.display.Camera((500, 500))
screen.add_camera(camera)

player = KTFL.entities.OverheadPlayer()
image_data = json.load(open("KTFL/bin/animatedSprite/example.json"))
other_sprite = KTFL.sprite.AnimatedSprite([25, 50], [0, 0], image_data, centered=True)

client = KTFL.net.client.Client("local")
client.run()

pygame.time.wait(200)

client.create_variable(f"{client.id} pos", player.rect.topleft, KTFL.net.VECTOR, interpolated=True)

while True:
    camera.clear((200, 200, 200))
    player.update(camera)
    for var in client.variables.copy():
        if "pos" in client.variables[var].name and client.variables[var].name != f"{client.id} pos":
            # print(type(client.variables[var]))
            if type(client.variables[var].value) == tuple:
                other_sprite.position = [client.variables[var].value[0]+ 12.5, client.variables[var].value[1]+25]
        # print(client.variables[var].value, client.variables[var].id)
    other_sprite.update_animation(screen.delta_time)
    camera.draw_sprite(other_sprite)
    var = client.get_var_by_name(f"{client.id} pos")
    if var:
        client.update_variable(var.id, player.rect.topleft, KTFL.net.VECTOR)
    screen.update()