import os, time

class Logger:
    def __init__(self, base_dir: str, name: str):
        self.dir = os.path.join(base_dir, name)
        os.makedirs(self.dir, exist_ok=True)
        self.file = os.path.join(self.dir, 'log.txt')

    def log(self, msg: str):
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(self.file, 'a') as f:
            f.write(f'[{ts}] {msg}\n')
