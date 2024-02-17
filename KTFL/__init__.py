import sys
import os

try:
    import pygame
except ModuleNotFoundError:
    print("Pygame not installed")
    exit()
try:
    import shapely
except ModuleNotFoundError:
    print("Shapely not installed")
try:
    import OpenGL
except ModuleNotFoundError:
    print("OpenGL not installed")
    exit()

pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                pygame.GL_CONTEXT_PROFILE_CORE)

import KTFL.display
import KTFL.gui
import KTFL.control
import KTFL.load
import KTFL.draw
import KTFL.util
import KTFL.entities
import KTFL.particle
import KTFL.net
