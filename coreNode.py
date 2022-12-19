import time
import threading
from abc import ABC

from node import Node
from ports import *

class CoreNode(Node, ABC):
    # Core layer nodes use update everywhere, active, and eager replication to replicate data
    def __init__(self, host, id, peers):
        Node.__init__(self, host, id, CORE_LAYER)
        print("Initializing Core Node", id)

        # Lock
        self.lock = threading.Lock()

        self.id = id
        # Placeholder to connect peers at beginning of runtime
        self.peers = peers

        self.receive_peers = [NUM_CORES]
        self.send_peers = [NUM_CORES]

        # Values to operate with Data Replication
        self.num_acks = 0
        self.num_updates = 0

    def run(self):
        # Accept all incoming and connect to outgoing ports
        thread_peers = threading.Thread(target=self.accept_peers, args=(self.peers, ))
        thread_peers.start()

        time.sleep(0.5)
        self.send_peers = self.connect_to_peers(self.peers)

        # Wait for all receive peers to be set up
        thread_peers.join()
        if len(self.receive_peers) < len(self.peers):
            print("NOT ENOUGH RECEIVE PEERS SET UP")

        # Start a thread for each connection to receive info from
        rcv_threads = []
        for s in self.receive_peers:
            rcv = threading.Thread(target=self.receive_from_peer, args=(s,))
            rcv_threads.append(rcv)
            rcv.start()

        print("Core Node", self.id, " received all peer connections")

        # Core node #1 will always be listening to the instructions provided by Big Brother
        bigBrotherThread = None
        if self.id == 1:
            print("BIG BRO TALKING")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, BIG_BROTHER_PORT))
            bigBrotherThread = threading.Thread(target=self.receive_from_peer, args=(sock,sock))
            bigBrotherThread.start()

        # While alive dispatch outgoing messages
        while self.is_alive or self.msg_queue:
            time.sleep(0.1)
            if self.msg_queue and self.dest_queue:
                self.send_to_peer(self.dest_queue.pop(0), self.msg_queue.pop(0))

            # If there are more than 10 updates, forward to the next layer
            if self.num_updates >= 10:
                self.num_updates =0
                self.update_children()

        # Program Closing
        for thread in rcv_threads:
            thread.join()
        if bigBrotherThread is not None: bigBrotherThread.join()


    # Connect outgoing connections to peers
    def connect_to_peers(self, nodes):
        print("Connecting to Peers!")
        array_send_conn = [None] * NUM_CORES
        for node in nodes:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port = node + CORE_PORT
            sock.connect((HOST, port))

            # Store Sockets in array position for comfort
            array_send_conn[node -1] = sock

        return array_send_conn


    # Override function to count updates
    def write_value(self, position, value):
        super().write_value(position, value)
        self.num_updates += 1
        print("hey, # of updates is", self.num_updates)

    # Accept all incoming connections
    def accept_peers(self, nodes):
        print("Accepting Peers!")
        array_received_conn = []
        self.socket.listen(len(nodes))
        while len(array_received_conn) < NUM_CORES-1:
            conn, addr = self.socket.accept()
            # print("CORE NODE", self.id, "accepted ", addr)
            array_received_conn.append(conn)

        self.receive_peers = array_received_conn


    def process_instruction(self, instruction, sender, reply, position, value, bigBrother=None):
        if instruction == WRITE_ACK: self.num_acks += 1
        if bigBrother is not None:

            # If received a WRITE from client we need to replicate the information to other cores
            if instruction == WRITE:
                #with self.lock:
                for conn in self.send_peers:
                    if conn is not None:
                        writeFwd = str(self.id) + '\n' + WRITE + '\n' + str(position) + '\n' + str(value)
                        self.msg_queue.append(writeFwd)
                        self.dest_queue.append(conn)
                # Wait for all nodes to respond
                while self.num_acks < NUM_CORES - 1 :
                    time.sleep(0.5)
                    print(self.num_acks)
                print("ACKS Received!: ", self.num_acks)
                self.num_acks = 0

            if instruction == CLOSE:
                writeFwd = str(self.id) + '\n' + CLOSE
                for conn in self.send_peers:
                    if conn is not None:
                        self.msg_queue.append(writeFwd)
                        self.dest_queue.append(conn)
                for child in self.children:
                    self.msg_queue.append(writeFwd)
                    self.dest_queue.append(child)
            if reply is not None:
                self.msg_queue.append(reply)
                self.dest_queue.append(bigBrother)
        elif reply is not None:
            s = self.send_peers[sender-1]
            self.msg_queue.append(reply)
            self.dest_queue.append(s)






