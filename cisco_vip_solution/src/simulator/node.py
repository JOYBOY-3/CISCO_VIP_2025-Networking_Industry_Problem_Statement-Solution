import threading, time, random
from typing import Dict, List
from .ipc import IPCServer, send_msg

class SimNode(threading.Thread):
    def __init__(self, name: str, node_type: str, port: int, neighbors: Dict[str, int], log):
        super().__init__(daemon=True)
        self.name = name
        self.type = node_type
        self.port = port
        self.neighbors = neighbors  # neighbor name -> port
        self.server = IPCServer('127.0.0.1', port)
        self.log = log
        self.fail_links = set()  # names of neighbors whose link is down
        self._stop = threading.Event()
        self.events = None  # set by runner

    def set_events(self, events):
        self.events = events

    def notify_link_failure(self, peer: str):
        self.fail_links.add(peer)

    def run(self):
        self.server.start()
        self.log.log(f'Node {self.name} started on port {self.port} with neighbors {self.neighbors}')
        time.sleep(0.2)
        # Day-1: neighbor discovery/hello
        while not self._stop.is_set():
            self.events.wait_run()
            # send hello to neighbors whose link is up
            for nb, p in self.neighbors.items():
                if nb in self.fail_links:
                    continue
                send_msg('127.0.0.1', p, f'HELLO from {self.name} to {nb}')
            # process inbox
            while not self.server.inbox.empty():
                msg = self.server.inbox.get()
                if msg.startswith('HELLO'):
                    self.log.log(f'{self.name} recv: {msg}')
            time.sleep(0.5)

    def stop(self):
        self._stop.set()
        self.server.stop()
