import time
import badger2040
from draw_header import draw_header
from read_current_data import read_current_data

def show_impressum():
    display = badger2040.Badger2040()
    WIDTH = 296

    display.set_update_speed(badger2040.UPDATE_NORMAL)
    display.set_pen(15)
    display.clear()
    draw_header(read_current_data()[0])
    display.set_pen(0)
    display.text("", 10, 10, WIDTH, 1)  # Empty line
    display.text("Version: 2.0.0", 10, 30, WIDTH, 1)
    display.text("Programmierer:", 10, 50, WIDTH, 1)
    display.text("Joao Neisinger", 10, 70, WIDTH, 1)
    display.text("Lizenz: None", 10, 90, WIDTH, 1)
    display.update()
    wait_for_user_to_release_buttons()
    while not display.pressed_any():
        time.sleep(0.1)