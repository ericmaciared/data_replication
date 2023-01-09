import socket

# Networking constants
HOST = socket.gethostbyname(socket.gethostname())
BIG_BROTHER_PORT = 6000
CORE_LAYER_PORT = 7000
L1_LAYER_PORT = 8000
L2_LAYER_PORT = 9000

CORE_NODES = 3
L1_NODES = 2
L2_NODES = 2


def node_port(layer, id):
    """Returns port for node with id in layer"""
    return layer + id

def layer_port(layer):
    return layer * 1000 + BIG_BROTHER_PORT

def nodes_per_layer(layer):
    if layer == 1:
        return CORE_NODES
    elif layer == 2:
        return L1_NODES
    elif layer == 3:
        return L2_NODES
    else:
        return 1

def id_by_port(port):
    if port == BIG_BROTHER_PORT:
        return "Big Brother"
    elif port == CORE_LAYER_PORT:
        return f'A{port-CORE_LAYER_PORT}'
    elif port == L1_LAYER_PORT:
        return f'B{port-L1_LAYER_PORT}'
    elif port == L2_LAYER_PORT:
        return f'C{port-L2_LAYER_PORT}'
    else:
        return None

def id_for_layer(layer):
    if layer == 0 or layer == BIG_BROTHER_PORT:
        return 0
    elif layer == 1 or layer == CORE_LAYER_PORT:
        return 'A'
    elif layer == 2 or layer == L1_LAYER_PORT:
        return 'B'
    elif layer == 3 or layer == L2_LAYER_PORT:
        return 'C'
    else:
        return None

