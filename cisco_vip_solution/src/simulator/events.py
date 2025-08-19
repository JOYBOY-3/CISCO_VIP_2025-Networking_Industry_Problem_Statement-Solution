import threading

class SimEvents:
    def __init__(self):
        self.pause_evt = threading.Event()
        self.pause_evt.set()  # start in 'running' state

    def pause(self):
        self.pause_evt.clear()

    def resume(self):
        self.pause_evt.set()

    def wait_run(self):
        self.pause_evt.wait()
