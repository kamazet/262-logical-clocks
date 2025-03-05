import time
import json
import multiprocessing
from virtual_machine import VirtualMachine

def start_virtual_machine(machine_id, num_machines, host, port_base):
    vm = VirtualMachine(machine_id, num_machines, host, port_base)
    vm.start()

def main():
    # Number of virtual machines to create
    num_machines = 3
    
    # Create and start the virtual machines
    processes = []

    # parse config.json
    with open('config.json', 'r') as f:
        config = json.load(f)
    host = config['host']
    port_base = config['port_base']

    for i in range(num_machines):
        process = multiprocessing.Process(target=start_virtual_machine, args=(i, num_machines, host, port_base))
        processes.append(process)
    
    # Start all machine processes
    for process in processes:
        process.start()
    
    try:
        # Let the simulation run for a specified time
        simulation_time = 60  # seconds
        print(f"Simulation running for {simulation_time} seconds...")
        time.sleep(simulation_time)
    except KeyboardInterrupt:
        print("Simulation interrupted by user")
    finally:
        # Stop all machines
        for process in processes:
            process.terminate()
        
        # Wait for all processes to finish
        for process in processes:
            process.join()
        
        print("Simulation completed")

if __name__ == "__main__":
    main()