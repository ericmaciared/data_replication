import socket
import time
from ports import *

class Layer2Node:
    # Layer 2 receives the data every 10 seconds (lazy) through passive replication and primary backup.
    def __init__(self, host, id, parentId):
        self.host = host
        self.port = id + CORE_PORT
        
        # Init versions of file (Array of 10 ints)
        self.versions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        # Init log file
        self.log = f"logs/C{id}.txt"
        file = open(self.log, "w")
        file.write(str(self.versions))
        file.close()

    def writeToFile(msg):
        file = open(self.log, "w")
        file.write(msg)
        file.close()

    def run(self):
        pass
