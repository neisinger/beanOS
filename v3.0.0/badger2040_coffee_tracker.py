import badger2040
import time
import csv
from datetime import datetime

# File paths
LOG_FILE = "/log.csv"
CURRENT_DATA_FILE = "/current_data.csv"

# Initial counters
espresso_count = 0
cappuccino_count = 0
other_count = 0

# Initialize Badger2040
badger = badger2040.Badger2040()

# Load current data
def load_current_data():
    try:
        with open(CURRENT_DATA_FILE, "r") as file:
            reader = csv.reader(file)
            data = next(reader)
            global espresso_count, cappuccino_count, other_count
            espresso_count = int(data[1])
            cappuccino_count = int(data[2])
            other_count = int(data[3])
            return data[0]
    except:
        return None

# Save current data
def save_current_data(date):
    with open(CURRENT_DATA_FILE, "w") as file:
        writer = csv.writer(file)
        writer.writerow([date, espresso_count, cappuccino_count, other_count])

# Log data to CSV
def log_data(date):
    with open(LOG_FILE, "a") as file:
        writer = csv.writer(file)
        writer.writerow([date, espresso_count, cappuccino_count, other_count])

# Initialize data
current_date = load_current_data()
if not current_date:
    current_date = input("Enter current date (DD.MM.YYYY): ")
    save_current_data(current_date)

# Display function
def display():
    badger.pen(0)
    badger.clear()
    badger.pen(15)
    badger.text(f"Date: {current_date}", 10, 10)
    badger.text(f"Espresso: {espresso_count}", 10, 30)
    badger.text(f"Cappuccino: {cappuccino_count}", 10, 50)
    badger.text(f"Other: {other_count}", 10, 70)
    badger.update()

# Button handling
def button_a():
    global espresso_count
    espresso_count += 1
    save_current_data(current_date)
    display()

def button_b():
    global cappuccino_count
    cappuccino_count += 1
    save_current_data(current_date)
    display()

def button_c():
    global other_count
    other_count += 1
    save_current_data(current_date)
    display()

def button_up():
    global current_menu
    current_menu = "main_menu"
    display_menu()

def button_down():
    global current_date, espresso_count, cappuccino_count, other_count
    log_data(current_date)
    espresso_count = 0
    cappuccino_count = 0
    other_count = 0
    current_date = (datetime.strptime(current_date, "%d.%m.%Y") + timedelta(days=1)).strftime("%d.%m.%Y")
    save_current_data(current_date)
    display()

# Menu handling
current_menu = None

def display_menu():
    badger.pen(0)
    badger.clear()
    badger.pen(15)
    if current_menu == "main_menu":
        badger.text("> Einstellungen", 10, 10)
        badger.text("  Auswertung", 10, 30)
        badger.text("  Achievements", 10, 50)
        badger.text("  Impressum", 10, 70)
    badger.update()

# Main loop
display()
while True:
    if badger.pressed(badger2040.BUTTON_A):
        button_a()
    elif badger.pressed(badger2040.BUTTON_B):
        button_b()
    elif badger.pressed(badger2040.BUTTON_C):
        button_c()
    elif badger.pressed(badger2040.BUTTON_UP):
        button_up()
    elif badger.pressed(badger2040.BUTTON_DOWN):
        button_down()
    time.sleep(0.1)