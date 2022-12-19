import socket
import time
import threading
from abc import abstractmethod
import re
from ports import *

class Node:
    # Core layer nodes use update everywhere, active, and eager replication to replicate data
    def __init__(self, host, id, layer):
        
        # Boolean to kill the process
        self.is_alive = True

        self.id = id
        self.host = host

        # Override in subclasses' constructor methods
        self.receive_peers = None
        self.send_peers = None
        self.layerPort = None
        self.layer = layer
        self.port = id

        # Set port depending on Layer
        if layer == CORE_LAYER: self.port += CORE_PORT
        elif layer == L1_LAYER: self.port += L1_PORT
        else: self.port += L2_PORT
        
        # Init versions of file (Array of 10 ints)
        self.versions = [0] * 10

        # Lists/Queues for sending
        self.msg_queue = []
        self.dest_queue = []
        self.children = []
        
        # Init log file
        self.log = f"logs/{self.layer}{self.id}.txt"
        self.write_to_log('w')

        # Bind socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    @abstractmethod
    def run(self):
        pass

    # Add child nodes to connect to
    def add_child(self, child):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, child + self.layerPort))
        self.children.append(sock)
        print(self.layer, "Node", self.id, "connected to child", child)

    def write_value(self, position, value):
        self.versions[position] = value
        self.write_to_log()

    def write_to_log(self, mode='a'):
        # By default open file in append mode, although write-overwrite is used to init the file
        file = open(self.log, mode)
        if mode == 'a': file.write('\n')
        file.write(str(self.versions))
        file.close()

    def receive_from_peer(self, s, bigBrother = None):
        while self.is_alive:
            self.process_message(s.recv(DEF_MSG_SIZE), bigBrother)

    def send_to_peer(self, s, message):
        s.sendall(message.encode())
        #print(self.id, "sent ", message, "to ", s)

    def update_children(self):
        message = str(self.id) + '\n' + UPDATE + '\n' + str(self.versions)
        for child in self.children:
            self.msg_queue.append(message)
            self.dest_queue.append(child)

    @abstractmethod
    def process_message(self, message, bigBrother=None):
        message = message.decode().split('\n')
        print(self.id, "received message", message)
        reply = None
        # Message: SenderID + Instruction + Value1 + Value2

        sender = int(message[0])
        instruction = message[1]
        position = None
        value = None

        if instruction == READ:
            position = int(message[2])
            value = self.versions[position]
            reply = str(self.id) + '\n' + READ_ACK + '\n' + str(self.versions[position])

        elif instruction == WRITE:
            position = int(message[2])
            value = int(message[3])
            self.write_value(position, value)
            reply = str(self.id) + '\n' + WRITE_ACK + '\n' + str(self.versions[position])

        elif instruction == UPDATE:
            arrayString = re.sub(r'[<>()]', "", message[2])
            for i, value in enumerate(arrayString.split(",")):
                self.write_value(i, value)

            reply = str(self.id) + '\n' + UPDATE_ACK + '\n' + str(self.versions)

        elif instruction == BEGIN:
            print("ERROR SENDING BEGIN TO CORE NODE")
            self.is_alive = False
            exit()

        elif instruction == CLOSE:
            self.is_alive = False

        self.process_instruction(instruction, sender, reply, position, value, bigBrother)

    @abstractmethod
    def process_instruction(self, instruction, sender, reply, position, value, bigBrother):
        pass








