import time
import threading
import json
from virtual_machine import VirtualMachine

def main():
    # Number of virtual machines to create
    num_machines = 3
    
    # Create and start the virtual machines
    machines = []
    threads = []

    # parse config.json
    with open('config.json', 'r') as f:
        config = json.load(f)
    host = config['host']
    port_base = config['port_base']

    
    for i in range(num_machines):
        vm = VirtualMachine(i, num_machines, host, port_base)
        machines.append(vm)
        
        thread = threading.Thread(target=vm.start)
        threads.append(thread)
    
    # Start all machine threads
    for thread in threads:
        thread.start()
    
    try:
        # Let the simulation run for a specified time
        simulation_time = 60  # seconds
        print(f"Simulation running for {simulation_time} seconds...")
        time.sleep(simulation_time)
    except KeyboardInterrupt:
        print("Simulation interrupted by user")
    finally:
        # Stop all machines
        for vm in machines:
            vm.stop()
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        print("Simulation completed")

if __name__ == "__main__":
    main() 