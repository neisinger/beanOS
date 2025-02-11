import badger2040
import machine
import time

# Constants
WIDTH = 296
HEIGHT = 128
GRID_SIZE = 16
SQUARE_SIZE = 16
PADDING = 1
NUM_DAYS = 128
FILENAME = "kaffee_log.csv"

# Initialize display
display = badger2040.Badger2040()
display.set_font("bitmap8")

def read_log():
    data = []
    with open(FILENAME, 'r') as file:
        headers = file.readline().strip().split(',')
        for line in file:
            row = line.strip().split(',')
            daily_sum = sum(int(value) for i, value in enumerate(row) if headers[i] != 'Datum')
            data.append(daily_sum)
    return data

def normalize_data(data):
    max_value = max(data) if data else 1
    normalized = [int((value / max_value) * 255) for value in data]
    return normalized

def fill_data(data):
    if len(data) < NUM_DAYS:
        data = [0] * (NUM_DAYS - len(data)) + data
    return data[-NUM_DAYS:]

def draw_heatmap(data):
    display.set_pen(15)  # White background
    display.clear()
    data = fill_data(data)
    normalized_data = normalize_data(data)
    
    for i, value in enumerate(normalized_data):
        row = i // 16
        col = i % 16
        x = col * SQUARE_SIZE
        y = row * SQUARE_SIZE
        color = 255 - value  # Invert value for grayscale
        display.set_pen(color)
        display.rectangle(x + PADDING, y + PADDING, SQUARE_SIZE - PADDING, SQUARE_SIZE - PADDING)
    
    display.update()

def main():
    last_update = time.time()
    while True:
        if display.pressed(badger2040.BUTTON_C):
            machine.reset()  # This will reset the device and run main.py

        current_time = time.time()
        if current_time - last_update >= 60:  # Check if a minute has passed
            data = read_log()
            draw_heatmap(data)
            last_update = current_time

if __name__ == "__main__":
    main()
