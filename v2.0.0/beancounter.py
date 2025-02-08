import badger2040
from draw_header import draw_header
from read_current_data import read_current_data
from draw_counters import draw_counters

def show_beancounter():
    display = badger2040.Badger2040()
    display.set_pen(15)
    display.clear()

    data = read_current_data()
    current_date = data[0]
    espresso_count = data[1]
    cappuccino_count = data[2]
    other_count = sum(data[3:9])
    
    draw_header(current_date)
    draw_counters(espresso_count, cappuccino_count, other_count)
    
    display.set_update_speed(badger2040.UPDATE_NORMAL)
    display.update()