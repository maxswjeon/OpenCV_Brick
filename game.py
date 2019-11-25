import pygame

from sprites.Ball import Ball
from sprites.Brick import Brick
from sprites.Paddle import Paddle
from threads.RankInput import RankInput
from threads.Webcam import Webcam

try:
    from cv2 import cv2
except ImportError:
    pass
import numpy

import sqlite3
import random
import time

# Adjustments
SCREEN_SIZE = (1280, 960)
PADDING = (50, 25, 25, 25)

# 8% of width, 3.5% of height is Fine
BRICK_SIZE = (100, 35)
BRICK_COUNT = (10, 5)
BRICK_PADDING = 10

BALL_SIZE = (24, 24)
BALL_SPEED = 10

PADDLE_SIZE = (75, 20)
PADDLE_SPEED = 10
PADDLE_BOTTOM = 200

low = (52, 72, 126)
high = (70, 154, 253)

roi = (450, 650)

# States
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
        self.init_sqlite()

    def init_pygame(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)  # type: pygame.Surface
        self.background = pygame.Surface(self.screen.get_size())
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('fonts/Noto_Sans_CJK_KR/Medium.otf', 32)

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

        frame_size = (SCREEN_SIZE[0] - PADDING[1] - PADDING[3], SCREEN_SIZE[1] - PADDING[0] - PADDING[2])

        self.cam_thread = Webcam(self.cap, SCREEN_SIZE, PADDING, low, high, roi)
        self.cam_thread.onFrameRead.append(resize_frame)
        self.cam_thread.start()

        print('Waiting For First Frame to Loaded')
        while not self.cam_thread.is_updated():
            pass
        print('Loaded First Frame')
        print()

        while self.cam_thread.get_frame() is None:
            pass

    def init_game(self):
        self.state = STATE_BALL_IN_PADDLE
        self.rank_saved = False
        self.score = 0
        self.prev = {}
        self.prev['score'] = 0
        self.prev['time'] = 0

        # Create Paddle
        image = pygame.image.load('images/Bar.png').convert_alpha()
        image = pygame.transform.scale(image, PADDLE_SIZE)
        self.paddle = Paddle(image)
        self.paddle.rect.center = (SCREEN_SIZE[0] / 2, SCREEN_SIZE[1] - PADDLE_BOTTOM)

        # Create Ball
        image = pygame.image.load('images/Ball.png').convert_alpha()
        image = pygame.transform.scale(image, BALL_SIZE)
        self.ball = Ball(image, self.paddle.rect.centerx, self.paddle.rect.top - 12)
        self.ball.speed = BALL_SPEED
        self.ball.boundRect(pygame.Rect(PADDING[3], PADDING[0], SCREEN_SIZE[0] - (PADDING[1] + PADDING[3]),
                                        SCREEN_SIZE[1] - (PADDING[0] + PADDING[2])))

        self.create_bricks()

        self.background.fill((0, 0, 0))
        t = self.font.render('Score : {0:04d}'.format(0), True, (255, 255, 255))
        self.background.blit(t,
                             (SCREEN_SIZE[0] - t.get_size()[0] - PADDING[1] - 15,
                              int((PADDING[0] - t.get_size()[1]) / 2)))

        t = self.font.render('Time : {0:02d}:{1:02d}'.format(0, 0), True, (255, 255, 255))
        self.background.blit(t,
                             (PADDING[3] + 15,
                              int((PADDING[0] - t.get_size()[1]) / 2)))

    def init_sqlite(self):
        self.db = sqlite3.connect('data/rank.db')
        self.rank_thread = RankInput(self.db)
        self.rank_token = None
        self.rank_thread.start()

    def create_bricks(self):
        self.bricks = pygame.sprite.Group()

        total_brick_width = -BRICK_PADDING + (BRICK_SIZE[0] + BRICK_PADDING) * BRICK_COUNT[0]

        side_pad = SCREEN_SIZE[0] - total_brick_width
        top_pad = PADDING[0] + BRICK_SIZE[1] * 2

        for i in range(0, BRICK_COUNT[1]):
            for j in range(0, BRICK_COUNT[0]):
                brick = Brick(random.randrange(1, 10), BRICK_SIZE)
                brick.rect.x = int(side_pad / 2) + j * (BRICK_SIZE[0] + BRICK_PADDING)
                brick.rect.y = top_pad + i * (BRICK_SIZE[1] + BRICK_PADDING)
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
                pos[0] -= PADDLE_SPEED
                if pos[0] < min_x:
                    pos[0] = min_x

            if keys[pygame.K_RIGHT]:
                pos[0] += PADDLE_SPEED
                if pos[0] > max_x:
                    pos[0] = max_x

        if keys[pygame.K_SPACE] and self.state == STATE_BALL_IN_PADDLE:
            self.state = STATE_PLAYING
            self.time_start = time.time()
            start_angle = random.randrange(20, 60)
            if random.random() < 0.5:
                start_angle = -start_angle
            self.ball.start(start_angle + 180)
        elif keys[pygame.K_RETURN] and (self.state in [STATE_GAME_OVER, STATE_WON]) and self.rank_token is None:
            self.init_game()
            return
        elif keys[pygame.K_h] and (self.state in [STATE_GAME_OVER, STATE_WON, STATE_BALL_IN_PADDLE]):
            self.draw_help()
            return
        elif keys[pygame.K_r] and (self.state in [STATE_GAME_OVER, STATE_WON]):
            self.draw_rank()

        if self.state == STATE_BALL_IN_PADDLE:
            self.paddle.move(tuple(pos))
            self.ball.move(pos=(pos[0], self.paddle.rect.top - 12))
        elif self.state == STATE_PLAYING:
            self.paddle.move(tuple(pos))

    def update_header(self):
        if self.state == STATE_PLAYING:
            time_elapsed = int(time.time() - self.time_start)
            if self.prev['score'] != self.score or time_elapsed != self.prev['time']:
                black = pygame.Surface((SCREEN_SIZE[0], PADDING[0]))

                self.background.blit(black, (0, 0))
                t = self.font.render('Score : {0:04d}'.format(self.score), True, (255, 255, 255))
                self.background.blit(t,
                                     (SCREEN_SIZE[0] - t.get_size()[0] - PADDING[1] - 15,
                                      int((PADDING[0] - t.get_size()[1]) / 2)))
                self.prev['score'] = self.score

                t = self.font.render('Time : {0:02d}:{1:02d}'.format(int(time_elapsed / 60), time_elapsed % 60), True,
                                     (255, 255, 255))
                self.background.blit(t,
                                     (PADDING[3] + 15,
                                      int((PADDING[0] - t.get_size()[1]) / 2)))
                self.prev['time'] = time_elapsed

    def run(self):
        done = False

        while not done:
            if self.cam_thread.is_updated():
                self.frame = self.cam_thread.get_frame()
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                self.frame = numpy.rot90(self.frame)
                self.frame = pygame.surfarray.make_surface(self.frame)
            self.background.blit(self.frame, (PADDING[3], PADDING[0]))

            self.update_header()

            self.bricks.draw(self.background)
            self.paddle.draw(self.background)
            self.ball.draw(self.background)

            if roi[0] != -1 and roi[1] != -1 and self.state == STATE_BALL_IN_PADDLE:
                pygame.draw.line(self.background, (255, 0, 0), (PADDING[3], roi[0]),
                                 (SCREEN_SIZE[0] - PADDING[1], roi[0]), 2)
                pygame.draw.line(self.background, (255, 0, 0), (PADDING[3], roi[1]),
                                 (SCREEN_SIZE[0] - PADDING[1], roi[1]), 2)

            if self.state in [STATE_WON, STATE_GAME_OVER] and not self.ball.go:
                self.add_rank()

            self.check_input(False)

            self.screen.blit(self.background, (0, 0))
            pygame.display.update()
            self.clock.tick(30)

            self.ball.move(self.bricks, self.paddle)

            if self.state == STATE_PLAYING:
                hit_list = pygame.sprite.spritecollide(self.ball, self.bricks, True, pygame.sprite.collide_mask)
                for h in hit_list:
                    self.score += h.score
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
                    self.clean()
                    done = True

    def add_rank(self):
        if not self.rank_saved:
            time_elapsed = time.time() - self.time_start
            self.rank_token = self.rank_thread.queue_info(self.score, time_elapsed, self.state)
            self.rank_saved = True

        status = self.rank_thread.get_status(self.rank_token)
        if status is None:
            s = pygame.Surface((800, 150))
            s.set_alpha(128)
            s.fill((255, 255, 255))

            f = pygame.font.Font('fonts/Noto_Sans_CJK_KR/Medium.otf', 72)
            t = f.render('Game Over', True, (255, 0, 0))
            s.blit(t, ((800 - t.get_size()[0]) / 2, (150 - t.get_size()[1]) / 2))

            self.background.blit(s, ((SCREEN_SIZE[0] - 800) / 2, (SCREEN_SIZE[1] - 150) / 2))
        else:
            # (uid, score, time, name, phone)
            cur = self.db.cursor()
            cur.execute('INSERT INTO rank(name, phone, score, "time") VALUES (?, ?, ?, ?)',
                        (status[3], status[4], status[1], status[2]))
            self.db.commit()
            self.rank_token = None

    def clean(self):
        print('Closing Game...')
        print()
        self.cam_thread.stop()
        print('Waiting for Camera Thread to Stop')
        while self.cam_thread.running:
            pass
        print('Camera Thread Stopped')
        print()

        self.rank_thread.stop()
        print('Waiting for Rank Thread to Stop')
        while self.rank_thread.running:
            pass
        print('Rank Thread Stopped')
        print()

        self.cap.release()
        cv2.destroyAllWindows()


def main(debug=False):
    game = Game()
    game.run()
    game.clean()


if __name__ == '__main__':
    main(True)
