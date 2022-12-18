import socket

# Ports
HOST = socket.gethostbyname(socket.gethostname())
BIG_BROTHER_PORT = 6000
CORE_PORT = 7000
L1_PORT = 8000
L2_PORT = 9000

# Message Size
DEF_MSG_SIZE = 1024

# Messages
READ = "READ"
WRITE = "WRITE"
BEGIN = "BEGIN"
CLOSE = "CLOSE"

READ_ACK = "READ_ACK"
WRITE_ACK = "WRITE_ACK"
BEGIN_ACK = "BEGIN_ACK"