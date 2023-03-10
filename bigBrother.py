import socket
import threading
import time

from coreNode import CoreNode
from layer1node import Layer1Node
from layer2node import Layer2Node
from ports import *
import re

INIT_INST = 'b'
READ_INST = 'r'
WRITE_INST = 'w'
CLOSE_INST = 'c'

TRANSACTIONS = "transactions.txt"

global conn
global thread

def perform_instruction(instruction):
    global conn
    global thread

    if type(instruction) is list: inst = instruction.pop(0)
    else: inst = instruction

    if inst == INIT_INST:
        contactNode = None
        if instruction is []: contactNode = int(instruction.pop(0))

        # Initialize the node structure
        thread = threading.Thread(target=init_structure, args=(contactNode,))
        thread.start()

        # Start socket for overseeing connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, BIG_BROTHER_PORT))
            s.listen()
            print("BIG BROTHER LISTENING")
            conn, addr = s.accept()

    elif inst == READ_INST:
        position = instruction.pop(0)
        print("ASK READ", position)
        message = str(0) + '\n' + READ + '\n' + str(position)
        conn.sendall(message.encode())
        print("BB Received:", conn.recv(DEF_MSG_SIZE).decode())

    elif inst == WRITE_INST:
        position = instruction.pop(0)
        value = instruction.pop(0)
        print("ASK WRITE", position, "AT VAL", value)
        message = str(0) + '\n' + WRITE + '\n' + str(position) + '\n' + str(value)
        conn.sendall(message.encode())
        print("BB Received:", conn.recv(DEF_MSG_SIZE).decode())

    elif inst == CLOSE_INST:
        print("ASK CLOSE")
        message = str(0) + '\n' + CLOSE
        conn.sendall(message.encode())
        conn.close()
        conn = None

# Method to read file
def import_transactions():
    file = open(TRANSACTIONS)
    file_data = file.read()
    file_lines = file_data.splitlines()
    transactions = []
    for line in file_lines:
        instructions = []
        for instruction in line.split(', '):
            inst_targ = re.sub(r'[<>(),]', " ", instruction).strip().split(' ')
            if len(inst_targ) > 2:
                instructions.append([inst_targ[0], inst_targ[1], inst_targ[2]])
            elif len(inst_targ) > 1:
                instructions.append([inst_targ[0], inst_targ[1]])
            else : instructions.append(inst_targ[0])
        transactions.append(instructions)
    print(transactions)
    return transactions


def init_structure(readNode=None):
    nodes = []
    node_threads = []

    print("Initializing Structure")

    # Core Layer (sets)
    nodes.append(CoreNode(HOST, id = 1, peers = [2, 3], bigBrotherTalking = (readNode is None or readNode == 0)))
    nodes.append(CoreNode(HOST, id = 2, peers = [1, 3], bigBrotherTalking = False))
    nodes.append(CoreNode(HOST, id = 3, peers = [1, 2], bigBrotherTalking = False))

    # Layer 1 (B1 -> A2, B2 > A3)
    nodes.append(Layer1Node(HOST, id = 1, parentId = 2, bigBrotherTalking = (readNode == 1)))
    nodes.append(Layer1Node(HOST, id = 2, parentId = 3, bigBrotherTalking = False))

    # Layer 2 (C1 -> B2, C2 -> B2)
    nodes.append(Layer2Node(HOST, id = 1, parentId = 2, bigBrotherTalking = (readNode == 2)))
    nodes.append(Layer2Node(HOST, id = 2, parentId = 2, bigBrotherTalking = False))

    for node in nodes:
        node_threads.append(threading.Thread(target= node.run))

    for thread in node_threads:
        thread.start()

    for n in nodes:
        if type(n) is Layer1Node:
            for m in nodes:
                if type(m) is CoreNode:
                    if m.id == n.parentId:
                        m.add_child(n.id)
    print("AJ")

    for n in nodes:
        if type(n) is Layer2Node:
            for m in nodes:
                if type(m) is Layer1Node:
                    if m.id == n.parentId:
                        m.add_child(n.id)

    for t in node_threads:
        t.join()
        

# Big Brother is the main class that initializes the network and starts the threads, oversees the network
# and handles the communication with the web server
def main():
    # Read transactions file
    transactions = import_transactions()
    for transaction in transactions:
        for instruction in transaction: perform_instruction(instruction)
        # Join init thread terminating node structure
        thread.join()


if __name__ == '__main__': 
    main()