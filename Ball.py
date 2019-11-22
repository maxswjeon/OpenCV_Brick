import pygame
import math

from Paddle import Paddle


class Ball(pygame.sprite.Sprite):
    def __init__(self, img: pygame.Surface, x: int, y: int):
        assert isinstance(img, pygame.Surface)
        assert isinstance(x, int)
        assert isinstance(y, int)

        super().__init__()
        self.image = img
        self.rect = img.get_rect()
        self.rect.center = (x, y)
        self.mask = pygame.mask.from_surface(img)
        self.go = False
        self.dt = 10
        self.x = x
        self.y = y
        self.direction = [1, 1]

    def boundRect(self, rect):
        self.brect = rect

    def start(self, angle):
        self.angle = angle
        self.go = True

    def stop(self):
        self.go = False

    def moveLeft(self, bx):
        self.angle = 191 + bx
        self.direction[0] = 1

    def moveRight(self, bx):
        self.angle = 169 + bx
        self.direction[0] = 1

    def colideBar(self, bar_x):
        self.direction[1] *= -1

        bx = bar_x - self.rect.center[0]
        if self.rect.center[0] < bar_x:
            self.moveLeft(bx)
        elif self.rect.center[0] > bar_x:
            self.moveRight(bx)

    def draw(self, surface: pygame.Surface):
        assert isinstance(surface, pygame.Surface)
        surface.blit(self.image, self.rect)

    def move(self, bricks: pygame.sprite.Group = None, paddle: Paddle = None, pos: tuple = None):
        if pos is not None:
            self.x = pos[0]
            self.y = pos[1]
            self.rect.center = (self.x, self.y)
            return

        if not self.go:
            return

        dx = math.sin(math.radians(self.angle)) * self.dt * self.direction[0]
        dy = math.cos(math.radians(self.angle)) * self.dt * self.direction[1]

        self.x += dx
        self.y += dy

        if self.x - self.rect.width / 2 < self.brect.x:
            self.x = self.brect.x + self.rect.width / 2
            self.direction[0] *= -1
        if self.y - self.rect.width / 2 < self.brect.y:
            self.y = self.brect.y + self.rect.width / 2
            self.direction[1] *= -1
        if self.x + self.rect.width / 2 > self.brect.x + self.brect.width:
            self.x = self.brect.x + self.brect.width - self.rect.width / 2
            self.direction[0] *= -1
        if self.y + self.rect.width / 2 > self.brect.y + self.brect.height:
            self.stop()

        self.rect.center = (self.x, self.y)



