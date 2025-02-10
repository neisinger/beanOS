import time, badger2040, machine, uos

# Initialisierung des Badger2040
display = badger2040.Badger2040()
display.set_font("bitmap8")  # Schriftart ändern
WIDTH, HEIGHT = 296, 128
BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP, BUTTON_DOWN, LED = badger2040.BUTTON_A, badger2040.BUTTON_B, badger2040.BUTTON_C, badger2040.BUTTON_UP, badger2040.BUTTON_DOWN, 25
led = machine.Pin(LED, machine.Pin.OUT)
log_file, date_file, count_file = "kaffee_log.csv", "current_date.txt", "current_counts.txt"
menu_options = ["Statistiken anzeigen", "Tagesstatistiken zurücksetzen", "Datum ändern", "Information"]
current_menu_option, menu_active, change_date_active, view_statistics_active, view_info_active, battery_reminder_active = 0, False, False, False, False, False
version = "1.6.0"
# Neue globale Variablen
additional_menu_active = False
additional_menu_options = ["lungo", "iced latte", "affogato", "shakerato", "espresso tonic", "other"]
current_additional_menu_option = 0
additional_counts = [0] * len(additional_menu_options)

def parse_date(date_str):
    try:
        day, month, year = map(int, date_str.split('.'))
        return time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
    except ValueError as e:
        print(f"Fehler beim Parsen des Datums: {e}")
        return None

def get_from_file(file, default, parser=lambda x: x):
    if file in uos.listdir():
        with open(file, 'r') as f:
            return parser(f.readline().strip())
    return default

def format_date(t): return f"{t[2]:02d}.{t[1]:02d}.{t[0]}"

def save_data(date, espresso, cappuccino, additional_counts):
    if log_file not in uos.listdir():
        with open(log_file, 'w') as file:
            headers = "Datum,Espresso,Cappuccino," + ",".join(additional_menu_options)
            file.write(headers + "\n")
    lines = []
    with open(log_file, 'r') as file:
        lines = file.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(date):
            parts = line.strip().split(',')
            parts[1] = str(espresso)
            parts[2] = str(cappuccino)
            for j in range(3, 3 + len(additional_counts)):
                parts[j] = str(additional_counts[j - 3])
            lines[i] = ','.join(parts) + '\n'
            updated = True
            break
    
    if not updated:
        additional_counts_str = ",".join(map(str, additional_counts))
        lines.append(f'{date},{espresso},{cappuccino},{additional_counts_str}\n')
    
    with open(log_file, 'w') as file:
        file.write(''.join(lines))
    print(f"Data saved: {date}, {espresso}, {cappuccino}, {additional_counts}")

def nap():
    global menu_active, view_statistics_active, change_date_active, view_info_active, additional_menu_active
    print("System will turn off in 5 seconds...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        # Make the LED flicker
        for _ in range(5):
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            time.sleep(0.1)
    display.set_update_speed(badger2040.UPDATE_FAST)
    display.set_pen(4)  # Set to white color
    text1 = "wake me up"
    text2 = "when the caffeine ends"
    text_width1 = display.measure_text(text1, 2)
    text_width2 = display.measure_text(text2, 2)
    display.text(text1, (WIDTH - text_width1) // 2, (HEIGHT // 2) - 20, scale=2)
    display.text(text2, (WIDTH - text_width2) // 2, (HEIGHT // 2), scale=2)
    display.update()
    
    # Configure buttons as wake-up sources, excluding BUTTON_UP
    for btn in [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_DOWN]:
        pin = machine.Pin(btn, machine.Pin.IN, machine.Pin.PULL_UP)
        pin.irq(trigger=machine.Pin.IRQ_RISING)
    
    print("System turned off")
    display.halt()

    # Reset menu state after wake up
    menu_active = False
    view_statistics_active = False
    change_date_active = False
    view_info_active = False
    additional_menu_active = False

    # Reset button states
    for btn in [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_DOWN]:
        pin = machine.Pin(btn, machine.Pin.IN, machine.Pin.PULL_UP)
        pin.irq(trigger=0)  # Disable interrupts to reset state  

def update_file(file, content):
    with open(file, 'w') as f:
        f.write(content)

current_date = get_from_file(date_file, time.mktime((2025, 2, 5, 0, 0, 0, 0, 0, -1)), parse_date)
espresso_count, cappuccino_count, other_count, battery_reminder_count = map(int, get_from_file(count_file, "0,0,0,0").split(','))
button_press_count, temp_date, refresh_count = 0, current_date, 0

def clear_log_file(file, date):
    if file in uos.listdir():
        with open(file, 'r') as f:
            lines = f.readlines()
        
        with open(file, 'w') as f:
            for line in lines:
                if line.startswith(date):
                    parts = line.strip().split(',')
                    parts[1] = '0'  # Reset espresso count
                    parts[2] = '0'  # Reset cappuccino count
                    for j in range(3, len(parts)):
                        parts[j] = '0'  # Reset additional counts
                    f.write(','.join(parts) + '\n')
                else:
                    f.write(line)

def calculate_total_statistics_and_first_date():
    if log_file not in uos.listdir():
        return 0, 0, 0, None
    
    total_espresso, total_cappuccino, total_other = 0, 0, 0
    first_date = None
    
    with open(log_file, 'r') as file:
        lines = file.readlines()[1:]  # Skip header line
        for line in lines:
            date, espresso, cappuccino, *additional_counts = line.strip().split(',')
            total_espresso += int(espresso)
            total_cappuccino += int(cappuccino)
            total_other += sum(map(int, additional_counts))
            if first_date is None:
                first_date = date
    
    return total_espresso, total_cappuccino, total_other, first_date

def update_display(full_update=False):
    global refresh_count
    if battery_reminder_active:
        display.set_update_speed(badger2040.UPDATE_NORMAL)
        display.set_pen(0)
        display.clear()
        display.set_pen(15)
        display.text("Batterien wechseln!", 10, 50, scale=2)
        display.update()
        return

    display.set_update_speed(badger2040.UPDATE_NORMAL if full_update or refresh_count >= 14 else badger2040.UPDATE_TURBO)
    refresh_count = 0 if full_update else refresh_count + 1
    display.set_pen(15)
    display.clear()
    
    # Schwarz 20 Pixel hohen Balken hinzufügen
    display.set_pen(0)
    display.rectangle(0, 0, WIDTH, 20)
    display.set_pen(15)
    
    # Text in Weiß
    display.set_pen(15)
    display.text("beanOS", 10, 2)
    date_str = format_date(time.localtime(current_date))
    display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
    
    display.set_pen(0)

    if change_date_active:
        date_str = format_date(time.localtime(temp_date))
        display.text(date_str, (WIDTH - display.measure_text(date_str, 2)) // 2, HEIGHT // 2 - 10, scale=2)
    elif view_statistics_active:
        total_espresso, total_cappuccino, total_other, first_date = calculate_total_statistics_and_first_date()
        display.set_font("bitmap8")
        display.text("Gesamtstatistiken", 10, 22)
        display.text(f"Espresso {total_espresso}", 10, 44)
        display.text(f"Cappuccino {total_cappuccino}", 10, 66)
        display.text(f"Andere Getränke {total_other}", 10, 88)
        display.text(f"Seit: {first_date}" if first_date else "Keine Daten verfügbar", 10, 110)
    elif view_info_active:
        display.set_font("bitmap8")
        display.text("Information", 10, 22)
        display.text(f"Version: {version}", 10, 44)
        display.text("by Joao Neisinger", 10, 66)
        display.text("Lizenz: None", 10, 88)
    elif additional_menu_active:
        display.set_font("bitmap8")  # Schriftart auf bitmap8 setzen
        for i, option in enumerate(additional_menu_options):
            display.text("> " + option if i == current_additional_menu_option else option, 10, 22 + i * 18)  # Abstand zu oberem Rand auf 22 Pixel gesetzt
    elif menu_active:
        display.set_font("bitmap8")  # Schriftart auf bitmap8 setzen
        for i, option in enumerate(menu_options):
            display.text("> " + option if i == current_menu_option else option, 10, 22 + i * 18)  # Abstand zu oberem Rand auf 22 Pixel gesetzt
    else:
        # Zähler und Labels am unteren Bildschirmrand
        terms = ["ESPRESSO", "CAPPU", "ANDERES"]
        counts = [espresso_count, cappuccino_count, sum(additional_counts)]
        centers = [41, 147, 253]  # Zentrierungen
        for term, count, center in zip(terms, counts, centers):
            display.text(str(count), center - display.measure_text(str(count), 1) // 2, HEIGHT - 42, scale=2)
            display.text(term, center - display.measure_text(term, 1) // 2, HEIGHT - 22, scale=2)

    display.update()

def clear_today_log_entries(log_file, date):
    if log_file in uos.listdir():
        with open(log_file, 'r') as file:
            lines = file.readlines()

        with open(log_file, 'w') as file:
            for line in lines:
                if not line.startswith(date):
                    file.write(line)

def load_counters_from_log(log_file):
    global espresso_count, cappuccino_count, other_count, additional_counts
    if log_file in uos.listdir():
        with open(log_file, 'r') as file:
            lines = file.readlines()
            if len(lines) > 1:
                last_line = lines[-1].strip().split(',')
                espresso_count = int(last_line[1])
                cappuccino_count = int(last_line[2])
                other_count = int(last_line[3])
                additional_counts = list(map(int, last_line[4:]))

def button_pressed(pin):
    global espresso_count, cappuccino_count, current_date, button_press_count, menu_active, current_menu_option, change_date_active, view_statistics_active, view_info_active, battery_reminder_active, additional_menu_active, current_additional_menu_option, additional_counts, battery_reminder_count, temp_date, last_interaction_time, other_count

    last_interaction_time = time.time()  # Update last interaction time on button press
    print(f"Button pressed: {pin}, last interaction time updated")

    if battery_reminder_active:
        if display.pressed(BUTTON_A):
            battery_reminder_active = False
            battery_reminder_count = 0
            save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, additional_counts)
            update_display(True)
        return

    if change_date_active:
        temp_date += -86400 if display.pressed(BUTTON_UP) else 86400 if display.pressed(BUTTON_DOWN) else 0
        if display.pressed(BUTTON_A):
            current_date = temp_date
            update_file(date_file, format_date(time.localtime(current_date)))
            change_date_active, menu_active = False, False
        elif display.pressed(BUTTON_C):
            temp_date, change_date_active = current_date, False
        update_display(False)
        return

    if view_statistics_active:
        if display.pressed(BUTTON_C): 
            view_statistics_active = False
        update_display(False)
        return

    if view_info_active:
        if display.pressed(BUTTON_C): 
            view_info_active = False
        update_display(False)
        return

    if additional_menu_active:
        if display.pressed(BUTTON_UP):
            current_additional_menu_option = (current_additional_menu_option - 1) % len(additional_menu_options)
            print(f"BUTTON_UP pressed in additional_menu_active: {current_additional_menu_option}")
        elif display.pressed(BUTTON_DOWN):
            current_additional_menu_option = (current_additional_menu_option + 1) % len(additional_menu_options)
        elif display.pressed(BUTTON_A):
            additional_counts[current_additional_menu_option] += 1
            save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, additional_counts)
            additional_menu_active = False  # Menü schließen
        elif display.pressed(BUTTON_C):
            additional_menu_active = False
        update_display(False)
        return

    if display.pressed(BUTTON_UP):
        current_menu_option = (current_menu_option - 1) % len(menu_options) if menu_active else 0
        menu_active = True if not menu_active else menu_active
        print(f"BUTTON_UP pressed: {current_menu_option}, menu_active: {menu_active}")
        update_display(False)
        return

    if display.pressed(BUTTON_DOWN):
        current_menu_option = (current_menu_option + 1) % len(menu_options) if menu_active else 0
        if not menu_active:
            save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, additional_counts)
            current_date += 86400
            update_file(date_file, format_date(time.localtime(current_date)))
            espresso_count, cappuccino_count, other_count, battery_reminder_count = 0, 0, 0, battery_reminder_count + 1
            additional_counts = [0] * len(additional_menu_options)  # Reset additional counts
            battery_reminder_active = battery_reminder_count >= 10
            button_press_count = 0
            update_display(True)
        update_display(False)
        return

    if display.pressed(BUTTON_A):
        if menu_active:
            if current_menu_option == 0: view_statistics_active = True
            if current_menu_option == 1:
                clear_today_log_entries(log_file, format_date(time.localtime(current_date)))
                espresso_count, cappuccino_count = 0, 0
            if current_menu_option == 2: change_date_active, temp_date = True, current_date
            if current_menu_option == 3: view_info_active = True
            if current_menu_option == 4: menu_active = False
            update_display(True)
            return
        espresso_count += 1
        button_press_count += 1

    if display.pressed(BUTTON_B):
        if not menu_active:
            cappuccino_count += 1
            button_press_count += 1

    if display.pressed(BUTTON_C):
        if menu_active:
            if change_date_active: change_date_active = False
            elif view_statistics_active: view_statistics_active = False
            elif view_info_active: view_info_active = False
            else: menu_active = False
            update_display(True)
        else:
            additional_menu_active = True
        update_display(False)
        return

    if not menu_active:
        other_count += 1
        button_press_count += 1

    update_display(False)
    if button_press_count >= 10:
        update_display(True)
        button_press_count = 0
    save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, additional_counts)

if __name__ == "__main__":
    current_date = get_from_file(date_file, time.mktime((2025, 2, 5, 0, 0, 0, 0, 0, -1)), parse_date)
    espresso_count, cappuccino_count, other_count, battery_reminder_count = map(int, get_from_file(count_file, "0,0,0,0").split(','))
    button_press_count, temp_date, refresh_count = 0, current_date, 0

    load_counters_from_log(log_file)
    print("Counters initialized")

    led.value(1)  # Ensure the LED is on when RP2040 is active
    update_display(True)
    last_interaction_time = time.time()  # Initialize last interaction time
    while True:
        if any(display.pressed(btn) for btn in [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP, BUTTON_DOWN]):
            button_pressed(None)
        else:
            led.value(1)  # Keep LED on when no button is pressed
        # Check for inactivity and turn off if no interaction for 30 seconds
        if time.time() - last_interaction_time > 15:
            nap()
        time.sleep(0.1)
    led.value(0)
