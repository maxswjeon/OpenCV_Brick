import pygame
from Brick import Brick
from Paddle import Paddle
from Ball import Ball

try:
    from cv2 import cv2
except ImportError:
    pass
import numpy
from Webcam import Webcam

import random

SCREEN_SIZE = (1280, 720)
PADDING = (50, 25, 25, 25)

low = (35, 75, 50)
high = (80, 150, 255)

STATE_BALL_IN_PADDLE = 0
STATE_PLAYING = 1
STATE_WON = 2
STATE_GAME_OVER = 3


def resize_frame(frame):
    frame = cv2.resize(frame, SCREEN_SIZE)
    frame = frame[PADDING[0]:-PADDING[2], PADDING[3]:-PADDING[1]]
    return True, frame


class Game:
    def __init__(self):
        self.init_pygame()
        self.init_opencv()
        self.init_game()

    def init_pygame(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE)  # type: pygame.Surface
        self.background = pygame.Surface(self.screen.get_size())
        self.clock = pygame.time.Clock()

    def init_opencv(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # self.cap = cv2.VideoCapture("C:/Users/maxsw/OneDrive/바탕 화면/blank.mp4")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, SCREEN_SIZE[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, SCREEN_SIZE[1])

        max_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        max_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if (max_width != SCREEN_SIZE[0]
                or max_height != SCREEN_SIZE[1]):
            print("Screen Too Big for Webcam")
            print("Max Resolution : {0}x{1}".format(max_width, max_height))
            # exit(1)

        self.cam_thread = Webcam(self.cap, low, high)
        self.cam_thread.onFrameRead.append(resize_frame)
        self.cam_thread.start()

        while self.cam_thread.get_frame() is None:
            pass

    def init_game(self):
        self.state = STATE_BALL_IN_PADDLE

        # Create Paddle
        image = pygame.image.load('images/Bar.png').convert_alpha()
        image = pygame.transform.scale(image, (75, 25))
        self.paddle = Paddle(image)
        self.paddle.rect.center = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] - 150)

        # Create Ball
        image = pygame.image.load('images/Ball.png').convert_alpha()
        image = pygame.transform.scale(image, (24, 24))
        self.ball = Ball(image, self.paddle.rect.centerx, self.paddle.rect.top - 12)
        self.ball.boundRect(pygame.Rect(PADDING[3], PADDING[0], SCREEN_SIZE[0] - (PADDING[1] + PADDING[3]),
                                        SCREEN_SIZE[1] - (PADDING[0] + PADDING[2])))

        self.create_bricks()

    def create_bricks(self):
        self.bricks = pygame.sprite.Group()
        for i in range(0, 5):
            for j in range(1, 11):
                brick = Brick(random.randrange(1, 10))
                brick.rect.x = 10 + j * 105
                brick.rect.y = 100 + i * 30
                self.bricks.add(brick)

    def check_input(self, cam_input=False):
        pos = list(self.paddle.rect.center)
        width = self.paddle.rect.width
        max_x = SCREEN_SIZE[0] - (PADDING[1] + PADDING[3]) - width / 2
        min_x = width
        keys = pygame.key.get_pressed()

        if cam_input:
            if self.cam_thread.center != -1:
                pos[0] = SCREEN_SIZE[0] - self.cam_thread.center
        else:
            if keys[pygame.K_LEFT]:
                pos[0] -= 10
                if pos[0] < min_x:
                    pos[0] = min_x

            if keys[pygame.K_RIGHT]:
                pos[0] += 10
                if pos[0] > max_x:
                    pos[0] = max_x

        if keys[pygame.K_SPACE] and self.state == STATE_BALL_IN_PADDLE:
            self.state = STATE_PLAYING
            start_angle = random.randrange(-60, 60)
            self.ball.start(start_angle + 180)
        elif keys[pygame.K_RETURN] and (self.state == STATE_GAME_OVER or self.state == STATE_WON):
            self.init_game()
            return

        if self.state == STATE_BALL_IN_PADDLE:
            self.paddle.move(tuple(pos))
            self.ball.move(pos=(pos[0], self.paddle.rect.top - 12))
        elif self.state == STATE_PLAYING:
            self.paddle.move(tuple(pos))

    def run(self):
        done = False

        while not done:
            frame = self.cam_thread.get_frame()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = numpy.rot90(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.background.fill((0, 0, 0))
            self.background.blit(frame, (PADDING[3], PADDING[0]))

            self.bricks.draw(self.background)
            self.paddle.draw(self.background)
            self.ball.draw(self.background)

            self.screen.blit(self.background, (0, 0))
            self.clock.tick(30)
            pygame.display.flip()

            self.check_input(True)

            self.ball.move(self.bricks, self.paddle)

            if self.state == STATE_PLAYING:
                hit_list = pygame.sprite.spritecollide(self.ball, self.bricks, True, pygame.sprite.collide_mask)
                for h in hit_list:
                    if h.rect.left <= self.ball.rect.centerx <= h .rect.right:
                        self.ball.direction[1] *= -1
                    else:
                        self.ball.direction[0] *= -1

                    if h.hit() == False:
                        self.bricks.remove(h)

                if len(hit_list) != 0:
                    sfx1 = pygame.mixer.Sound('sounds/pop.ogg')
                    sfx1.set_volume(0.5)
                    sfx1.play()

                if pygame.sprite.collide_mask(self.ball, self.paddle):
                    self.ball.colideBar(self.paddle.rect.center[0])

                if self.ball.rect.centery > self.paddle.rect.top:
                    self.state = STATE_GAME_OVER
                    # self.ball.stop()

                if len(self.bricks) == 0:
                    self.state = STATE_WON

            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.QUIT:
                    done = True

    def clean(self):
        self.cam_thread.stop()
        self.cap.release()
        cv2.destroyAllWindows()


def main(debug=False):
    game = Game()
    game.run()
    game.clean()


if __name__ == '__main__':
    main(True)
