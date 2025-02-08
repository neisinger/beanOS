import os
import machine
from read_current_data import read_current_data
from write_current_data import write_current_data
from update_display import update_display

def reset_total_stats():
    log_file = "log.csv"
    # Clear the log file
    with open(log_file, "w") as f:
        f.write("")  
    
    # Reset beverage counters to 0 in current_data.csv
    data = read_current_data()
    for i in range(1, 9):
        data[i] = 0
    write_current_data(data)
    
    update_display()  # Refresh the display to show the reset statistics
    machine.reset()   # Restart the RP2040