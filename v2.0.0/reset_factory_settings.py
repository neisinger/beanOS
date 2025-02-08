import machine
from read_current_data import read_current_data
from write_current_data import write_current_data
from reset_total_stats import reset_total_stats

def reset_factory_settings():
    data = read_current_data()
    for i in range(1, len(data)):
        data[i] = 0
    write_current_data(data)
    reset_total_stats()
    machine.reset()   # Restart the RP2040