import abc
from ports import *
import threading
import queue
import pickle
from communication import *
import socketio

class Node:
    def __init__(self, layer, id):
        self.alive = True
        self.name = f'{id_for_layer(layer)}{id}'
        self.id = id
        self.layer = layer
        self.port = node_port(self.layer, self.id)
        self.children = []
        self.updates = 0
        self.message_queue = queue.Queue() # Queue of messages to be processed
        self.update_register = queue.Queue() # Queue of updates to be sent to children

        # Initialize and connect websocket for versions
        self.sio = socketio.Client()
        self.sio.connect('http://localhost:5000')

        # Initialize node versions
        self.versions = [0] * 10
        self.log = f"logs/{self.name}.txt"
        self.write_to_log()
        
        # Initialize node socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, self.port))
        print(f"{self.name}: listening on port {self.port}")

        # Initialize listener thread for incoming messages
        self.listener = threading.Thread(target = self.accept_messages)
        self.listener.start()

        # Initialize dispatcher for queue of messages
        self.dispatcher = threading.Thread(target = self.dispatch_messages)
        self.dispatcher.start()
        

    def accept_messages(self):
        """Accepts incoming messages and adds them to the message queue"""
        self.socket.listen()
        while self.alive:
            conn, addr = self.socket.accept()
            with conn:
                data = conn.recv(1024)
                message = pickle.loads(data)
                if message.instruction.operation == ACK: # Do not queue ACK messages
                    #print(f"{self.name}: ACK Received")
                    self.ack_count += 1
                else:
                    self.message_queue.put(message)


    def dispatch_messages(self):
        """Dispatches messages from the message queue"""
        while self.alive:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                self.execute_instruction(message)
                #print(f"{self.name}: Dispatched: {str(message.instruction)}")


    def send_message(self, message):
        """Sends message to node with id in layer"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, message.destination))
            message = pickle.dumps(message)
            s.sendall(message)
 

    def send_changes(self):
        """Sends changes to children"""
        while not self.update_register.qsize() == 0:
            instruction = self.update_register.get()
            for child in self.children:
                target_port = node_port(self.layer + 1000, child)
                #print(f"{self.name}: Sending {instruction} to children at {target_port}")
                message = Message(sender=self.port, destination=target_port, instruction=instruction)
                self.send_message(message)

    @abc.abstractmethod
    def execute_instruction(self, message):
        """Executes instruction on node"""
        pass

    @abc.abstractmethod
    def run(self):
        pass


    def stop(self):
        """Stops node and joins working threads"""
        print(f"{self.name}: Stopping")
        self.alive = False

        # Stop dispatcher thread
        self.dispatcher.join()

        # Send stop message to itself to interrupt accept blocking call
        instruction = Instruction(operation=QUIT)
        message = Message(sender = self.port, destination=self.port, instruction=instruction)
        self.send_message(message)
        self.listener.join()
        
        # Close sockets
        self.socket.close()
        self.sio.disconnect() # Close websocket


    ### VERSIONS AND LOG FUNCTIONS ###
    def read_value(self, position):
        #print(f"{self.name}: Read value at position {position}: {self.versions[position]}")
        instruction = Instruction(operation=READ_RESULT, position=position, value=self.versions[position])
        message = Message(sender = self.port, destination=BIG_BROTHER_PORT, instruction=instruction)
        self.send_message(message)

    def write_value(self, position, value):
        """Writes value to node version at position"""
        self.versions[position] = value
        self.write_to_log()
        self.updates += 1
        self.update_register.put(Instruction(operation=WRITE, position=position, value=value)) # Add update to register for children

    # Write current node versions to log file
    def write_to_log(self):
        """Writes current node versions to log file"""
        file = open(self.log, "w")
        file.write(str(self.versions))
        file.close()

        #Send log to websocket
        self.sio.emit('version', (self.name, self.versions))
