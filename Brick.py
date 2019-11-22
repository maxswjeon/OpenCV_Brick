import pygame


class Brick(pygame.sprite.Sprite):
    def __init__(self, index:int):
        assert isinstance(index, int)
        super().__init__()
        self.image = pygame.image.load('images/Brick/{:02d}.png'.format(index)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 25))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def hit(self):
        # TODO : Multiple Hits
        return False
