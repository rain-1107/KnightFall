import pygame

FONT = pygame.font.Font("freesansbold.ttf", 15)


def get_text_surf(text, font=FONT, colour=(0, 0, 0)):
    return font.render(text, False, colour)
