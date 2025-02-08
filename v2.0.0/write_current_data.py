def write_current_data(data):
    current_data_file = "current_data.csv"
    with open(current_data_file, mode="w") as file:
        header = "date,espresso,cappuccino,lungo,iced latte,affogato,shakerato,espresso tonic,other,count_battery,count_descale,count_degrease,count_grinder,count_maintenance\n"
        file.write(header)
        file.write(",".join(map(str, data)) + "\n")