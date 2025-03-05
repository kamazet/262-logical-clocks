# Distributed System Simulation with Logical Clocks

This project implements a simulation of an asynchronous distributed system with multiple virtual machines running at different speeds, each maintaining its own logical clock. The system demonstrates concepts like Lamport's logical clocks, message passing, and asynchronous communication.

## Project Structure 
.  
├── README.md  
├── analyze_logs.py  
├── config.json  
├── main.py  
├── message.py  
├── message_tests.py  
├── run{n} (n is the run number and specifications of the trial)  
│&emsp;├── logical_clock.txt  
│&emsp;├── machine_0.log  
│&emsp;├── machine_1.log  
│&emsp;├── machine_2.log  
│&emsp;└── queue_length.txt  
├── virtual_machine.py  
└── virtual_machine_tests.py  


## Components

### Virtual Machine (`virtual_machine.py`)
- Implements a virtual machine that runs at a randomly assigned clock rate (1-6 ticks/second)
- Maintains a logical clock and message queue
- Connects to other machines via sockets
- Logs all events with timestamps
- Performs operations based on clock cycles:
  - Process messages from queue
  - Generate random events (internal events or message sending)
  - Update logical clock according to Lamport's rules

### Message System (`message.py`)
- Defines the Message class for inter-machine communication
- Includes:
  - Sender ID
  - Logical clock value
  - Timestamp
- Provides JSON serialization/deserialization

### Main Script (`main.py`)
- Creates and initializes multiple virtual machines
- Manages simulation lifecycle
- Runs the simulation for a specified duration
- Handles graceful shutdown

### Log Analysis (`analyze_logs.py`)
- Processes log files from simulation runs
- Extracts and organizes:
  - Logical clock values
  - Message queue lengths
- Creates formatted output files:
  - `logical_clock.txt`: Tracks logical clock progression
  - `queue_length.txt`: Monitors message queue sizes

## Usage

### Running the Simulation
```
bash
python main.py
```

This will:
1. Create 3 virtual machines with random clock rates
2. Run the simulation for 60 seconds
3. Generate log files for each machine

### Analyzing the Logs
```
bash
python analyze_logs.py <run_folder>
```

Example:
bash
python analyze_logs.py run1


This generates two analysis files:
- `logical_clock.txt`: Shows logical clock values for each machine over time
- `queue_length.txt`: Shows message queue lengths for each machine over time

## Log File Formats

### Machine Logs
Each machine generates a log file with entries like:
2025-02-28 13:30:58 - Machine initialized with clock rate: 5 ticks/second
2025-02-28 13:31:00 - Sent message to Machine 1, Logical clock: 1
2025-02-28 13:31:01 - Received message from Machine 0, Queue length: 2, Logical clock: 3


### Analysis Files
The analysis script generates formatted tables:
Timestamp | Machine 0 (5 ticks/s) | Machine 1 (2 ticks/s) | Machine 2 (1 ticks/s)
----------------------------------------------------------------------------
13:30:58 | 1 | 1 | 1
13:31:00 | 2 | 2 | 2


## System Behavior

1. **Clock Rates**: Each machine runs at a random speed (1-6 ticks/second)
2. **Message Passing**: Machines communicate via TCP sockets
3. **Event Types**:
   - Internal events (increment logical clock)
   - Send message to one machine
   - Send message to all machines
4. **Logical Clock Updates**:
   - Increment on internal events
   - Increment on send messages
   - Set to max(local, received) + 1 on message receipt

## Implementation Details

### Virtual Machine Operation
- Each machine operates independently in its own thread
- Clock rate determines operation frequency
- Message queue operates asynchronously from clock rate
- Socket connections are maintained for message passing

### Logging System
- Real-time logging of all events
- Timestamps in both system time and logical clock time
- Queue length monitoring for message processing

### Analysis Tools
- Post-run analysis of system behavior
- Correlation of events across machines
- Visualization of logical clock progression
- Monitoring of message queue dynamics

## Requirements
- Python 3.6+
- No additional modules should need to be installed, as they are standard:
  - threading
  - socket
  - logging
  - json
  - time
