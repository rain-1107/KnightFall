import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from .util import *
from .gui import get_text_surf

from copy import deepcopy

import numpy as np

import string
# TODO: add ability to draw lines


# abstracted shaders idk if u wanted that but iI did it
def create_shader(vertex_filepath, fragment_filepath):
    with open(vertex_filepath, 'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath, 'r') as f:
        fragment_src = f.readlines()

    return compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))


DEFAULT_SHADER = None


TEXTURE_CACHE = {}

OPENGL_OBJECTS = []


def load_texture(file, size=[50, 50], shader=DEFAULT_SHADER):  # NOTE: loads texture into memory does not return a usable object
    global TEXTURE_CACHE
    _image = file
    if type(file) != str:
        return
    if file in TEXTURE_CACHE:
        return
    try:
        _image = pygame.image.load(file).convert_alpha()
    except FileNotFoundError:
        _surf = pygame.surface.Surface(size)
        _surf.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        text = get_text_surf(f"{file}")
        _surf.blit(text,
                   ((size[0] / 2) - (text.get_size()[0] / 2), (size[1] / 2) - (text.get_size()[1] / 2)))
        _image = _surf.convert()
    texture = Material(_image)
    TEXTURE_CACHE[file] = texture


# For internal use
class Material:
    next_id = 0

    def __init__(self, image, create_quad=True):
        OPENGL_OBJECTS.append(self)
        self.loaded = False
        self.py_image = image
        self.size = self.py_image.get_size()
        self.texture = glGenTextures(1)
        self.id = self.next_id
        self.next_id = self.next_id + 1
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        img_data = pygame.image.tostring(image, 'RGBA')
        image_width, image_height = image.get_size()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        print(glGetError())
        if create_quad:
            self.quad = Quad(image_width, image_height)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def destroy(self):
        if self.loaded:
            glDeleteTextures(1, (self.texture,))


# For internal use
class Quad:
    def __init__(self, width, height):
        OPENGL_OBJECTS.append(self)
        self.width = width
        self.height = height
        self.loaded = False

    def load(self, display_size, shader):
        self.shader = shader
        self.display_size = display_size
        x_co = 2 / display_size[0]
        y_co = 2 / display_size[1]
        vertices = np.array([0, 0, 0, 1, 1, 1, 0, 0,  # top left
                             x_co * self.width, 0, 0, 1, 1, 1, 1, 0,  # top right
                             0, -(y_co * self.height), 0, 1, 1, 1, 0, 1,  # bottom left
                             x_co * self.width, -(y_co * self.height), 0, 1, 1, 1, 1, 1],  # bottom right
                            dtype=np.float32)

        # Define the indices to form a quad (two triangles)
        indices = np.array([0, 1, 2,  # First triangle (vertices 0, 1, 2)
                            1, 3, 2],  # Second triangle (vertices 1, 3, 2)
                           dtype=np.uint32)

        # Define the total number of vertices and indices
        self.vertex_count = 4
        self.index_count = 6

        # Generate a Vertex Array Object (VAO) and bind it
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Generate a Vertex Buffer Object (VBO) for vertices and bind it, then allocate memory and fill it with vertex data
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Enable the first attribute (position) in the vertex shader
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        # Enable the second attribute (color) in the vertex shader
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))

        # Generate an Index Buffer Object (IBO) and bind it, then allocate memory and fill it with index data
        self.ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        self.camera_uniloc = glGetUniformLocation(self.shader, "cameraScale")
        self.pos_uniloc = glGetUniformLocation(self.shader, "objectPos")
        self.loaded = True

    def draw(self, camera, position) -> None:
        # arm for drawing
        glUniform3f(self.camera_uniloc, camera.display_size.x / camera.size.x, camera.display_size.y / camera.size.y, 0)
        glUniform3f(self.pos_uniloc, position[0] * (2 / self.display_size[0]) - 1,
                    -(position[1] * (2 / self.display_size[1]) - 1), 0)
        glBindVertexArray(self.vao)
        # draw
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)

    def destroy(self) -> None:
        if self.loaded:
            glDeleteVertexArrays(1, (self.vao,))
            glDeleteBuffers(1, (self.vbo,))


class Font:
    def __init__(self, name, font, colour=(0, 0, 0)):
        self.pg_font = pygame.font.Font(font, 40)
        self.size = 40
        self.colour = colour
        surf = self.pg_font.render(string.printable, False, (255, 255, 255))
        pygame.image.save(surf, "font.png")
        surf_width = surf.get_width()
        self.char_width = surf_width/len(string.printable)
        self.character_texture = Material(surf, False)
        # TEXTURE_CACHE[name] = self.character_texture

    def get_char_uv(self, char) -> list:
        index = string.printable.index(char)
        #       u, v
        return [self.char_width*index, 0,
                self.char_width*(index+1), 0,
                self.char_width*index, self.size,
                self.char_width*(index+1), self.size]


class Text:
    def __init__(self, text, display_size, font=None):
        self.display_size = display_size
        self._text = text
        self.font = font
        if font is None:
            self.font = Font("1", "freesansbold.ttf")

    def load(self, shader):
        self.shader = shader
        vertices = np.array(self.get_line_vertices(self.text),  # bottom right
                            dtype=np.float32)

        # Define the indices to form a quad (two triangles)
        indices = np.array([0, 1, 2,  # First triangle (vertices 0, 1, 2)
                            1, 3, 2],  # Second triangle (vertices 1, 3, 2)
                           dtype=np.uint32)

        # Define the total number of vertices and indices
        self.vertex_count = 4
        self.index_count = 6

        # Generate a Vertex Array Object (VAO) and bind it
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Generate a Vertex Buffer Object (VBO) for vertices and bind it, then allocate memory and fill it with vertex data
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Enable the first attribute (position) in the vertex shader
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))

        # Enable the second attribute (color) in the vertex shader
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))

        # Generate an Index Buffer Object (IBO) and bind it, then allocate memory and fill it with index data
        self.ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        self.camera_uniloc = glGetUniformLocation(self.shader, "cameraScale")
        self.pos_uniloc = glGetUniformLocation(self.shader, "objectPos")
        self.loaded = True

    def draw(self, camera, position) -> None:
        # arm for drawing
        glUniform3f(self.camera_uniloc, camera.display_size.x / camera.size.x, camera.display_size.y / camera.size.y, 0)
        glUniform3f(self.pos_uniloc, position[0] * (2 / self.display_size[0]) - 1,
                    -(position[1] * (2 / self.display_size[1]) - 1), 0)
        glBindVertexArray(self.vao)
        # draw
        glDrawElements(GL_TRIANGLES, self.index_count, GL_UNSIGNED_INT, None)

    def get_line_vertices(self, text):
        vertices = []
        x_co = 2 / self.display_size[0]
        y_co = 2 / self.display_size[1]
        for i, char in enumerate(text):
            uv_coords = self.font.get_char_uv(char)
            #                x, y, z, r, g, b, u, v
            char_vertices = [(self.font.char_width*i)*x_co, 0, 0, 1, 1, 1, uv_coords[0], uv_coords[1],
                             (self.font.char_width * (i+1))*x_co, 0, 0, 1, 1, 1, uv_coords[2], uv_coords[3],
                             (self.font.char_width*i)*x_co, -(self.font.size*y_co), 0, 1, 1, 1, uv_coords[4], uv_coords[5],
                             (self.font.char_width * (i+1))*x_co,-(self.font.size*y_co), 0, 1, 1, 1, uv_coords[6], uv_coords[7],
                             ]
            vertices.extend(char_vertices)
        print(str(vertices[:8]))
        return vertices

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new):
        self._text = new

