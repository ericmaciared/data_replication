from ports import *
from pickle import loads, dumps
from communication import *
from node import Node
from abc import ABC

class CoreNode(Node, ABC): 
    """Core nodes perform update everywhere, eager and active replication for data"""
    def __init__(self, id, peers = None, children = []):
        super().__init__(CORE_LAYER_PORT, id)
        self.peers = peers
        self.children = children


    def execute_instruction(self, message):
        """Executes instruction on node"""
        if message.instruction.operation == WRITE:
            self.write_value(message.instruction.position, message.instruction.value)
            
            # Propagate WRITE_ACK to peers
            self.ack_count = 1
            message.instruction.operation = WRITE_ACK # Change operation to WRITE_ACK for peers_
            for peer in self.peers:
                message = Message(sender=self.port, destination=node_port(self.layer, peer), instruction=message.instruction)
                self.send_message(message)

            # Ensure write completions from peers (active replication)
            #print(f"{self.name}: Waiting for ACKs {message.instruction}")
            while self.ack_count < len(self.peers) + 1:
                pass
            #print(f"{self.name}: Executed write {message.instruction}")

            # Commit changes to big brother
            message.instruction.operation = ACK
            #print(f"{self.name}: Sending ACK to big brother {message.instruction}")
            self.send_message(Message(sender=self.port, destination=BIG_BROTHER_PORT, instruction=message.instruction))
        
        elif message.instruction.operation == WRITE_ACK:
            self.write_value(message.instruction.position, message.instruction.value) # Execute write locally

            # Commit changes to sender
            message.instruction.operation = ACK # Change operation to ACK for peers
            self.send_message(Message(sender=self.port, destination=message.sender, instruction = message.instruction))

        elif message.instruction.operation == READ:
            self.read_value(message.instruction.position)

        elif message.instruction.operation == QUIT:
            print(f"{self.name}: quitting.")


    def run(self):
        while self.alive:
            if self.updates == 10:
                # Send changes to children
                self.send_changes()
                self.updates = 0