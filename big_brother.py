from core_node import CoreNode
from l1_node import L1Node
from l2_node import L2Node
from communication import *
import threading
from ports import *
import time
import pickle
import random

class BigBrother:
    def __init__(self):
        """Initialize Big Brother structure, creates data nodes and starts them"""
        self.name = "Big Brother"
        self.alive = True # Determines if structure should be running
        self.port = BIG_BROTHER_PORT

        self.nodes = []
        self.node_threads = []
        
        # Core Layer
        self.nodes.append(CoreNode(id = 1, peers = [2, 3]))
        self.nodes.append(CoreNode(id = 2, peers = [1, 3], children=[1]))
        self.nodes.append(CoreNode(id = 3, peers = [1, 2], children=[2]))

        # L1 Layer
        self.nodes.append(L1Node(id = 1))
        self.nodes.append(L1Node(id = 2, children = [1, 2]))

        # L2 Layer
        self.nodes.append(L2Node(id = 1))
        self.nodes.append(L2Node(id = 2))
        
        # Start node threads
        for node in self.nodes:
            self.node_threads.append(threading.Thread(target = node.run))

        for thread in self.node_threads:
            thread.start()
        
        # Initialize listener thread for incoming messages
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, self.port))
        print(f"{self.name}: listening on port {self.port}")
        self.ack = 0

        self.listener = threading.Thread(target = self.accept_messages)
        self.listener.start()


    def execute_instruction(self, layer, instruction):
        """Executes instruction on node 1 in layer specified"""
        #destination_node_id = random.randint(1, nodes_per_layer(layer)) # LOad balaning, random selection
        message = Message(sender=self.port, destination=node_port(layer_port(layer), 1), instruction = instruction)
        if instruction.operation == WRITE:
            self.send_message(message)
        elif instruction.operation == READ:
            self.send_message(message)


    def send_message(self, message):
        """Sends message to node with id in layer"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #print(f"{self.name}: Connecting to: {message.destination}")
            s.connect((HOST, message.destination))
            message = pickle.dumps(message)
            s.sendall(message)


    def accept_messages(self):
        """Accepts incoming messages and handles them"""
        self.socket.listen()
        while self.alive:
            conn, addr = self.socket.accept()
            with conn:
                data = conn.recv(1024)
                message = pickle.loads(data)
                if message.instruction.operation == ACK: 
                    self.ack = 1
                elif message.instruction.operation == READ_RESULT:
                    print(f"{self.name}: Received Read at [{message.instruction.position}]: {message.instruction.value}")
                elif message.instruction.operation == QUIT:
                    self.alive = False

    
    def stop(self):
        """Stops Big Brother structure and joins node threads"""
        # Stop accepting connections
        self.alive = False
        
        # Send stop message to itself to interrupt accept blocking call
        instruction = Instruction(operation=QUIT)
        message = Message(sender = self.port, destination=self.port, instruction=instruction)
        self.send_message(message)
        self.listener.join()
        
        # Close socket
        self.socket.close()

        # Stop node threads
        for node in self.nodes:
            node.stop()
        for thread in self.node_threads:
            thread.join()


    def run(self, transactions):
        """Runs transactions on the structure"""
        # Execute transactions
        for transaction in transactions:
            for instruction in transaction.instructions:
                print(f"{self.name}: Executing {instruction}")
                self.execute_instruction(transaction.layer, instruction)
                if instruction.operation == WRITE:
                    while self.ack != 1:
                        pass
                    print(f"{self.name}: Received ACK")
                    self.ack = 0