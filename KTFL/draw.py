import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from .util import *
from .gui import get_text_surf

from copy import deepcopy

import numpy as np

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

    def __init__(self, image):
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
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        img_data = pygame.image.tostring(image, 'RGBA')
        image_width, image_height = image.get_size()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        self.quad = Quad(image_width, image_height)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def __del__(self):
        if self.loaded:
            glDeleteTextures(1, (self.texture,))


# For internal use
class Quad:
    def __init__(self, width, height):
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

        # Convert the vertices and indices into NumPy arrays with appropriate data types
        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

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
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class Sprite:
    def __init__(self, size, position, image=None, colour=(255, 255, 255), centered=False, id=0, tag="", level=None):
        self.id = id
        self.centered = centered
        self._size = Vector2.list_to_vec(size)
        self.top_left = Vector2(0, 0)
        self.position = position
        self._image = image
        load_texture(self._image)
        self._tag = tag
        self.level = level

        self.size = TEXTURE_CACHE[self._image].size

    def draw_to(self, cam):  # TODO: abstract this to add to draw list
        cam.draw_sprite(self)

    def is_point_in_sprite(self, point):
        point = Vector2.list_to_vec(point)
        if self.top_left.x < point.x < self.top_left.x + self.size.x:
            if self.top_left.y < point.y < self.top_left.y + self.size.y:
                return True
        return False

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, new):
        self._tag = new

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new):
        self.image_file = new
        load_image(new, self.size.list)

    @property
    def size(self) -> Vector2:
        return self._size

    @size.setter
    def size(self, new):
        self._size = Vector2.list_to_vec(new)

    @property
    def position(self) -> Vector2:
        if self.centered:
            return self.centre
        return self.top_left

    @position.setter
    def position(self, new):
        if self.centered:
            self.centre = new
            return
        self.top_left = Vector2.list_to_vec(new)

    @property
    def centre(self) -> Vector2:
        return Vector2(self.top_left.x + (self.size.x / 2), self.top_left.y + (self.size.y / 2))

    @centre.setter
    def centre(self, new):
        _centre = Vector2.list_to_vec(new)
        self.top_left.set(Vector2(_centre.x-self.size.x/2, _centre.y-self.size.y/2))


class AnimatedSprite(Sprite):
    def __init__(self, size, position, image_data: dict, centered=False, id=0, tag=""):
        super().__init__(size, position, id=id, centered=centered, tag=tag)
        self.raw_data = deepcopy(image_data)
        self.image_data = deepcopy(image_data)
        for list in self.image_data:
            temp = []
            for image in self.image_data[list]["images"]:
                image = load_image(image, self.size.list)
                temp.append(image)
            self.image_data[list]["images"] = temp
        self.index = 0
        self.tick = 0
        self.state = next(iter(self.image_data))
        self.previous_state = next(iter(self.image_data))

    def update_animation(self, delta_time: float = 1 / 60):
        self.tick -= delta_time
        if self.tick < 0:
            self.tick = self.image_data[self.state]["tick"]
            self.index += 1
            if self.index > self.image_data[self.state]["images"].__len__() - 1:
                if self.image_data[self.state]["loop"]:
                    self.index = 0
                else:
                    self.change_state(self.previous_state)
            self._image = self.image_data[self.state]["images"][self.index]
            self.size = self.image.get_size()

    def change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state
        self.index = -1
        self.tick = 0
