import random
import socket
import threading
import time
import queue
import logging
from message import Message

class VirtualMachine:
    def __init__(self, machine_id, num_machines, port_base=9000):
        self.machine_id = machine_id
        self.num_machines = num_machines
        self.logical_clock = 0
        
        # Determine clock rate (1-6 ticks per second)
        self.clock_rate = random.randint(1, 6)
        self.cycle_time = 1.0 / self.clock_rate
        
        # Set up message queue
        self.message_queue = queue.Queue()
        
        # Set up networking
        self.port = port_base + machine_id
        self.peers = []
        for i in range(num_machines):
            if i != machine_id:
                self.peers.append(port_base + i)
        
        # Set up logging
        log_filename = f"machine_{machine_id}.log"
        self.logger = logging.getLogger(f"Machine-{machine_id}")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_filename, mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        self.logger.addHandler(handler)
        
        
        # Set up socket for receiving messages
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', self.port))
        self.server_socket.listen(5)
        
        # Flag to control the machine's execution
        self.running = False
        
        # Log initialization
        print(f"Machine {machine_id} initialized with clock rate: {self.clock_rate} ticks/second")
        self.logger.info(f"Machine initialized with clock rate: {self.clock_rate} ticks/second")
    
    def start(self):
        """Start the virtual machine's operation"""
        self.running = True
        
        # Start listener thread for incoming connections
        listener_thread = threading.Thread(target=self._listen_for_connections)
        listener_thread.daemon = True
        listener_thread.start()
        
        # Give time for all machines to start up
        time.sleep(2)
        
        # Start the main clock cycle
        self._run_clock_cycle()
    
    def stop(self):
        """Stop the virtual machine's operation"""
        self.running = False
        self.server_socket.close()
    
    def _listen_for_connections(self):
        """Listen for incoming connections from other machines"""
        while self.running:
            try:
                client_socket, _ = self.server_socket.accept()
                handler = threading.Thread(target=self._handle_client, args=(client_socket,))
                handler.daemon = True
                handler.start()
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket):
        """Handle messages from a connected client"""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Process the received message
                message = Message.from_json(data.decode())
                self.message_queue.put(message)
        except Exception as e:
            if self.running:
                self.logger.error(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def _send_message(self, peer_port, message):
        """Send a message to a peer machine"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', peer_port))
            client_socket.sendall(message.to_json().encode())
            client_socket.close()
        except Exception as e:
            self.logger.error(f"Error sending message to port {peer_port}: {e}")
    
    def _run_clock_cycle(self):
        """Run the main clock cycle of the virtual machine"""
        while self.running:
            cycle_start = time.time()
            
            # Process a message if available
            if not self.message_queue.empty():
                message = self.message_queue.get()
                
                # Update logical clock according to Lamport's rule
                self.logical_clock = max(self.logical_clock, message.logical_clock) + 1
                
                # Log the message receipt
                queue_length = self.message_queue.qsize()
                self.logger.info(
                    f"Received message from Machine {message.sender_id}, " +
                    f"Queue length: {queue_length}, " +
                    f"Logical clock: {self.logical_clock}"
                )
            else:
                # No message to process, generate random action
                action = random.randint(1, 10)
                
                if 1 <= action <= 3:
                    # Send message to other machines
                    self.logical_clock += 1
                    message = Message(self.machine_id, self.logical_clock)
                    
                    if action == 1:
                        # Send to one random machine
                        target = random.choice(self.peers)
                        self._send_message(target, message)
                        target_id = target - (self.port - self.machine_id)
                        self.logger.info(
                            f"Sent message to Machine {target_id}, " +
                            f"Logical clock: {self.logical_clock}"
                        )
                    
                    elif action == 2:
                        # Send to another random machine (different from action 1)
                        target = random.choice(self.peers)
                        self._send_message(target, message)
                        target_id = target - (self.port - self.machine_id)
                        self.logger.info(
                            f"Sent message to Machine {target_id}, " +
                            f"Logical clock: {self.logical_clock}"
                        )
                    
                    elif action == 3:
                        # Send to all other machines
                        for peer in self.peers:
                            self._send_message(peer, message)
                        self.logger.info(
                            f"Sent message to ALL other machines, " +
                            f"Logical clock: {self.logical_clock}"
                        )
                
                else:
                    # Internal event
                    self.logical_clock += 1
                    self.logger.info(
                        f"Internal event, " +
                        f"Logical clock: {self.logical_clock}"
                    )
            
            # Calculate sleep time to maintain clock rate
            elapsed = time.time() - cycle_start
            sleep_time = max(0, self.cycle_time - elapsed)
            time.sleep(sleep_time) 