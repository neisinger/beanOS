import time
from display import display_main, display_menu
from buttons import handle_button_presses
from data_handler import initialize_data, save_current_data, log_data, load_current_data
from datetime import datetime, timedelta

# Initialize data
current_date, espresso_count, cappuccino_count, other_count = load_current_data()
if not current_date:
    current_date = input("Enter current date (DD.MM.YYYY): ")
    save_current_data(current_date, 0, 0, 0)

# Display main screen
display_main(current_date, espresso_count, cappuccino_count, other_count)

# Main loop
while True:
    handle_button_presses(current_date, espresso_count, cappuccino_count, other_count)
    time.sleep(0.1)