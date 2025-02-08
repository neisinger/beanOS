import badger2040
from display import display_main, display_menu
from data_handler import save_current_data, log_data
from datetime import datetime, timedelta

# Button handling
def handle_button_presses(current_date, espresso_count, cappuccino_count, other_count):
    if badger2040.pressed(badger2040.BUTTON_A):
        button_a(current_date, espresso_count, cappuccino_count, other_count)
    elif badger2040.pressed(badger2040.BUTTON_B):
        button_b(current_date, espresso_count, cappuccino_count, other_count)
    elif badger2040.pressed(badger2040.BUTTON_C):
        button_c(current_date, espresso_count, cappuccino_count, other_count)
    elif badger2040.pressed(badger2040.BUTTON_UP):
        button_up()
    elif badger2040.pressed(badger2040.BUTTON_DOWN):
        button_down(current_date, espresso_count, cappuccino_count, other_count)

def button_a(current_date, espresso_count, cappuccino_count, other_count):
    espresso_count += 1
    save_current_data(current_date, espresso_count, cappuccino_count, other_count)
    display_main(current_date, espresso_count, cappuccino_count, other_count)

def button_b(current_date, espresso_count, cappuccino_count, other_count):
    cappuccino_count += 1
    save_current_data(current_date, espresso_count, cappuccino_count, other_count)
    display_main(current_date, espresso_count, cappuccino_count, other_count)

def button_c(current_date, espresso_count, cappuccino_count, other_count):
    other_count += 1
    save_current_data(current_date, espresso_count, cappuccino_count, other_count)
    display_main(current_date, espresso_count, cappuccino_count, other_count)

def button_up():
    current_menu = "main_menu"
    display_menu(current_menu)

def button_down(current_date, espresso_count, cappuccino_count, other_count):
    log_data(current_date, espresso_count, cappuccino_count, other_count)
    espresso_count = 0
    cappuccino_count = 0
    other_count = 0
    current_date = (datetime.strptime(current_date, "%d.%m.%Y") + timedelta(days=1)).strftime("%d.%m.%Y")
    save_current_data(current_date, espresso_count, cappuccino_count, other_count)
    display_main(current_date, espresso_count, cappuccino_count, other_count)