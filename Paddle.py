import pygame


class Paddle(pygame.sprite.Sprite):
    def __init__(self, img: pygame.Surface):
        assert isinstance(img, pygame.Surface)
        super().__init__()
        self.image = img
        self.rect = img.get_rect()
        self.mask = pygame.mask.from_surface(img)

    def draw(self, surface: pygame.Surface):
        assert isinstance(surface, pygame.Surface)
        surface.blit(self.image, self.rect)

    def move(self, pos):
        self.rect.center = pos
