import threading
import time
import random

class Thread(threading.Thread):
    def __init__(self, sec):
        super(Thread, self).__init__()
        self.is_running = True
        self.thlock = 1
        self.keylock = 0
        self.parent = None
        self.sec = sec
        self.start()

    def __call__(self):
        self.keylock = 1
        self.unlock()

    def set_parent(self, parent):
        self.parent = parent

    def lock(self):
        self.thlock = 1

    def unlock(self):
        self.thlock = 0

    def is_lock(self):
        return self.thlock

    def is_cpu(self):
        return self.parent.cpu

    def is_end(self):
        return self.parent.is_end

    def is_gorilla(self):
        return self.parent.gorilla

    def random_choice(self):
        if self.is_end():
            self.lock()
            return
        time.sleep(self.sec)
        tag = random.choice(list(self.parent.candidates.keys()))
        self.parent.update_board(tag)
        if self.is_cpu() or self.is_gorilla():
            return
        self.lock()
        self.keylock = 0

    def alpha_zero(self):
        pass

    def run(self):
        while self.is_running:
            if self.is_lock():
                continue
            self.random_choice()