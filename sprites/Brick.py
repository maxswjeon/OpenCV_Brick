import pygame


class Brick(pygame.sprite.Sprite):
    def __init__(self, index: int, size: tuple):
        assert isinstance(index, int)
        super().__init__()
        self.image = pygame.image.load('images/Brick/{:02d}.png'.format(index)).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        # self.score = random.randrange(100, 200)
        self.score = 100

    def hit(self):
        # TODO : Multiple Hits
        return False
