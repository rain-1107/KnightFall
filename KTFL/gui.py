import pygame
import KTFL.sprite
import KTFL.control

FONT = pygame.font.Font("freesansbold.ttf", 15)

# TODO : GRID NEEDS TO BE LOCKED TO WORLD NOT CAMERA
# TODO : SO LIKE MAKE IT NOT MOVE WITH CAMERA IDK HOW IM TOO TIRED
# TODO : GOOD LOOK RYAN :D
def draw_grid(camera, sx, sy):
    if sx < 4 or sy < 4: #python shits the bed if too low :(
        return
    surf = camera.surface
    camerasnapped = camera.position.snap_to_grid(sx,sy)
    for x in range(0, surf.get_width(), int(sx)):
        for y in range(0, surf.get_height(), int(sy)):
            rect = pygame.Rect(x, y, sx, sy)
            pygame.draw.rect(surf, (255,255,255), rect, 1)

def get_text_surf(text, font=None, colour=(0, 0, 0)):
    if font:
        return font.render(text, False, colour)
    return FONT.render(text, False, colour)


class Button:
    def __init__(self, size, position, image, select_image, function=None, text=""):
        self.size = size
        self.position = position
        self.function = function
        self.pressed = False
        self.sprites = [KTFL.sprite.Sprite(size, position, image), KTFL.sprite.Sprite(size, position, select_image)]
        self.text_surf = get_text_surf(text)

    def update(self, camera):
        surf = camera.surface
        input = camera.display.control
        self.pressed = False
        image_index = 0
        if self.position[0] <= input.mouse_pos(camera)[0] <= self.position[0] + self.size[0] and \
                self.position[1] <= input.mouse_pos(camera)[1] <= self.position[1] + self.size[1]:
            image_index = 1
            if input.mouse_button(1) == "down":
                if self.function:
                    self.function()
                else:
                    self.pressed = True
        surf.blit(self.sprites[image_index].image, self.position)
        surf.blit(self.text_surf, [(self.position[0]+self.size[0]/2)-(self.text_surf.get_size()[0]/2), (self.position[1]+self.size[1]/2)-(self.text_surf.get_size()[1]/2)])


class Switch:
    def __init__(self, size, position, off_image, off_highlighted, on_image, on_highlighted):
        self.size = size
        self.position = position
        self.sprites = [
            [KTFL.sprite.Sprite(size, position, off_image), KTFL.sprite.Sprite(size, position, off_highlighted)],
            [KTFL.sprite.Sprite(size, position, on_image), KTFL.sprite.Sprite(size, position, on_highlighted)]]
        self.on = 0

    def update(self, camera):
        surf = camera.surface
        input = camera.display.control
        image_index = 0
        if self.position[0] <= input.mouse_pos(camera)[0] <= self.position[0] + self.size[0] and \
                self.position[1] <= input.mouse_pos(camera)[1] <= self.position[1] + self.size[1]:
            image_index = 1
            if input.mouse_button(1) == "down":
                self.on = int(not self.on == 1)
        surf.blit(self.sprites[self.on][image_index].image, self.position)


class TextInput:
    def __init__(self, size, position, background_image, text_font=None, text=""):
        self.size = size
        self.position = position
        self.sprite = KTFL.sprite.Sprite(size, position, background_image)
        self.text = text
        self.font = text_font
        self.pulse = 0.5
        self.tick = 0
        self.show_column = True
        self.selected = False

    def update(self, camera, dt=1 / 60):
        surf = camera.surface
        input = camera.display.control
        if input.mouse_button(1) == "down":
            if self.position[0] <= input.mouse_pos(camera)[0] <= self.position[0] + self.size[0] and \
                    self.position[1] <= input.mouse_pos(camera)[1] <= self.position[1] + self.size[1]:
                self.selected = True
                self.show_column = True
            else:
                self.selected = False
                self.show_column = False
                self.tick = self.pulse
        if self.selected:
            for key in input.log["keys"]:
                try:
                    if chr(key) == "\b":
                        self.text = self.text[:-1]
                    elif chr(key) not in """qwertyuiop[]asdfghjkl;'#\zxcvbnm,./1234567890-=`QWERTYUIOP{}ASDFGHJKL:@~|ZXCVBNM<>?\\¬!"£$%^&*()_+ """:
                        pass
                    else:
                        if input.log["keys"][key][1] & pygame.KMOD_LSHIFT:
                            self.text += chr(key).upper()
                        else:
                            self.text += chr(key)
                except ValueError:
                    pass
            self.tick -= dt
            if self.tick < 0:
                self.tick = self.pulse
                self.show_column = not self.show_column
            self.sprite.draw_to(surf)
            if self.show_column:
                surf.blit(get_text_surf(self.text+"|", font=self.font),
                          [self.position[0] + 5, self.position[1] + self.size[1] / 2 - 8])
                return
            surf.blit(get_text_surf(self.text, font=self.font),
                      [self.position[0] + 5, self.position[1] + self.size[1] / 2 - 8])
            return
        self.sprite.draw_to(surf)
        surf.blit(get_text_surf(self.text, font=self.font),
                  [self.position[0] + 5, self.position[1] + self.size[1] / 2 - 8])
