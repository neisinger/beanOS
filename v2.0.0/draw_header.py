import badger2040
from read_battery_voltage import read_battery_voltage
from read_storage_percentage import read_storage_percentage

def draw_header(date_str):
    display = badger2040.Badger2040()
    WIDTH = 296

    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, 16)
    display.set_pen(15)
    display.text("beanOS", 4, 4, WIDTH, 1)
    
    # Zeichne Batterie- und Speicherplatzsymbole
    voltage = read_battery_voltage()
    storage_percentage = read_storage_percentage()
    
    # Battery icon dimensions
    battery_icon_width = 24
    battery_icon_height = 10
    icon_y = 3
    
    # Storage icon dimensions
    storage_icon_width = 16
    storage_icon_height = 14
    storage_bar_height = 3
    storage_bar_spacing = 1
    
    # Draw date, battery icon, and storage icon if values are below the warning thresholds
    battery_str = f"{voltage:.2f}V"
    date_width = display.measure_text(date_str, 1)
    date_x = WIDTH - date_width - 4
    
    icon_x = date_x

    if voltage <= 3.4:  # Adjusted for modularity
        icon_x -= battery_icon_width + 4  # 4 pixels spacing between icons and date
        display.rectangle(icon_x, icon_y, battery_icon_width, battery_icon_height)
        display.rectangle(icon_x + battery_icon_width, icon_y + 2, 2, battery_icon_height - 4)
        battery_text_width = display.measure_text(battery_str, 1)
        display.text(battery_str, icon_x + (battery_icon_width - battery_text_width) // 2, icon_y + 2, WIDTH, 1)
    
    if storage_percentage >= 90:  # Adjusted for modularity
        icon_x -= storage_icon_width + 4
        for i in range(3):
            y = icon_y + i * (storage_bar_height + storage_bar_spacing)
            display.rectangle(icon_x, y, storage_icon_width, storage_bar_height)

    display.text(date_str, date_x, 4, WIDTH, 1)