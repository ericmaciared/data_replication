import socket
import time
import threading
from abc import abstractmethod
import re
from ports import *
import asyncio
import websockets

class Node:
    # Core layer nodes use update everywhere, active, and eager replication to replicate data
    def __init__(self, host, id, layer):

        # Boolean to kill the process
        self.is_alive = True

        self.id = id
        self.host = host

        self.bigBrotherThread = None
        self.bigBrotherSocket = None
        self.bigBrotherTalking = False

        # Web Socket
        #TODO: Set WEBSOCKET connection
        #self.webSocket = websockets.connect("ws://localhost:8765")

        # Override in subclasses' constructor methods
        self.receive_peers = None
        self.send_peers = None
        self.layerPort = None
        self.layer = layer
        self.port = id

        # Set portLayer depending on Layer
        if layer == CORE_LAYER: self.layerPort = CORE_PORT
        elif layer == L1_LAYER: self.layerPort = L1_PORT
        else: self.layerPort = L2_PORT

        self.port += self.layerPort
        
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

    # Function to call to enable big brother connection to this node
    def connect_to_big_bro(self):
        self.bigBrotherTalking = True
        self.bigBrotherSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bigBrotherSocket.connect((HOST, BIG_BROTHER_PORT))
        self.bigBrotherThread = threading.Thread(target=self.receive_from_peer, args=(self.bigBrotherSocket, self.bigBrotherSocket))
        self.bigBrotherThread.name = "BIGBRO THREAD"
        self.bigBrotherThread.start()
        print("BIG BRO CONNECTED")

    # Add child nodes to connect to
    def add_child(self, child):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = child + self.layerPort + CHILD_OFFSET
        sock.connect((HOST, port))
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

        #TODO:Send to websocket
        #message = self.layer + '\n' + str(self.layerPort) + '\n' + str(self.id) + '\n' + str(self.versions)
        #self.webSocket.send(message)

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

    def close_children(self):
        message = str(self.id) + '\n' + CLOSE
        for child in self.children:
            self.msg_queue.append(message)
            self.dest_queue.append(child)
        while self.msg_queue:
            time.sleep(0.3)
        for child in self.children:
            child.close()
        self.children.clear()

    @abstractmethod
    def process_message(self, message, bigBrother=None):
        message = message.decode().split('\n')
        if message != ['']:
            print(self.layer, self.id, "received message", message)
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
                self.update_values(message[2])
                reply = str(self.id) + '\n' + UPDATE_ACK + '\n' + str(self.versions)

            elif instruction == BEGIN:
                print("ERROR SENDING BEGIN TO CORE NODE")
                self.is_alive = False
                exit()

            elif instruction == CLOSE:
                self.close()

            self.process_instruction(instruction, sender, reply, position, value, bigBrother)

    @abstractmethod
    def process_instruction(self, instruction, sender, reply, position, value, bigBrother):
        pass

    def update_values(self, arrayString):
        arrayString = re.sub(r'[<>()\[\]]', "", arrayString)
        for i, value in enumerate(arrayString.split(",")):
            self.versions[i] = int(value)
        self.write_to_log()

    def close(self):
        self.is_alive = False
        self.close_children()
        self.socket.close()




