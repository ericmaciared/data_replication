import socket
import time
from ports import *

class CoreNode:
    # Core layer nodes use update everywhere, active, and eager replication to replicate data
    def __init__(self, host, id, peers):
        self.host = host
        self.port = id + CORE_PORT
        
        # Init versions of file (Array of 10 ints)
        self.versions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Init log file
        self.log = f"logs/A{id}.txt"
        file = open(self.log, "w")
        file.write(str(self.versions))
        file.close()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def connect_to_peers(self, peers):
        for peer in peers:
            self.socket.connect((peer.host, peer.port))

    def run(self):
        pass
