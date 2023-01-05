from ports import *
from pickle import loads, dumps
from communication import *
from node import Node
from abc import ABC
import time

class L1Node(Node, ABC): 
    """Layer 1 nodes perform primary backup, lazy and passive replication for data"""
    def __init__(self, id, children=[]):
        super().__init__(L1_LAYER_PORT, id)
        self.children = children
        self.timer = time.time()

    def execute_instruction(self, message):
        """Executes instruction on node"""
        if message.instruction.operation == WRITE:
            self.write_value(message.instruction.position, message.instruction.value)
            #print(f"{self.name}: Executed write {message.instruction}")

        elif message.instruction.operation == READ:
            self.read_value(message.instruction.position)

        elif message.instruction.operation == QUIT:
            print(f"{self.name}: quitting.")


    def run(self):
        while self.alive:
            if time.time() - self.timer >= 10:
                # Send changes to children
                self.send_changes()
                self.timer = time.time()

            
