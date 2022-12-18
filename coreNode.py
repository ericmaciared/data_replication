import socket
import time
import threading
from ports import *

class CoreNode:
    # Core layer nodes use update everywhere, active, and eager replication to replicate data
    def __init__(self, host, id, peers):

        self.lock = threading.Lock()

        # Boolean to kill the process
        self.is_alive = True

        self.id = id
        self.receive_peers = []
        self.host = host
        self.port = id + CORE_PORT
        
        # Init versions of file (Array of 10 ints)
        self.versions = [0] * 10

        # Number of ACKs after a write
        self.num_acks = 0
        self.msg_queue = []
        
        # Init log file
        self.log = f"logs/A{id}.txt"
        file = open(self.log, "w")
        file.write(str(self.versions))
        file.close()

        # Bind socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

        # Accept all incoming and connect to outgoing ports
        thread_peers = threading.Thread(target=self.accept_peers(peers))
        self.send_peers = self.connect_to_peers(peers)

        thread_peers.join()

        while len(self.receive_peers) < len(peers):
            time.sleep(0.1)

        # Core node #1 will always be listening to the instructions provided by Big Brother
        if id ==1:
            threading.Thread(target=self.talk_to_big_brother())

        while self.is_alive:
            if len(self.msg_queue) != 0:
                task = self.msg_queue.remove(0)
                s = task[0]
                msg = task[1]
                s.send(msg.encode())

    # Connect outgoing connections to peers
    def connect_to_peers(self, nodes):
        array_send_conn = []
        for node in nodes:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port = node + CORE_PORT
            sock.connect((HOST, port))

            # Store Sockets in array position for comfort
            array_send_conn[node] = sock

        return array_send_conn

    # Accept all incoming connections
    def accept_peers(self, nodes):
        array_received_conn = []
        self.socket.listen(len(nodes))
        while len(array_received_conn) < len(nodes):
            conn, addr = self.socket.accept()
            array_received_conn.append(conn)

        self.receive_peers = array_received_conn

    # Communication to Big Brother (Clients connected to Core)
    def talk_to_big_brother(self):
        while self.is_alive:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, BIG_BROTHER_PORT))

            self.process_message(sock.recv(DEF_MSG_SIZE), sock)

    def receive_from_peer(self, s):
        while self.is_alive:
            self.process_message(s.recv(DEF_MSG_SIZE), s)

    def process_message(self, message, bigBrother=None):
        message = message.decode().split('\n')
        reply = None
        # Message: SenderID + Instruction + Value1 + Value2

        sender = int(message[0])
        instruction = message[1]
        writePosition = None
        value = None

        if instruction == READ:
            readPosition = int(message[2])
            value = self.versions[readPosition]
            reply = str(self.id) + '\n' + READ_ACK + '\n' + str(self.versions[value])

        elif instruction == WRITE:
            writePosition = int(message[2])
            value = int(message[3])
            self.versions[writePosition] = value
            reply = str(self.id) + '\n' + WRITE_ACK + '\n' + str(self.versions[value])

        elif instruction == BEGIN:
            print("ERROR SENDING BEGIN TO CORE NODE")
            exit()

        elif instruction == CLOSE:
            exit()

        # By default do nothing with ACKs

        if reply is not None:
            if bigBrother is not None:

                # If received a WRITE from client we need to replicate the information to other cores
                if instruction == WRITE:
                    with self.lock:
                        for conn in self.send_peers:
                            writeFwd = str(self.id) + '\n' + WRITE + '\n' + str(writePosition) + '\n' + str(value)
                            self.msg_queue.append([conn, writeFwd])

                self.msg_queue.append([bigBrother , reply])

            else :
                s = self.send_peers[sender]
                self.msg_queue.append([s, reply])






