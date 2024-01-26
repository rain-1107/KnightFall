import pygame
import KTFL.sprite



class Display:
    def __init__(self, size=(500, 500), fullscreen=False, fps=60):
        if fullscreen:
            self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.surface = pygame.display.set_mode(size)
        self.size = self.surface.get_size()
        self.cameras = []
        self.fps = fps
        self.clock = pygame.time.Clock()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        for camera in self.cameras:
            camera.update(self)
        pygame.display.flip()
        self.clock.tick(self.fps)

    def add_camera(self, camera):
        self.cameras.append(camera)

    def draw_to(self, sprite: KTFL.sprite.Sprite):
        self.surface.blit(sprite.image, sprite.position)


class Camera:
    def __init__(self, size, display_size=0, position=(0, 0)):
        self.size = size
        self.display_size = display_size
        self.position = position
        self.surface = pygame.surface.Surface(size)

    def update(self, display: Display):
        if self.display_size:
            display.surface.blit(pygame.transform.scale(self.surface, self.display_size), self.position)
            return
        display.surface.blit(pygame.transform.scale(self.surface, display.size), self.position)

    def draw_to(self, sprite: KTFL.sprite.Sprite):
        self.surface.blit(sprite.image, sprite.position)
