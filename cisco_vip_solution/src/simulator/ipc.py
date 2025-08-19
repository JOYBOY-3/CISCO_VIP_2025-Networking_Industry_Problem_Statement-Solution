import socket, threading, queue, time
from typing import Dict, Tuple

# Simple TCP-based IPC for metadata packets
# Each node hosts a server on a port; neighbors connect as clients.
# Messages are plaintext lines for simplicity.

class IPCServer(threading.Thread):
    def __init__(self, host: str, port: int):
        super().__init__(daemon=True)
        self.host, self.port = host, port
        self.inbox = queue.Queue()
        self._stop = threading.Event()
        self.sock = None

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.sock.settimeout(0.5)
        conns = []
        while not self._stop.is_set():
            try:
                c, _ = self.sock.accept()
                c.settimeout(0.1)
                conns.append(c)
            except socket.timeout:
                pass
            # read from all
            for c in list(conns):
                try:
                    data = c.recv(4096)
                    if data:
                        for line in data.decode(errors='ignore').splitlines():
                            self.inbox.put(line.strip())
                except socket.timeout:
                    pass
                except Exception:
                    try: c.close()
                    except: pass
                    conns.remove(c)
        for c in conns:
            try: c.close()
            except: pass
        try: self.sock.close()
        except: pass

    def stop(self):
        self._stop.set()

def send_msg(host: str, port: int, msg: str):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        s.connect((host, port))
        s.sendall((msg + '\n').encode())
        s.close()
    except Exception:
        pass
