import csv
import time
import badger2040

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
        reader = csv.DictReader(file)
        for row in reader:
            daily_sum = sum(int(value) for key, value in row.items() if key != 'Datum')
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
    display.pen(15)  # White background
    display.clear()
    data = fill_data(data)
    normalized_data = normalize_data(data)
    
    for i, value in enumerate(normalized_data):
        row = i // 16
        col = i % 16
        x = col * SQUARE_SIZE
        y = row * SQUARE_SIZE
        color = 255 - value  # Invert value for grayscale
        display.pen(color)
        display.rectangle(x + PADDING, y + PADDING, SQUARE_SIZE - PADDING, SQUARE_SIZE - PADDING)
    
    display.update()

def main():
    while True:
        data = read_log()
        draw_heatmap(data)
        time.sleep(60)  # Update every minute

if __name__ == "__main__":
    main()