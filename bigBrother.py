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
global s
global nodes
global node_threads

def accept_connections(sock):
    global conn
    print("BIG BROTHER LISTENING")
    conn, addr = sock.accept()
    print("BIG BRO CONNECTED")

def perform_instruction(instruction):
    global conn
    global s
    global nodes

    if type(instruction) is list: inst = instruction.pop(0)
    else: inst = instruction

    if inst == INIT_INST:

        threadAccept = threading.Thread(target=accept_connections, args=(s,))
        threadAccept.name = "AcceptO"
        threadAccept.start()

        contactNode = None
        nodeType = None
        if instruction is []: contactNode = int(instruction.pop(0))
        if contactNode is None or contactNode == 0:
            nodeType = CoreNode
        elif contactNode == 1:
            nodeType = Layer1Node
        elif contactNode == 2:
            nodeType = Layer2Node
        else:
            print("CONTACT NODE ERROR")

        for node in nodes:
            if type(node) is nodeType and node.id == 1:
                node.connect_to_big_bro()

        threadAccept.join()

    elif inst == READ_INST:
        position = instruction.pop(0)
        #print("ASK READ", position)
        message = str(0) + '\n' + READ + '\n' + str(position)
        conn.sendall(message.encode())
        print("BB Received:", conn.recv(DEF_MSG_SIZE).decode().replace('\n', ', '))

    elif inst == WRITE_INST:
        position = instruction.pop(0)
        value = instruction.pop(0)
        #print("ASK WRITE", position, "AT VAL", value)
        message = str(0) + '\n' + WRITE + '\n' + str(position) + '\n' + str(value)
        conn.sendall(message.encode())
        print("BB Received:", conn.recv(DEF_MSG_SIZE).decode().replace('\n', ', '))

    elif inst == CLOSE_INST:
        print("ASK CLOSE")
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


def init_structure():
    global nodes
    global node_threads
    nodes = []
    node_threads = []

    print("Initializing Structure")

    # Core Layer (sets)
    nodes.append(CoreNode(HOST, id = 1, peers = [2, 3]))
    nodes.append(CoreNode(HOST, id = 2, peers = [1, 3]))
    nodes.append(CoreNode(HOST, id = 3, peers = [1, 2]))

    # Layer 1 (B1 -> A2, B2 > A3)
    nodes.append(Layer1Node(HOST, id = 1, parentId = 2))
    nodes.append(Layer1Node(HOST, id = 2, parentId = 3))

    # Layer 2 (C1 -> B2, C2 -> B2)
    nodes.append(Layer2Node(HOST, id = 1, parentId = 2))
    nodes.append(Layer2Node(HOST, id = 2, parentId = 2))

    for node in nodes:
        t = threading.Thread(target= node.run)
        pid = node.layer + str(node.id)
        t.name = pid
        node_threads.append(t)

    for t in node_threads:
        t.start()

    for n in nodes:
        if type(n) is Layer1Node:
            for m in nodes:
                if type(m) is CoreNode:
                    if m.id == n.parentId:
                        m.add_child(n.id)

    for n in nodes:
        if type(n) is Layer2Node:
            for m in nodes:
                if type(m) is Layer1Node:
                    if m.id == n.parentId:
                        m.add_child(n.id)
        

# Big Brother is the main class that initializes the network and starts the threads, oversees the network
# and handles the communication with the web server
def close_all_nodes():
    threadAccept = threading.Thread(target=accept_connections, args=(s,))
    threadAccept.name = "AcceptC"
    threadAccept.start()

    for node in nodes:
        if type(node) is CoreNode and node.id == 1:
            node.connect_to_big_bro()

    threadAccept.join()
    message = str(0) + '\n' + CLOSE
    conn.sendall(message.encode())
    conn.close()

def main():
    global conn
    global s

    # Initialize the node structure
    init_structure()

    # Start socket for overseeing connections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, BIG_BROTHER_PORT))
    s.listen()

    # Read transactions file
    transactions = import_transactions()
    for transaction in transactions:
        for instruction in transaction: perform_instruction(instruction)

    close_all_nodes()

    print(len(node_threads))

    for t in node_threads:
        t.join()
    print("ALL THREADS JOINED")

    #for thread in threading.enumerate():
    #    print(thread.name)

    exit()


if __name__ == '__main__': 
    main()