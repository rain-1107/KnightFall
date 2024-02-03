import pygame
import KTFL.control
import KTFL.sprite
import KTFL.util


class Display:
    def __init__(self, size=(500, 500), fullscreen=False, fps=60):
        if fullscreen:
            self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.size = KTFL.util.Vector2.list_to_vec(self.surface.get_size())
        else:
            self.surface = pygame.display.set_mode(size)
            self.size = KTFL.util.Vector2.list_to_vec(size)
        self.cameras = []
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.control = KTFL.control.Input()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        for camera in self.cameras:
            camera.update()
        pygame.display.flip()
        self.clock.tick(self.fps)
        self.control.update()

    def add_camera(self, camera):
        camera.display = self
        self.cameras.append(camera)

    def draw_to(self, sprite: KTFL.sprite.Sprite):
        self.surface.blit(sprite.image, sprite.position.list)

    def draw_surf(self, surf, position):
        self.surface.blit(surf, position)


class Camera:
    def __init__(self, size, display_size=0, position=(0, 0)):
        self.size = size
        self.display = None
        self.display_size = display_size
        self.position = KTFL.util.Vector2.list_to_vec(position)
        self.surface = pygame.surface.Surface(size, pygame.SRCALPHA)

    def update(self):
        surf = self.surface
        if self.display_size:
            self.display.surface.blit(pygame.transform.scale(surf, self.display_size), self.position.list)
            return
        self.display.surface.blit(pygame.transform.scale(surf, self.display.size.list), self.position.list)

    def draw_to(self, sprite: KTFL.sprite.Sprite):
        self.surface.blit(sprite.image, sprite.position.list)

    def draw_surf(self, surf, position):
        self.surface.blit(surf, position)
