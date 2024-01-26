import pygame


class Sprite:
    def __init__(self, size, position, image=None, colour=(255, 255, 255)):
        self.size = size
        self.position = position
        if image:
            self.image = image
        else:
            self.image = pygame.surface.Surface(size)
            self.image.fill(colour)


class AnimatedSprite(Sprite):
    def __init__(self, size, position, image_data: dict):
        super().__init__(size, position)
        self.image_data = image_data
        for list in self.image_data:
            temp = []
            for image in self.image_data[list]["images"]:
                try:
                    temp.append(pygame.image.load(image).convert_alpha())
                except FileNotFoundError:
                    surf = pygame.surface.Surface((50, 50))
                    surf.fill((255, 255, 255))
                    temp.append(surf)
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
            self.image = self.image_data[self.state]["images"][self.index]

    def change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state
        self.index = -1
        self.tick = 0


if __name__ == '__main__':
    sprite = AnimatedSprite((50, 50), (0, 0), {
    "idle": {
      "tick": 0.5,
      "loop": True,
      "images": [
        "sprites/player/idle-00.png",
        "sprites/player/idle-01.png",
        "sprites/player/idle-02.png"
      ]
    },
    "run": {
      "tick": 0.1,
      "loop": True,
      "images": [
        "sprites/player/run-00.png",
        "sprites/player/run-01.png",
        "sprites/player/run-02.png",
        "sprites/player/run-03.png",
        "sprites/player/run-04.png",
        "sprites/player/run-05.png"
      ]
    }
  })