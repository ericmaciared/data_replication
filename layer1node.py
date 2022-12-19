import time
import threading
from abc import ABC

from node import Node
from ports import *

TIMER = 10

class Layer1Node(Node, ABC):
    # Core layer nodes use update everywhere, active, and eager replication to replicate data
    def __init__(self, host, id, parentId):
        Node.__init__(self, host, id, L1_LAYER)
        print("Initializing L1 Node", id)

        self.id = id
        self.parentId = parentId
        self.parent = None

        # Values to operate with Data Replication
        self.timeThread = threading.Timer(TIMER, self.update_children)
        self.timeThread.name = "L1 Time Thread"

    def run(self):
        # Accept connection from parent
        self.socket.listen(1)
        conn, addr = self.socket.accept()
        self.parent = conn

        rcv = threading.Thread(target=self.receive_from_peer, args=(self.parent,))
        rcv.name = "L1 RCV"
        rcv.start()
        self.timeThread.start()

        print("L1 Node", self.id, " received parent connection")

        # While alive dispatch outgoing messages
        while self.is_alive or self.msg_queue:
            time.sleep(0.1)
            if self.msg_queue and self.dest_queue:
                self.send_to_peer(self.dest_queue.pop(0), self.msg_queue.pop(0))

        # Program Closing
        rcv.join()
        self.timeThread.cancel()
        self.timeThread.join()
        if self.bigBrotherTalking:
            self.bigBrotherSocket.close()
            self.bigBrotherThread.join()

        print("CLOSED NODE", self.layer, self.id)


    def process_instruction(self, instruction, sender, reply, position, value, bigBrother=None):
        pass





