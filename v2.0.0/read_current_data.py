import os

current_data_file = "current_data.csv"

def read_current_data():
    try:
        with open(current_data_file, mode="r") as file:
            lines = file.readlines()
            data = lines[1].strip().split(",")  # Skip header and read data line
            # Date remains as string, counters are converted to integers
            return [data[0]] + [int(x) for x in data[1:]]
    except FileNotFoundError:
        # Create the file with default data if it doesn't exist
        with open(current_data_file, mode="w") as file:
            header = "date,espresso,cappuccino,lungo,iced latte,affogato,shakerato,espresso tonic,other,count_battery,count_descale,count_degrease,count_grinder,count_maintenance\n"
            default_data = "2025-02-07,0,0,0,0,0,0,0,0,0,0,0,0,0\n"
            file.write(header)
            file.write(default_data)
        return ["2025-02-07"] + [0] * 14