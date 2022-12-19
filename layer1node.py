import time
import threading
from abc import ABC

from node import Node
from ports import *

TIMER = 10

class Layer1Node(Node, ABC):
    # Core layer nodes use update everywhere, active, and eager replication to replicate data
    def __init__(self, host, id, parentId, bigBrotherTalking):
        Node.__init__(self, host, id, L1_LAYER, bigBrotherTalking)
        print("Initializing L1 Node", id)

        self.id = id
        self.parentId = parentId
        self.parent = None

        # Values to operate with Data Replication
        self.timeThread = threading.Timer(TIMER, self.update_children)

    def run(self):
        # Accept connection from parent
        self.socket.listen(1)
        conn, addr = self.socket.accept()
        self.parent = conn

        rcv = threading.Thread(target=self.receive_from_peer, args=(self.parent,))
        rcv.start()
        self.timeThread.start()

        print("L1 Node", self.id, " received parent connection")

        # Connect to big brother if required
        if self.bigBrotherTalking: self.connect_to_big_bro()

        # While alive dispatch outgoing messages
        while self.is_alive or self.msg_queue:
            time.sleep(0.1)
            if self.msg_queue and self.dest_queue:
                self.send_to_peer(self.dest_queue.pop(0), self.msg_queue.pop(0))

        # Program Closing
        rcv.join()
        self.timeThread.cancel()
        self.timeThread.join()
        if self.bigBrotherThread is not None: self.bigBrotherThread.join()

        print("CLOSED NODE", self.layer, self.id)


    def process_instruction(self, instruction, sender, reply, position, value, bigBrother=None):
        pass





