import badger2040, machine, time, json, uos

# Initialisierung des Badger2040
display = badger2040.Badger2040()
display.set_font("bitmap8")  # Schriftart ändern
WIDTH, HEIGHT = 296, 128
BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP, BUTTON_DOWN, LED = badger2040.BUTTON_A, badger2040.BUTTON_B, badger2040.BUTTON_C, badger2040.BUTTON_UP, badger2040.BUTTON_DOWN, 25
led = machine.Pin(LED, machine.Pin.OUT)
log_file, date_file, count_file = "kaffee_log.csv", "current_date.txt", "current_counts.txt"
menu_options = ["Bohnen", "Statistiken anzeigen", "Tagesstatistiken zurücksetzen", "Datum ändern", "Wartungshistorie", "Information"]
current_menu_option, menu_active, change_date_active, view_statistics_active, view_info_active, view_maintenance_history_active = 0, False, False, False, False, False
version = "2.2.6"
# Wartungshistorie Auswahl
maintenance_history_selected = 0
# Statistik-Seitenumschaltung
statistics_page = 0  # 0 = Gesamtstatistik, 1 = Bohnenstatistik
# Neue globale Variablen
drink_menu_active = False
drink_menu_options = ["lungo", "iced latte", "affogato", "shakerato", "espresso tonic", "other"]
current_drink_menu_option = 0
drink_counts = [0] * len(drink_menu_options)

# Battery-Reminder-Status
battery_reminder_active = False

# Packungstracking
bean_pack_input_active = False
bean_pack_sizes = [125, 200, 250, 500, 750, 1000]
bean_pack_size_index = 5  # Standardwert: 1000g

# Wartungsstatus
maintenance_status_file = "maintenance_status.json"

def load_maintenance_status():
    if maintenance_status_file in uos.listdir():
        try:
            with open(maintenance_status_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden von maintenance_status.json: {e}")
            show_error(f"Fehler in maintenance_status.json: {e}")
            return {}
    return {}

def save_maintenance_status(status):
    with open(maintenance_status_file, 'w') as f:
        json.dump(status, f)

def load_maintenance_config():
    if "maintenance_config.json" in uos.listdir():
        try:
            with open("maintenance_config.json", 'r') as f:
                data = json.load(f)
                if "tasks" in data and isinstance(data["tasks"], list):
                    return data["tasks"]
                else:
                    print("Fehler: 'tasks' fehlt oder ist kein Array in maintenance_config.json")
                    show_error("Fehlerhafte maintenance_config.json: 'tasks' fehlt oder ist kein Array")
                    return []
        except Exception as e:
            print(f"Fehler beim Laden von maintenance_config.json: {e}")
            show_error(f"Fehler in maintenance_config.json: {e}")
            return []
    else:
        print("maintenance_config.json nicht gefunden")
        show_error("maintenance_config.json nicht gefunden")
        return []
def show_error(msg):
    display.set_update_speed(badger2040.UPDATE_NORMAL)
    display.set_pen(0)
    display.clear()
    display.set_pen(15)
    display.text("FEHLER!", 10, 30, scale=2)
    display.text(msg, 10, 60, scale=1)
    display.update()

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

def save_data(date, espresso, cappuccino, drink_counts):
    if log_file not in uos.listdir():
        with open(log_file, 'w') as file:
            headers = "Datum,Espresso,Cappuccino," + ",".join(drink_menu_options)
            file.write(headers + "\n")
    lines = []
    with open(log_file, 'r') as file:
        lines = file.readlines()
    
    updated = False
    for i, line in enumerate(lines):
        parts = line.strip().split(',')
        # Nur Tageszeilen (mindestens 3 Felder, kein Wartungseintrag)
        if line.startswith(date) and len(parts) > 2 and not parts[1].startswith("WARTUNG:"):
            parts[1] = str(espresso)
            parts[2] = str(cappuccino)
            for j in range(3, 3 + len(drink_counts)):
                parts[j] = str(drink_counts[j - 3])
            lines[i] = ','.join(parts) + '\n'
            updated = True
            break
    
    if not updated:
        drink_counts_str = ",".join(map(str, drink_counts))
        lines.append(f'{date},{espresso},{cappuccino},{drink_counts_str}\n')
    
    with open(log_file, 'w') as file:
        file.write(''.join(lines))
    print(f"Data saved: {date}, {espresso}, {cappuccino}, {drink_counts}")

def nap():
    global menu_active, view_statistics_active, change_date_active, view_info_active, drink_menu_active
    print("System will turn off in 5 seconds...")
    # Hauptbildschirm anzeigen
    menu_active = False
    view_statistics_active = False
    change_date_active = False
    view_info_active = False
    drink_menu_active = False
    update_display(True)
    for i in range(5, 0, -1):
        print(f"{i}...")
        for _ in range(5):
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            time.sleep(0.1)
    display.set_update_speed(badger2040.UPDATE_FAST)
    display.set_pen(4)
    text1 = "wake me up"
    text2 = "when the caffeine ends"
    text_width1 = display.measure_text(text1, 2)
    text_width2 = display.measure_text(text2, 2)
    display.text(text1, (WIDTH - text_width1) // 2, (HEIGHT // 2) - 20, scale=2)
    display.text(text2, (WIDTH - text_width2) // 2, (HEIGHT // 2), scale=2)
    display.update()
    time.sleep(1)

    print("System turned off")
    display.halt()

    # Nach dem Aufwachen Zähler aus Logdatei laden
    load_counters_from_log(log_file)

def update_file(file, content):
    with open(file, 'w') as f:
        f.write(content)

current_date = get_from_file(date_file, time.mktime((2025, 2, 5, 0, 0, 0, 0, 0, -1)), parse_date)
count_values = get_from_file(count_file, "0,0,0").split(',')
# Robust gegen zu viele/wenige Werte
espresso_count = int(count_values[0]) if len(count_values) > 0 else 0
cappuccino_count = int(count_values[1]) if len(count_values) > 1 else 0
battery_reminder_count = int(count_values[2]) if len(count_values) > 2 else 0
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
    # Nach dem Zurücksetzen auch die aktuellen Zähler im RAM zurücksetzen
    global espresso_count, cappuccino_count, drink_counts
    espresso_count = 0
    cappuccino_count = 0
    drink_counts = [0] * len(drink_menu_options)

def calculate_total_statistics_and_first_date():
    if log_file not in uos.listdir():
        return 0, 0, 0, None
    total_espresso, total_cappuccino, total_other = 0, 0, 0
    first_date = None
    with open(log_file, 'r') as file:
        lines = file.readlines()[1:]  # Skip header line
        for line in lines:
            parts = line.strip().split(',')
            # Nur Tageszeilen (mindestens 3 Felder, kein Wartungseintrag)
            if len(parts) > 2 and not parts[1].startswith("WARTUNG:"):
                date, espresso, cappuccino, *drink_counts = parts
                total_espresso += int(espresso)
                total_cappuccino += int(cappuccino)
                total_other += sum(map(int, drink_counts))
                if first_date is None:
                    first_date = date
    return total_espresso, total_cappuccino, total_other, first_date

# Wartungswarnung-Status
maintenance_warning_hidden = False
maintenance_warning_tasks = []

def check_maintenance_warnings():
    global maintenance_warning_tasks
    tasks = load_maintenance_config()
    status = load_maintenance_status()
    warnings = []
    today = int(time.mktime(time.localtime(current_date)) // 86400)  # Tag als Zahl
    total_drinks = espresso_count + cappuccino_count + sum(drink_counts)
    # Finde das erste Tagesdatum im Logfile
    first_day = today
    if log_file in uos.listdir():
        with open(log_file, 'r') as file:
            lines = file.readlines()[1:]
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) > 2 and not parts[1].startswith("WARTUNG:"):
                    try:
                        first_day = int(time.mktime(time.strptime(parts[0], "%d.%m.%Y")) // 86400)
                    except Exception:
                        first_day = today
                    break
    for task in tasks:
        last_done = status.get(task["name"], first_day)
        interval = task["interval"]
        if task["name"] == "brew_group_cleaning":
            last_drinks = status.get("brew_group_cleaning_drinks", 0)
            drink_limit = task.get("drink_limit", 150)
            if (today - last_done >= interval) or (total_drinks - last_drinks >= drink_limit):
                warnings.append(task["name"])
        else:
            if today - last_done >= interval:
                warnings.append(task["name"])
    maintenance_warning_tasks = warnings
    return warnings

def update_display(full_update=False):
    global statistics_page
    if view_maintenance_history_active:
        global menu_active, maintenance_history_selected
        menu_active = False
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Wartungshistorie", 10, 2)
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        wartung_dict = {}
        if log_file in uos.listdir():
            with open(log_file, 'r') as file:
                lines = file.readlines()[1:]
                for line in lines:
                    parts = line.strip().split(',')
                    if len(parts) == 2 and parts[1].startswith("WARTUNG:"):
                        typ = parts[1][8:]
                        wartung_dict[typ] = parts[0]
        wartungstypen = [
            ("cleaning", "Reinigung"),
            ("descaling", "Entkalken"),
            ("brew_group_cleaning", "Brühgruppe reinigen"),
            ("grinder_cleaning", "Mühle reinigen"),
            ("deep_cleaning", "Grundreinigung")
        ]
        for i, (typ, name) in enumerate(wartungstypen):
            datum = wartung_dict.get(typ, "")
            prefix = "> " if i == maintenance_history_selected else "  "
            if datum:
                # Jahr als '25 anzeigen
                try:
                    tag, monat, jahr = datum.split('.')
                    jahr_kurz = jahr[-2:]
                    datum_kurz = f"{tag}.{monat}.'{jahr_kurz}"
                except Exception:
                    datum_kurz = datum
                display.text(f"{prefix}{name}: {datum_kurz}", 10, 30 + i*18)
            else:
                display.text(f"{prefix}{name}: ", 10, 30 + i*18)
        display.update()
        return
    global refresh_count, maintenance_warning_hidden
    # Wartungswarnungen prüfen
    maintenance_warnings = check_maintenance_warnings()
    if battery_reminder_active:
        display.set_update_speed(badger2040.UPDATE_NORMAL)
        display.set_pen(0)
        display.clear()
        display.set_pen(15)
        display.text("Batterien wechseln!", 10, 50, scale=2)
        display.update()
        return
    if maintenance_warnings and not maintenance_warning_hidden:
        display.set_update_speed(badger2040.UPDATE_NORMAL)
        display.set_pen(0)
        display.clear()
        display.set_pen(15)
        display.text("Wartung fällig!", 10, 30, scale=2)
        for i, warn in enumerate(maintenance_warnings):
            display.text(warn, 10, 60 + i*20, scale=1)
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
        display.set_font("bitmap8")
        if statistics_page == 0:
            # Seite 0: Gesamtstatistik
            total_espresso, total_cappuccino, total_other, first_date = calculate_total_statistics_and_first_date()
            display.text("Gesamtstatistiken", 10, 22)
            # Tagesschnitt berechnen
            log_days = 0
            espresso_avg = cappuccino_avg = other_avg = 0
            if log_file in uos.listdir():
                with open(log_file, 'r') as file:
                    lines = file.readlines()[1:]
                    log_days = len([l for l in lines if len(l.strip().split(',')) > 2 and not l.strip().split(',')[1].startswith("WARTUNG:")])
            espresso_avg = total_espresso / log_days if log_days > 0 else 0
            cappuccino_avg = total_cappuccino / log_days if log_days > 0 else 0
            other_avg = total_other / log_days if log_days > 0 else 0
            display.text(f"Espresso {total_espresso} ({espresso_avg:.1f} pro Tag)", 10, 44)
            display.text(f"Cappuccino {total_cappuccino} ({cappuccino_avg:.1f} pro Tag)", 10, 66)
            display.text(f"Andere Getränke {total_other} ({other_avg:.1f} pro Tag)", 10, 88)
            display.text(f"Seit: {first_date}" if first_date else "Keine Daten verfügbar", 10, 110)
            total_drinks = total_espresso + total_cappuccino + total_other
            display.text(f"Kaffee gesamt: {total_drinks}", 10, 132)
        elif statistics_page == 1:
            # Seite 1: Bohnenstatistik
            display.text("Bohnenstatistik", 10, 22)
            bean_pack_size = bean_pack_sizes[bean_pack_size_index]
            log_days = 0
            total_beans_used = 0
            if log_file in uos.listdir():
                with open(log_file, 'r') as file:
                    lines = file.readlines()[1:]
                    for line in lines:
                        parts = line.strip().split(',')
                        # Nur Tageszeilen (mindestens 3 Felder, kein Wartungseintrag)
                        if len(parts) > 2 and not parts[1].startswith("WARTUNG:"):
                            log_days += 1
                            date, espresso, cappuccino, *other = parts
                            total_beans_used += int(espresso)*8 + int(cappuccino)*16 + sum(map(int, other))*10
            days_per_pack = bean_pack_size / (total_beans_used / log_days) if log_days > 0 and total_beans_used > 0 else 0
            grams_per_day = total_beans_used / log_days if log_days > 0 else 0
            # Anzeige der Packungsgröße entfernt
            display.text(f"Tage pro Packung: {days_per_pack:.1f}", 10, 66)
            display.text(f"Gramm pro Tag: {grams_per_day:.1f}", 10, 88)
        else:
            display.text("Unbekannte Statistik-Seite", 10, 22)
    elif view_info_active:
        display.set_font("bitmap8")
        display.text("Information", 10, 22)
        display.text(f"Version: {version}", 10, 44)
        display.text("by Joao Neisinger", 10, 66)
        display.text("Lizenz: GNU GPLv3", 10, 88)
    elif drink_menu_active:
        display.set_font("bitmap8")  # Schriftart auf bitmap8 setzen
        for i, option in enumerate(drink_menu_options):
            display.text("> " + option if i == current_drink_menu_option else option, 10, 22 + i * 18)  # Abstand zu oberem Rand auf 22 Pixel gesetzt
    elif menu_active:
        display.set_font("bitmap8")  # Schriftart auf bitmap8 setzen
        for i, option in enumerate(menu_options):
            display.text("> " + option if i == current_menu_option else option, 10, 22 + i * 18)  # Abstand zu oberem Rand auf 22 Pixel gesetzt
    else:
        # Zähler und Labels am unteren Bildschirmrand
        terms = ["ESPRESSO", "CAPPU", "ANDERES"]
        counts = [espresso_count, cappuccino_count, sum(drink_counts)]
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
                if line.startswith(date):
                    parts = line.strip().split(',')
                    parts[1] = '0'  # Reset espresso count
                    parts[2] = '0'  # Reset cappuccino count
                    for j in range(3, len(parts)):
                        parts[j] = '0'  # Reset additional counts
                    file.write(','.join(parts) + '\n')
                else:
                    file.write(line)
    # Nach dem Zurücksetzen auch die aktuellen Zähler im RAM zurücksetzen
    global espresso_count, cappuccino_count, drink_counts
    espresso_count = 0
    cappuccino_count = 0
    drink_counts = [0] * len(drink_menu_options)

def load_counters_from_log(log_file):
    global espresso_count, cappuccino_count, drink_counts
    if log_file in uos.listdir():
        with open(log_file, 'r') as file:
            lines = file.readlines()
            # Suche die letzte Tageszeile (kein "WARTUNG:" im zweiten Feld)
            for line in reversed(lines[1:]):  # Überspringe Header
                parts = line.strip().split(',')
                if len(parts) > 2 and not parts[1].startswith("WARTUNG:"):
                    try:
                        espresso_count = int(parts[1])
                        cappuccino_count = int(parts[2])
                        drink_counts = list(map(int, parts[3:]))
                    except Exception:
                        espresso_count = 0
                        cappuccino_count = 0
                        drink_counts = [0] * len(drink_menu_options)
                    break

def button_pressed(pin):
    global espresso_count, cappuccino_count, current_date, button_press_count, menu_active, current_menu_option, change_date_active, view_statistics_active, view_info_active, battery_reminder_active, drink_menu_active, current_drink_menu_option, drink_counts, battery_reminder_count, temp_date, last_interaction_time, maintenance_warning_hidden, maintenance_warning_tasks, view_maintenance_history_active, statistics_page

    last_interaction_time = time.time()  # Update last interaction time on button press
    button_name = {BUTTON_A: "A", BUTTON_B: "B", BUTTON_C: "C", BUTTON_UP: "UP", BUTTON_DOWN: "DOWN"}.get(pin, "Unknown")
    print(f"Button pressed: {button_name}, last interaction time updated")

    if battery_reminder_active:
        if display.pressed(BUTTON_A):
            battery_reminder_active = False
            battery_reminder_count = 0
            save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, drink_counts)
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
        if display.pressed(BUTTON_UP):
            statistics_page = (statistics_page - 1) % 2  # Zwei Seiten: 0 und 1
            update_display(False)
            return
        if display.pressed(BUTTON_DOWN):
            statistics_page = (statistics_page + 1) % 2
            update_display(False)
            return
        if display.pressed(BUTTON_C): 
            view_statistics_active = False
            update_display(False)
            return
        update_display(False)
        return

    if view_info_active:
        if display.pressed(BUTTON_C): 
            view_info_active = False
        update_display(False)
        return

    if drink_menu_active:
        if display.pressed(BUTTON_UP):
            current_drink_menu_option = (current_drink_menu_option - 1) % len(drink_menu_options)
            print(f"BUTTON_UP pressed in drink_menu_active: {current_drink_menu_option}")
        elif display.pressed(BUTTON_DOWN):
            current_drink_menu_option = (current_drink_menu_option + 1) % len(drink_menu_options)
        elif display.pressed(BUTTON_A):
            if 0 <= current_drink_menu_option < len(drink_counts):
                drink_counts[current_drink_menu_option] += 1
                save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, drink_counts)
            drink_menu_active = False  # Menü schließen
        elif display.pressed(BUTTON_C):
            drink_menu_active = False
        update_display(False)
        return

    if display.pressed(BUTTON_UP):
        current_menu_option = (current_menu_option - 1) % len(menu_options) if menu_active else 0
        menu_active = True if not menu_active else menu_active
        print(f"BUTTON_UP pressed: {current_menu_option}, menu_active: {menu_active}")
        update_display(False)
        return

    if view_maintenance_history_active:
        global maintenance_history_selected
        wartungstypen = [
            ("cleaning", "Reinigung"),
            ("descaling", "Entkalken"),
            ("brew_group_cleaning", "Brühgruppe reinigen"),
            ("grinder_cleaning", "Mühle reinigen"),
            ("deep_cleaning", "Grundreinigung")
        ]
        if display.pressed(BUTTON_UP):
            maintenance_history_selected = (maintenance_history_selected - 1) % len(wartungstypen)
            update_display(False)
            return
        if display.pressed(BUTTON_DOWN):
            maintenance_history_selected = (maintenance_history_selected + 1) % len(wartungstypen)
            update_display(False)
            return
        if display.pressed(BUTTON_A):
            # Wartungseintrag auf heute setzen
            typ = wartungstypen[maintenance_history_selected][0]
            datum = format_date(time.localtime(current_date))
            wartung_eintrag = f'{datum},WARTUNG:{typ}'
            if log_file not in uos.listdir():
                with open(log_file, 'w') as file:
                    headers = "Datum,Espresso,Cappuccino," + ",".join(drink_menu_options)
                    file.write(headers + "\n")
            with open(log_file, 'a') as file:
                file.write(wartung_eintrag + "\n")
            status = load_maintenance_status()
            today_num = int(time.mktime(time.localtime(current_date)) // 86400)
            status[typ] = today_num
            if typ == "brew_group_cleaning":
                total_drinks = espresso_count + cappuccino_count + sum(drink_counts)
                status["brew_group_cleaning_drinks"] = total_drinks
            save_maintenance_status(status)
            update_display(True)
            return
        if display.pressed(BUTTON_C):
            view_maintenance_history_active = False
            menu_active = True
            update_display(True)
            return
        update_display(True)
        return
    if display.pressed(BUTTON_DOWN):
        current_menu_option = (current_menu_option + 1) % len(menu_options) if menu_active else 0
        if not menu_active:
            save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, drink_counts)
            current_date += 86400
            update_file(date_file, format_date(time.localtime(current_date)))
            espresso_count = 0
            cappuccino_count = 0
            battery_reminder_count += 1
            drink_counts = [0] * len(drink_menu_options)  # Reset additional counts
            battery_reminder_active = battery_reminder_count >= 10
            button_press_count = 0
            update_display(True)
    if view_maintenance_history_active:
        global maintenance_history_selected
        wartungstypen = [
            ("cleaning", "Reinigung"),
            ("descaling", "Entkalken"),
            ("brew_group_cleaning", "Brühgruppe reinigen"),
            ("grinder_cleaning", "Mühle reinigen"),
            ("deep_cleaning", "Grundreinigung")
        ]
        if display.pressed(BUTTON_UP):
            maintenance_history_selected = (maintenance_history_selected - 1) % len(wartungstypen)
            update_display(False)
            return
        if display.pressed(BUTTON_DOWN):
            maintenance_history_selected = (maintenance_history_selected + 1) % len(wartungstypen)
            update_display(False)
            return
        if display.pressed(BUTTON_A):
            # Wartungseintrag auf heute setzen
            typ = wartungstypen[maintenance_history_selected][0]
            datum = format_date(time.localtime(current_date))
            # Logfile ergänzen
            wartung_eintrag = f'{datum},WARTUNG:{typ}'
            if log_file not in uos.listdir():
                with open(log_file, 'w') as file:
                    headers = "Datum,Espresso,Cappuccino," + ",".join(drink_menu_options)
                    file.write(headers + "\n")
            with open(log_file, 'a') as file:
                file.write(wartung_eintrag + "\n")
            # Status aktualisieren
            status = load_maintenance_status()
            today_num = int(time.mktime(time.localtime(current_date)) // 86400)
            status[typ] = today_num
            if typ == "brew_group_cleaning":
                total_drinks = espresso_count + cappuccino_count + sum(drink_counts)
                status["brew_group_cleaning_drinks"] = total_drinks
            save_maintenance_status(status)
            update_display(True)
            return
        if display.pressed(BUTTON_C):
            view_maintenance_history_active = False
            menu_active = True
            update_display(True)
            return
        update_display(True)
        return

    if display.pressed(BUTTON_A):
        if menu_active:
            if current_menu_option == 0:
                drink_menu_active = True
            elif current_menu_option == 1:
                view_statistics_active = True
                statistics_page = 0  # Immer mit Seite 0 starten
            elif current_menu_option == 2:
                clear_today_log_entries(log_file, format_date(time.localtime(current_date)))
                espresso_count, cappuccino_count = 0, 0
            elif current_menu_option == 3:
                change_date_active, temp_date = True, current_date
            elif current_menu_option == 4:
                view_maintenance_history_active = True
                menu_active = False
                update_display(True)
            elif current_menu_option == 5:
                view_info_active = True
            update_display(True)
            return
        espresso_count += 1
        button_press_count += 1

    if display.pressed(BUTTON_B):
        if not menu_active:
            button_press_count += 1

    if display.pressed(BUTTON_C):
        if menu_active:
            if change_date_active: change_date_active = False
            elif view_statistics_active: view_statistics_active = False
            elif view_info_active: view_info_active = False
            else: menu_active = False
            update_display(True)
        else:
            drink_menu_active = True
        update_display(False)
        return

    # Entferne die Zählung von drink_counts[-1] außerhalb des Untermenüs

    # Wartungswarnung-Interaktion
    if check_maintenance_warnings() and not maintenance_warning_hidden:
        if display.pressed(BUTTON_A):
            # Markiere alle fälligen Aufgaben als erledigt
            status = load_maintenance_status()
            today = int(time.mktime(time.localtime(current_date)) // 86400)
            total_drinks = espresso_count + cappuccino_count + sum(drink_counts)
            for task in maintenance_warning_tasks:
                status[task] = today
                if task == "brew_group_cleaning":
                    status["brew_group_cleaning_drinks"] = total_drinks
                # Wartungsaktion ins Logfile schreiben
                # Format: Datum,WARTUNG:typ
                wartung_eintrag = f'{format_date(time.localtime(current_date))},WARTUNG:{task}'
                # Logfile ergänzen
                if log_file not in uos.listdir():
                    with open(log_file, 'w') as file:
                        headers = "Datum,Espresso,Cappuccino," + ",".join(drink_menu_options)
                        file.write(headers + "\n")
                with open(log_file, 'a') as file:
                    file.write(wartung_eintrag + "\n")
            save_maintenance_status(status)
            maintenance_warning_hidden = False
            update_display(True)
            return
        if display.pressed(BUTTON_C):
            maintenance_warning_hidden = True
            update_display(True)
            return

    update_display(False)
    if button_press_count >= 10:
        update_display(True)
        button_press_count = 0
    save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, drink_counts)

if __name__ == "__main__":
    current_date = get_from_file(date_file, time.mktime((2025, 2, 5, 0, 0, 0, 0, 0, -1)), parse_date)
    count_values = get_from_file(count_file, "0,0,0").split(',')
    # Robust gegen zu viele/wenige Werte
    espresso_count = int(count_values[0]) if len(count_values) > 0 else 0
    cappuccino_count = int(count_values[1]) if len(count_values) > 1 else 0
    battery_reminder_count = int(count_values[2]) if len(count_values) > 2 else 0
    button_press_count, temp_date, refresh_count = 0, current_date, 0

    load_counters_from_log(log_file)
    print("Counters initialized")

    led.value(1)
    update_display(True)
    last_interaction_time = time.time()
    debounce_time = 0.2
    last_button_press_time = {BUTTON_A: 0, BUTTON_B: 0, BUTTON_C: 0, BUTTON_UP: 0, BUTTON_DOWN: 0}

    while True:
        current_time = time.time()
        for btn in [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP, BUTTON_DOWN]:
            if display.pressed(btn):
                time.sleep(0.05)
                if display.pressed(btn) and (current_time - last_button_press_time[btn] > debounce_time):
                    button_pressed(btn)
                    last_button_press_time[btn] = current_time
                    break
            else:
                last_button_press_time[btn] = 0

        if time.time() - last_interaction_time > 15:
            nap()
