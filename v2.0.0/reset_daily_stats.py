import machine
from read_current_data import read_current_data
from write_current_data import write_current_data
from update_display import update_display

def reset_daily_stats():
    data = read_current_data()
    for i in range(1, 9):
        data[i] = 0
    write_current_data(data)
    update_display()
    machine.reset()   # Restart the RP2040