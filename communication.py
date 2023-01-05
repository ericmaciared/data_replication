import re

# Operation Constants
BEGIN  = 'b'
WRITE = 'w'
WRITE_ACK = 'wa'
ACK = 'a'
READ = 'r'
END = 'c'
QUIT = 'q'


def import_transactions(filename):
    """Imports transactions from file path and returns list of transactions in list of instructions"""
    file = open(filename, "r")
    lines = file.readlines()
    transactions = []
    
    for line in lines:
        current = Transaction()
        for instruction in line.split(', '):
            inst_targ = re.sub(r'[<>(),]', " ", instruction).strip().split(' ')
            if inst_targ[0] == BEGIN:
                if len(inst_targ) == 2:
                    current.set_layer(int(inst_targ[1]))
            elif inst_targ[0] == WRITE:
                current.add_instruction(Instruction(operation = WRITE, position = int(inst_targ[1]), value = int(inst_targ[2])))
            elif inst_targ[0] == READ:
                current.add_instruction(Instruction(operation = READ, position = int(inst_targ[1])))
            elif inst_targ[0] == END:
                transactions.append(current)
    file.close()
    
    return transactions 

### Communication Classes ###
class Message:
    def __init__(self, sender, destination, instruction = None):
        self.instruction = instruction
        self.sender = sender
        self.destination = destination


class Transaction:
    def __init__(self, layer = 1):
        self.layer = layer
        self.instructions = []

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def set_layer(self, layer):
        self.layer = layer


class Instruction:
    def __init__(self, operation, position=None, value=None):
        self.operation = operation
        self.position = position
        self.value = value

    def __str__(self):
        return f"{self.operation} ({self.position}, {self.value})"