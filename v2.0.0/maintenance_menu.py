import time
import badger2040
from read_current_data import read_current_data
from write_current_data import write_current_data
from update_display import update_display
from draw_header import draw_header

def maintenance_menu():
    options = ["Entkalken", "Entfetten", "Mühle reinigen", "Große Reinigung"]
    selected_option = 0

    display = badger2040.Badger2040()
    WIDTH = 296
    HEIGHT = 128

    while True:
        display.set_pen(15)
        display.clear()
        draw_header("Wartung")
        display.set_pen(0)
        display.set_font("bitmap8")

        for i, option in enumerate(options):
            if i == selected_option:
                display.set_pen(12)
                display.rectangle(0, 16 + i * 16, WIDTH, 16)
                display.set_pen(15)
            else:
                display.set_pen(0)
            display.text(option, 5, 16 + i * 16, WIDTH, 1)

        display.update()

        if display.pressed(badger2040.BUTTON_UP):
            selected_option = (selected_option - 1) % len(options)
        elif display.pressed(badger2040.BUTTON_DOWN):
            selected_option = (selected_option + 1) % len(options)
        elif display.pressed(badger2040.BUTTON_A):
            data = read_current_data()
            confirmation_message = ""
            if selected_option == 0:
                data[10] = 0  # Reset descale counter
                confirmation_message = "Entkalkung zurückgesetzt"
            elif selected_option == 1:
                data[11] = 0  # Reset degrease counter
                confirmation_message = "Entfetung zurückgesetzt"
            elif selected_option == 2:
                data[12] = 0  # Reset grinder counter
                confirmation_message = "Mühle Reinigung zurückgesetzt"
            elif selected_option == 3:
                data[13] = 0  # Reset maintenance counter
                confirmation_message = "Große Reinigung zurückgesetzt"
            write_current_data(data)
            update_display()  # Refresh the display to show the reset counter

            # Display confirmation message
            display.set_pen(0)  # Set background to black
            display.clear()
            draw_header("Wartung")
            display.set_pen(15)  # Set text to white
            display.set_font("bitmap8")
            text_width = display.measure_text(confirmation_message, 2)
            display.text(confirmation_message, (WIDTH - text_width) // 2, HEIGHT // 2 - 10, WIDTH, 2)
            display.update()
            time.sleep(2)  # Display confirmation message for 2 seconds

        elif display.pressed(badger2040.BUTTON_C):
            return  # Close the menu

        time.sleep(0.1)