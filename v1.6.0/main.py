import time, badger2040, machine, os

# Initialisierung des Badger2040
display = badger2040.Badger2040()
display.set_font("bitmap8")  # Schriftart ändern
WIDTH, HEIGHT = 296, 128
BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP, BUTTON_DOWN, LED = badger2040.BUTTON_A, badger2040.BUTTON_B, badger2040.BUTTON_C, badger2040.BUTTON_UP, badger2040.BUTTON_DOWN, 25
led = machine.Pin(LED, machine.Pin.OUT)
log_file, date_file, count_file = "kaffee_log.csv", "current_date.txt", "current_counts.txt"
menu_options = ["Statistiken anzeigen", "Tagesstatistiken zurücksetzen", "Gesamtstatistiken zurücksetzen", "Datum ändern", "Information"]
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
    if file in os.listdir():
        with open(file, 'r') as f:
            return parser(f.readline().strip())
    return default

def format_date(t): return f"{t[2]:02d}.{t[1]:02d}.{t[0]}"
def save_data(date, espresso, cappuccino, other):
    with open(log_file, 'a') as file:
        file.write(f'{date},{espresso},{cappuccino},{other}\n')

def update_file(file, content):
    with open(file, 'w') as f:
        f.write(content)

current_date = get_from_file(date_file, time.mktime((2025, 2, 5, 0, 0, 0, 0, 0, -1)), parse_date)
espresso_count, cappuccino_count, other_count, battery_reminder_count = map(int, get_from_file(count_file, "0,0,0,0").split(','))
button_press_count, temp_date, refresh_count = 0, current_date, 0

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
        display.text("Gesamtstatistiken:", 10, 10)
        display.text(f"Espresso: {total_espresso}", 10, 30)
        display.text(f"Cappuccino: {total_cappuccino}", 10, 50)
        display.text(f"Anderes: {total_other}", 10, 70)
        display.text(f"Seit: {first_date}" if first_date else "Keine Daten verfügbar", 10, 90)
    elif view_info_active:
        display.text("Information:", 10, 10)
        display.text(f"Version: {version}", 10, 30)
        display.text("by Joao Neisinger", 10, 50)
        display.text("Lizenz: None", 10, 70)
    elif additional_menu_active:
        for i, option in enumerate(additional_menu_options):
            display.text("> " + option if i == current_additional_menu_option else option, 10, 20 + i * 20)
    elif menu_active:
        for i, option in enumerate(menu_options):
            display.text("> " + option if i == current_menu_option else option, 10, 20 + i * 20)
    else:
        terms = ["ESPRESSO", "CAPPU", "ANDERES"]
        counts = [espresso_count, cappuccino_count, other_count]
        centers = [41, 147, 253]  # Neue Zentrierungen
        for term, count, center in zip(terms, counts, centers):
            display.text(str(count), center + (display.measure_text(term, 1) - display.measure_text(str(count), 1)) // 2 - display.measure_text(str(count), 1) // 2, HEIGHT - 40)
            display.text(term, center - display.measure_text(term, 1) // 2, HEIGHT - 20)
    display.update()

def button_pressed(pin):
    global espresso_count, cappuccino_count, other_count, current_date, button_press_count, menu_active, current_menu_option, change_date_active, view_statistics_active, view_info_active, battery_reminder_active, battery_reminder_count, additional_menu_active, current_additional_menu_option, additional_counts
    if battery_reminder_active:
        if display.pressed(BUTTON_A):
            battery_reminder_active = False
            battery_reminder_count = 0
            update_file(count_file, f'{espresso_count},{cappuccino_count},{other_count},{battery_reminder_count}')
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
        if display.pressed(BUTTON_C): view_statistics_active = False
        update_display(False)
        return
    if view_info_active:
        if display.pressed(BUTTON_C): view_info_active = False
        update_display(False)
        return
    if additional_menu_active:
        if display.pressed(BUTTON_UP):
            current_additional_menu_option = (current_additional_menu_option - 1) % len(additional_menu_options)
        elif display.pressed(BUTTON_DOWN):
            current_additional_menu_option = (current_additional_menu_option + 1) % len(additional_menu_options)
        elif display.pressed(BUTTON_A):
            additional_counts[current_additional_menu_option] += 1
        elif display.pressed(BUTTON_C):
            additional_menu_active = False
        update_display(False)
        return
    if display.pressed(BUTTON_UP):
        current_menu_option = (current_menu_option - 1) % len(menu_options) if menu_active else 0
        menu_active = True if not menu_active else menu_active
        update_display(False)
        return
    if display.pressed(BUTTON_DOWN):
        current_menu_option = (current_menu_option + 1) % len(menu_options) if menu_active else 0
        if not menu_active:
            save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, other_count)
            current_date += 86400
            update_file(date_file, format_date(time.localtime(current_date)))
            espresso_count, cappuccino_count, other_count, battery_reminder_count = 0, 0, 0, battery_reminder_count + 1
            battery_reminder_active = battery_reminder_count >= 10
            button_press_count = 0
            update_display(True)
            update_file(count_file, f'{espresso_count},{cappuccino_count},{other_count},{battery_reminder_count}')
        update_display(False)
        return
    if display.pressed(BUTTON_A):
        if menu_active:
            if current_menu_option == 0: view_statistics_active = True
            if current_menu_option == 1:
                clear_today_log_entries(log_file, count_file, format_date(time.localtime(current_date)))
                espresso_count, cappuccino_count, other_count = 0, 0, 0
            if current_menu_option == 2: clear_log_file(log_file); clear_count_file(count_file); espresso_count, cappuccino_count, other_count = 0, 0, 0
            if current_menu_option == 3: change_date_active, temp_date = True, current_date
            if current_menu_option == 4: view_info_active = True
            if current_menu_option == 5: menu_active = False
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
    update_file(count_file, f'{espresso_count},{cappuccino_count},{other_count},{battery_reminder_count}')

if __name__ == "__main__":
    led.value(1)
    update_display(True)
    while True:
        if any(display.pressed(btn) for btn in [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP, BUTTON_DOWN]):
            button_pressed(None)
        else:
            led.value(0)
        time.sleep(0.1)
    led.value(0)
