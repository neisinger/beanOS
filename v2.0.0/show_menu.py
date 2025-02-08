import time
import badger2040
from draw_header import draw_header
from read_current_data import read_current_data
from handle_menu_selection import handle_menu_selection
from settings_sub_options import settings_sub_options

def show_menu(options, title):
    global settings_current_option
    settings_current_option = 0
    menu_active = True
    last_option = -1

    display = badger2040.Badger2040()
    WIDTH = 296

    display.set_update_speed(badger2040.UPDATE_TURBO)

    while menu_active:
        if settings_current_option != last_option:
            display.set_pen(15)
            display.clear()
            draw_header(read_current_data()[0])
            display.set_pen(0)
            display.text(title, 10, 4, WIDTH, 1)
            for i, option in enumerate(options):
                y_pos = 40 + i * 20  # Start at 40 to leave the first line blank
                if i == settings_current_option:
                    display.text("> " + option, 10, y_pos, WIDTH, 1)
                else:
                    display.text(option, 10, y_pos, WIDTH, 1)
            display.update()
            last_option = settings_current_option

        if display.pressed(badger2040.BUTTON_UP):
            settings_current_option = (settings_current_option - 1) % len(options)
        elif display.pressed(badger2040.BUTTON_DOWN):
            settings_current_option = (settings_current_option + 1) % len(options)
        elif display.pressed(badger2040.BUTTON_A):
            selected_option = options[settings_current_option]
            if selected_option in settings_sub_options:
                show_menu(settings_sub_options[selected_option], selected_option)
            else:
                handle_menu_selection(selected_option)
        elif display.pressed(badger2040.BUTTON_C):
            menu_active = False
        time.sleep(0.1)