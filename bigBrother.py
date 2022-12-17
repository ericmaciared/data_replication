import socket
import threading
from coreNode import CoreNode
from layer1node import Layer1Node
from layer2node import Layer2Node
from ports import *

def initStructure():
    nodes = []
    node_threads = []

    # Core Layer (sets)
    nodes.append(CoreNode(HOST, id = 1, peers = [2, 3]))
    nodes.append(CoreNode(HOST, id = 2, peers = [1, 3]))
    nodes.append(CoreNode(HOST, id = 3, peers = [1, 2]))

    # Layer 1 (B1 -> A2, B2 > A3)
    nodes.append(Layer1Node(HOST, id = 1, parentId = 2))
    nodes.append(Layer1Node(HOST, id = 2, parentId = 3 ))

    # Layer 2 (C1 -> B2, C2 -> B2)
    nodes.append(Layer2Node(HOST, id = 1, parentId = 2))
    nodes.append(Layer2Node(HOST, id = 2, parentId = 2))

    for node in nodes:
        node_threads.append(threading.Thread(target= node.run()))
    
    for thread in node_threads:
        thread.start()

    for thread in node_threads:
        thread.join()
        

# Big Brother is the main class that initializes the network and starts the threads, oversees the network
# and handles the communication with the web server
def main():
    # Initialize the node structure
    thread = threading.Thread(target = initStructure())
    thread.start()

    # Start socket for overseeing connections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    # Wait for node connections
    

    # Join threads terminating node structure
    thread.join()


if __name__ == '__main__': 
    main()