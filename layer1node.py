import socket
import time
from ports import *

class Layer1Node:
    # Layer 1 nodes receive data every 10 updates (lazy) through passive replication, primary backup
    def __init__(self, host, id, parentId):
        self.host = host
        self.port = id + CORE_PORT
        
        # Init versions of file (Array of 10 ints)
        self.versions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Init log file
        self.log = f"logs/B{id}.txt"
        file = open(self.log, "w")
        file.write(str(self.versions))
        file.close()

    def run(self):
        pass
