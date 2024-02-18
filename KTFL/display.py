import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import sys
import KTFL.control
import KTFL.draw
from .util import *


class Display:
    def __init__(self, size=(500, 500), fullscreen=False, fps=60):
        if fullscreen:
            self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.OPENGL | pygame.DOUBLEBUF)
            self.size = KTFL.util.Vector2.list_to_vec(self.surface.get_size())
        else:
            self.surface = pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF)
            self.size = KTFL.util.Vector2.list_to_vec(size)

        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                        pygame.GL_CONTEXT_PROFILE_CORE)

        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.cameras = []
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.control = KTFL.control.Input()
        self.delta_time = 1
        self.shader = KTFL.draw.create_shader("KTFL/shaders/spr_vertex.glsl", "KTFL/shaders/spr_frag.glsl")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        KTFL.draw.DEFAULT_SHADER = self.shader
        self.draw_queue = {}

    def load_quads(self):
        for texture in KTFL.draw.TEXTURE_CACHE:
            KTFL.draw.TEXTURE_CACHE[texture].quad.load(self.size.list, self.shader)

    def update(self):  # TODO: add drawing code here for all sprites for optimisation (OpenGL); use batching etc.or event in pygame.event.get():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
        # refresh screen
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(self.shader)

        for image in self.draw_queue:
            KTFL.draw.TEXTURE_CACHE[image].use()
            for instance in self.draw_queue[image]:
                KTFL.draw.TEXTURE_CACHE[image].quad.draw(instance[0], instance[1])

        pygame.display.flip()
        self.clock.tick(self.fps)
        self.delta_time = 1 / (self.clock.get_fps()+1)
        self.control.update()

    def add_camera(self, camera):
        camera.display = self
        if not camera.display_size:
            camera.display_size = self.size
            camera.size_factor = camera.size/self.size
        self.cameras.append(camera)

    def add_cameras(self, *cameras):
        for camera in cameras:
            self.add_camera(camera)

    def close(self):
        for obj in KTFL.draw.OPENGL_OBJECTS:
            obj.destroy()
        exit()


class Camera:
    def __init__(self, size, display_size=0, position=(0, 0)):  # TODO: add relevant variables for drawing in OpenGL
        self.size = Vector2.list_to_vec(size)
        self.display = None
        self.display_size = display_size
        self.position = Vector2.list_to_vec(position)
        self.size_factor = Vector2(1, 1)
        self.surface = pygame.surface.Surface(size, pygame.SRCALPHA)
        self.surface.set_clip((0, 0, self.size.x, self.size.y))
        self.draw_offset = Vector2(0, 0)
        self.world_pos = Vector2(0, 0)

    def draw_sprite(self, sprite):
        pos = sprite.top_left.copy()
        pos = (pos-self.world_pos+self.draw_offset) * self.size_factor + self.position
        if sprite.image in self.display.draw_queue:
            self.display.draw_queue[sprite.image].append([self, pos.list])
        self.display.draw_queue[sprite.image] = [[self, pos.list]]

    def draw_text(self, text_obj, position):
        pos = Vector2.list_to_vec(position)
        if text_obj.font.name in self.display.draw_queue:
            self.display.draw_queue[text_obj.font.name].append([self, pos.list])


    def lock_to(self, sprite):
        self.lock_x_to(sprite)
        self.lock_y_to(sprite)

    def lock_x_to(self, sprite):
        self.world_pos.x = round(sprite.top_left.x) + sprite.size.x / 2 - self.size.x / 2

    def lock_y_to(self, sprite):
        self.world_pos.y = round(sprite.top_left.y - sprite.size.y / 2 - self.size.y / 2)

    def delete(self):
        self.display.cameras.remove(self)
        del self

    def clear(self, colour=None):
        if colour:
            self.surface.fill(colour)
            return
        self.surface.fill((0, 0, 0, 0))

    def set_size(self, new):
        self.size = new
        self.surface = pygame.surface.Surface(self.size.list, pygame.SRCALPHA)