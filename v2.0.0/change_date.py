import badger2040
from read_current_data import read_current_data
from write_current_data import write_current_data
from update_display import update_display
from draw_header import draw_header

def change_date():
    display = badger2040.Badger2040()
    data = read_current_data()
    current_date = data[0]
    date_parts = current_date.split('.')
    day = int(date_parts[0])
    month = int(date_parts[1])
    year = int(date_parts[2])
    
    date_changed = False
    first_load = True
    while not date_changed:
        display.set_pen(15)
        display.clear()
        draw_header(data[0])
        display.set_pen(0)
        display.set_font("bitmap8")
        new_date = f"{day:02d}.{month:02d}.{year:04d}"
        date_width = display.measure_text(new_date, 2)
        display.text(new_date, (296 - date_width) // 2, 128 // 2 - 10, 296, 2)
        
        if first_load:
            display.set_update_speed(badger2040.UPDATE_MEDIUM)  # Full update on first load
            display.update()
            first_load = False
        else:
            display.set_update_speed(badger2040.UPDATE_TURBO)  # Quick update for date changes
            display.update()

        if display.pressed(badger2040.BUTTON_UP):
            day = (day % 31) + 1
        elif display.pressed(badger2040.BUTTON_DOWN):
            day = (day - 2) % 31 + 1
        elif display.pressed(badger2040.BUTTON_A):
            date_changed = True
            data[0] = new_date
            write_current_data(data)
            update_display()  # Reload start page after date change
        elif display.pressed(badger2040.BUTTON_C):
            return  # Close the menu
        time.sleep(0.05)  # Reduced delay time for more responsive buttons