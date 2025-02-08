# File paths
LOG_FILE = "/log.csv"
CURRENT_DATA_FILE = "/current_data.csv"

# Load current data
def load_current_data():
    try:
        with open(CURRENT_DATA_FILE, "r") as file:
            data = file.readline().strip().split(',')
            current_date = data[0]
            espresso_count = int(data[1])
            cappuccino_count = int(data[2])
            other_count = int(data[3])
            return current_date, espresso_count, cappuccino_count, other_count
    except:
        return None, 0, 0, 0

# Save current data
def save_current_data(date, espresso_count, cappuccino_count, other_count):
    with open(CURRENT_DATA_FILE, "w") as file:
        file.write(f"{date},{espresso_count},{cappuccino_count},{other_count}\n")

# Log data to CSV
def log_data(date, espresso_count, cappuccino_count, other_count):
    with open(LOG_FILE, "a") as file:
        file.write(f"{date},{espresso_count},{cappuccino_count},{other_count}\n")