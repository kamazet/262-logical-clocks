import re
import sys
import os
from datetime import datetime
from collections import defaultdict

def parse_log_line(line):
    """Parse a single log line into timestamp and message"""
    try:
        timestamp_str, message = line.strip().split(" - ", 1)
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return timestamp, message
    except ValueError:
        return None, None

def extract_value(message, pattern):
    """Extract numerical value from message using regex pattern"""
    match = re.search(pattern, message)
    if match:
        return int(match.group(1))
    return None

def get_tick_rate(filename):
    """Extract tick rate from machine's initialization message"""
    with open(filename, 'r') as f:
        first_line = f.readline()
        _, message = parse_log_line(first_line)
        if message:
            rate = extract_value(message, r"clock rate: (\d+)")
            return rate
    return None

def read_log_file(filename):
    """Read a log file and extract logical clock and queue length values"""
    logical_clocks = []
    queue_lengths = []
    
    with open(filename, 'r') as f:
        for line in f:
            timestamp, message = parse_log_line(line)
            if not timestamp:
                continue
                
            logical_clock = extract_value(message, r"Logical clock: (\d+)")
            if logical_clock is not None:
                logical_clocks.append((timestamp, logical_clock))
                
            queue_length = extract_value(message, r"Queue length: (\d+)")
            if queue_length is not None:
                queue_lengths.append((timestamp, queue_length))
                
    return logical_clocks, queue_lengths

def write_value_file(filename, values, machine_count, tick_rates):
    """Write values to file in chronological order with even column spacing"""
    # Define column widths
    timestamp_width = 10  # HH:MM:SS format
    
    # Calculate required width for machine columns based on header length
    machine_headers = [f"Machine {i} ({tick_rates[i]} ticks/s)" for i in range(machine_count)]
    value_width = max(len(header) for header in machine_headers) + 4  # Add some padding
    
    with open(filename, 'w') as f:
        # Write header
        header = "Timestamp".ljust(timestamp_width)
        for i in range(machine_count):
            header += f" | {machine_headers[i]:<{value_width-3}}"
        f.write(header + "\n")
        
        # Write separator line
        f.write("-" * (timestamp_width + (value_width + 3) * machine_count - 3) + "\n")
        
        # Group values by timestamp
        time_values = defaultdict(lambda: ["" for _ in range(machine_count)])
        for machine_id, machine_values in enumerate(values):
            for timestamp, value in machine_values:
                time_values[timestamp][machine_id] = str(value)
        
        # Write values in chronological order
        for timestamp in sorted(time_values.keys()):
            time_str = timestamp.strftime('%H:%M:%S')
            row = time_str.ljust(timestamp_width)
            
            for value in time_values[timestamp]:
                row += f" | {value:<{value_width-3}}"
            
            f.write(row + "\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_logs.py <path_to_log_folder>")
        sys.exit(1)

    log_folder = sys.argv[1]
    
    # Check if folder exists
    if not os.path.isdir(log_folder):
        print(f"Error: Folder '{log_folder}' does not exist")
        sys.exit(1)
    
    # List of log files to analyze
    log_files = [
        os.path.join(log_folder, "machine_0.log"),
        os.path.join(log_folder, "machine_1.log"),
        os.path.join(log_folder, "machine_2.log")
    ]
    
    # Check if all log files exist
    for log_file in log_files:
        if not os.path.exists(log_file):
            print(f"Error: Log file '{log_file}' does not exist")
            sys.exit(1)
    
    # Get tick rates for all machines
    tick_rates = []
    for log_file in log_files:
        rate = get_tick_rate(log_file)
        if rate is None:
            print(f"Error: Could not find tick rate in {log_file}")
            sys.exit(1)
        tick_rates.append(rate)
    
    # Read all log files and extract values
    logical_clocks = []
    queue_lengths = []
    
    for log_file in log_files:
        lc, ql = read_log_file(log_file)
        logical_clocks.append(lc)
        queue_lengths.append(ql)
    
    # Create output files
    logical_clock_file = os.path.join(log_folder, "logical_clock.txt")
    queue_length_file = os.path.join(log_folder, "queue_length.txt")
    
    # Write values to files
    write_value_file(logical_clock_file, logical_clocks, len(log_files), tick_rates)
    write_value_file(queue_length_file, queue_lengths, len(log_files), tick_rates)
    
    print(f"Logical clock values written to {logical_clock_file}")
    print(f"Queue lengths written to {queue_length_file}")

if __name__ == "__main__":
    main() 