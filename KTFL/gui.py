import pygame
import KTFL.sprite
import KTFL.control

FONT = pygame.font.Font("freesansbold.ttf", 15)


def get_text_surf(text, font=FONT, colour=(0, 0, 0)):
    return font.render(text, False, colour)


class Button:
    def __init__(self, size, position, function, image, select_image):
        self.size = size
        self.position = position
        self.function = function
        self.sprites = [KTFL.sprite.Sprite(size, position, image), KTFL.sprite.Sprite(size, position, select_image)]

    def update(self, surf: pygame.surface.Surface, input: KTFL.control.Input):
        image_index = 0
        if self.position[0] <= input.mouse_pos()[0] <= self.position[0] + self.size[0] and \
            self.position[1] <= input.mouse_pos()[1] <= self.position[1] + self.size[1]:
            image_index = 1
            if input.mouse_button(1) == "down":
                self.function()
        surf.blit(self.sprites[image_index].image, self.position)
