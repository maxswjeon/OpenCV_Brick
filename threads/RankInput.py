import time as t
import uuid
from threading import Thread

STATE_BALL_IN_PADDLE = 0
STATE_PLAYING = 1
STATE_WON = 2
STATE_GAME_OVER = 3


class RankInput(Thread):
    def __init__(self, db):
        self.db = db
        self.running = True
        self.queue = []
        self.finished = []
        super().__init__()

    def queue_info(self, score, time, state):
        uid = uuid.uuid4()
        self.queue.append((uid, score, time, state))
        return uid

    def get_status(self, id):
        res = None
        for i in self.finished:
            if i[0] == id:
                res = i
                break

        if res is not None:
            self.finished.remove(res)

        return res

    def run(self):
        while self.running:
            if len(self.queue) != 0:
                item = self.queue.pop()

                uid = item[0]
                score = item[1]
                time = item[2]
                state = item[3]

                print("You scored {0} in {1:02d}:{2:02d}! Well Done!".format(score, int(time / 60), int(time) % 60))
                if state == STATE_WON:
                    print("Wow! You scored a perfect score! Excellent!")
                name = input("Please type your name here : ")
                phone = input("Please type your phone number here : ")
                print("Thanks for playing!")

                self.finished.append((uid, score, time, name, phone))
                t.sleep(1)

    def stop(self):
        self.running = False
