import unittest
import threading
import time
from virtual_machine import VirtualMachine
from message import Message

class TestVirtualMachine(unittest.TestCase):
    def setUp(self):
        """Set up the test environment"""
        self.host = 'localhost'
        self.port_base = 9000
        self.num_machines = 3
        self.machines = []
        self.threads = []

        # Create virtual machines
        for i in range(self.num_machines):
            vm = VirtualMachine(i, self.num_machines, self.host, self.port_base)
            self.machines.append(vm)

    def tearDown(self):
        """Clean up the test environment"""
        for vm in self.machines:
            vm.stop()
        for thread in self.threads:
            thread.join()

    def test_initialization(self):
        """Test the initialization of virtual machines"""
        for i, vm in enumerate(self.machines):
            self.assertEqual(vm.machine_id, i)
            self.assertEqual(vm.num_machines, self.num_machines)
            self.assertEqual(vm.host, self.host)
            self.assertEqual(vm.port, self.port_base + i)
            self.assertTrue(vm.logger)
            self.assertTrue(vm.server_socket)

    def test_start_stop(self):
        """Test starting and stopping virtual machines"""
        for vm in self.machines:
            thread = threading.Thread(target=vm.start)
            self.threads.append(thread)
            thread.start()
            time.sleep(1)  # Give some time for the machine to start
            self.assertTrue(vm.running)
            vm.stop()
            thread.join()
            self.assertFalse(vm.running)

    def test_message_sending(self):
        """Test sending and receiving messages between virtual machines"""
        sender = self.machines[0]
        receiver = self.machines[1]

        sender_thread = threading.Thread(target=sender.start)
        receiver_thread = threading.Thread(target=receiver.start)
        self.threads.extend([sender_thread, receiver_thread])

        sender_thread.start()
        receiver_thread.start()

        # wait for machines to start
        time.sleep(2)
        sender_time = sender.logical_clock
        message = Message(sender.machine_id, sender_time)
        sender._send_message(receiver.port, message)

         # stop the sender (no more sends)
        sender.stop()
        sender_thread.join()

        # wait for message to be received
        time.sleep(1)

        # test message received
        self.assertIsNotNone(receiver.last_received_message)
        # test message is correct
        self.assertEqual(receiver.last_received_message.sender_id, sender.machine_id)
        self.assertEqual(receiver.last_received_message.logical_clock, sender_time)
        # test update invariant (max of current clock, received clock)
        self.assertGreaterEqual(receiver.logical_clock, receiver.last_received_message.logical_clock)
        self.assertGreaterEqual(receiver.logical_clock, sender_time)

        sender.stop()
        receiver.stop()

if __name__ == "__main__":
    unittest.main()