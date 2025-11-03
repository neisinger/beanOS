import badger2040, machine, time, json, uos

# Initialisierung des Badger2040
display = badger2040.Badger2040()
display.set_font("bitmap8")  # Schriftart ändern
WIDTH, HEIGHT = 296, 128
BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP, BUTTON_DOWN, LED = badger2040.BUTTON_A, badger2040.BUTTON_B, badger2040.BUTTON_C, badger2040.BUTTON_UP, badger2040.BUTTON_DOWN, 25
led = machine.Pin(LED, machine.Pin.OUT)
log_file, date_file, count_file = "kaffee_log.csv", "current_date.txt", "current_counts.txt"
menu_options = ["Bohnen", "Statistiken anzeigen", "Tagesstatistiken zurücksetzen", "Datum ändern", "Wartungshistorie", "Achievements", "Information"]
current_menu_option, menu_active, change_date_active, view_statistics_active, view_info_active, view_maintenance_history_active, view_achievements_active = 0, False, False, False, False, False, False
version = "2.3.1"
# Wartungshistorie Auswahl
maintenance_history_selected = 0
# Achievement Auswahl
achievement_selected = 0
# Statistik-Seitenumschaltung
statistics_page = 0  # 0 = Gesamtstatistik, 1 = Bohnenstatistik
# Neue globale Variablen
drink_menu_active = False
drink_menu_options = ["lungo", "iced latte", "affogato", "shakerato", "espresso tonic", "other"]
current_drink_menu_option = 0
drink_counts = [0] * len(drink_menu_options)

# Notification-System (für Achievements und Wartungen)
notification_active = False
notification_type = ""  # "achievement" oder "maintenance"
notification_data = {}
achievements_file = "achievements.json"

# Achievement-Status für Titelleiste
daily_achievement_unlocked = False

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

# Generisches Notification-System
def show_notification(notification_type, data):
    global notification_active, notification_data
    notification_active = True
    notification_data = {"type": notification_type, "data": data}

def handle_notification_display():
    global notification_active, notification_data
    if not notification_active:
        return False
    
    display.set_update_speed(badger2040.UPDATE_NORMAL)
    display.set_pen(15)
    display.clear()
    
    # Schwarzer Rahmen um die Benachrichtigung
    display.set_pen(0)
    display.rectangle(5, 20, WIDTH-10, HEIGHT-40)
    display.set_pen(15)
    display.rectangle(7, 22, WIDTH-14, HEIGHT-44)
    display.set_pen(0)
    
    if notification_data["type"] == "achievement":
        # Achievement-Benachrichtigung
        achievement_key = notification_data["data"]
        
        # Titel zentrieren
        title_text = "!! ACHIEVEMENT !!"
        title_width = display.measure_text(title_text, 2)
        title_x = (WIDTH - title_width) // 2
        display.text(title_text, title_x, 40, scale=2)
        
        # Achievement anzeigen
        definitions = get_achievement_definitions()
        if achievement_key in definitions:
            achievement = definitions[achievement_key]
            
            # Icon und Name zentriert
            icon_name = f"[{achievement['icon']}] {achievement['name']}"
            text_width = display.measure_text(icon_name, 2)
            x_centered = (WIDTH - text_width) // 2
            display.text(icon_name, x_centered, 70, scale=2)
        
        # Button-Hinweise
        ok_text = "OK"
        ok_x = 41 - display.measure_text(ok_text, 1) // 2  # A-Button Position
        display.text(ok_text, ok_x, HEIGHT - 15, scale=1)
        
    elif notification_data["type"] == "maintenance":
        # Wartungs-Benachrichtigung
        maintenance_warnings = notification_data["data"]
        
        # Titel zentrieren
        title_text = "!! WARTUNG FÄLLIG !!"
        title_width = display.measure_text(title_text, 2)
        title_x = (WIDTH - title_width) // 2
        display.text(title_text, title_x, 40, scale=2)
        
        # Wartungsaufgaben zentriert anzeigen
        y_pos = 70
        for i, warn in enumerate(maintenance_warnings):
            warn_names = {
                "cleaning": "Maschine reinigen",
                "descaling": "Maschine entkalken", 
                "brew_group_cleaning": "Brühgruppe reinigen",
                "grinder_cleaning": "Mahlwerk reinigen",
                "deep_cleaning": "Grundreinigung"
            }
            warn_display = warn_names.get(warn, warn)
            text_width = display.measure_text(warn_display, 2)
            x_centered = (WIDTH - text_width) // 2
            display.text(warn_display, x_centered, y_pos, scale=2)
            y_pos += 25
        
        # Button-Hinweise
        erledigt_text = "Erledigt"
        erledigt_x = 41 - display.measure_text(erledigt_text, 1) // 2
        display.text(erledigt_text, erledigt_x, HEIGHT - 15, scale=1)
        
        verstecken_text = "Verstecken"
        verstecken_x = 253 - display.measure_text(verstecken_text, 1) // 2
        display.text(verstecken_text, verstecken_x, HEIGHT - 15, scale=1)
    
    display.update()
    return True

def handle_notification_input():
    global notification_active, notification_data, maintenance_warning_hidden, daily_achievement_unlocked
    
    if notification_data["type"] == "achievement":
        if display.pressed(BUTTON_A) or display.pressed(BUTTON_B) or display.pressed(BUTTON_C):
            daily_achievement_unlocked = True  # Zeige Icon in Titelleiste
            notification_active = False
            notification_data = {}
            update_display(True)
            return True
            
    elif notification_data["type"] == "maintenance":
        if display.pressed(BUTTON_A):
            # Markiere nur die erste fällige Aufgabe als erledigt
            maintenance_warnings = notification_data["data"]
            status = load_maintenance_status()
            today = int(time.mktime(time.localtime(current_date)) // 86400)
            total_drinks = espresso_count + cappuccino_count + sum(drink_counts)
            
            if maintenance_warnings:
                task = maintenance_warnings[0]
                status[task] = today
                if task == "brew_group_cleaning":
                    status["brew_group_cleaning_drinks"] = total_drinks
                
                wartung_eintrag = f'{format_date(time.localtime(current_date))},WARTUNG:{task}'
                if log_file not in uos.listdir():
                    with open(log_file, 'w') as file:
                        headers = "Datum,Espresso,Cappuccino," + ",".join(drink_menu_options)
                        file.write(headers + "\n")
                with open(log_file, 'a') as file:
                    file.write(wartung_eintrag + "\n")
            
            save_maintenance_status(status)
            maintenance_warning_hidden = False
            notification_active = False
            notification_data = {}
            update_display(True)
            return True
            
        if display.pressed(BUTTON_C):
            maintenance_warning_hidden = True
            notification_active = False
            notification_data = {}
            update_display(True)
            return True
    
    return False
def load_achievements():
    if achievements_file in uos.listdir():
        try:
            with open(achievements_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden von achievements.json: {e}")
            return {}
    return {}

def save_achievements(achievements):
    try:
        with open(achievements_file, 'w') as f:
            json.dump(achievements, f)
    except Exception as e:
        print(f"Fehler beim Speichern von achievements.json: {e}")

def get_achievement_definitions():
    return {
        # Meilensteine
        "first_coffee": {"name": "Erster Kaffee", "desc": "Dein allererster Kaffee!", "icon": "1", "category": "Meilensteine"},
        "coffee_10": {"name": "Kaffee-Starter", "desc": "10 Kaffees getrunken", "icon": "10", "category": "Meilensteine"},
        "coffee_50": {"name": "Kaffee-Fan", "desc": "50 Kaffees getrunken", "icon": "50", "category": "Meilensteine"},
        "coffee_100": {"name": "Kaffee-Liebhaber", "desc": "100 Kaffees getrunken", "icon": "100", "category": "Meilensteine"},
        "coffee_500": {"name": "Kaffee-Experte", "desc": "500 Kaffees getrunken", "icon": "500", "category": "Meilensteine"},
        "coffee_1000": {"name": "Kaffee-Meister", "desc": "1000 Kaffees getrunken", "icon": "1K", "category": "Meilensteine"},
        
        # Streak-basiert
        "streak_7": {"name": "Wochenentkämpfer", "desc": "7 Tage in Folge Kaffee", "icon": "7d", "category": "Streaks"},
        "streak_30": {"name": "Monatsmarathon", "desc": "30 Tage in Folge Kaffee", "icon": "30d", "category": "Streaks"},
        
        # Spezialgetränke
        "stay_cool": {"name": "Stay Cool", "desc": "Ersten Iced Latte getrunken", "icon": "IC", "category": "Spezialgetränke"},
        "dessert": {"name": "Dessert", "desc": "Ersten Affogato getrunken", "icon": "AF", "category": "Spezialgetränke"},
        "shaker": {"name": "Shake it!", "desc": "Ersten Shakerato getrunken", "icon": "SH", "category": "Spezialgetränke"},
        
        # Wartungsbezogen
        "maintenance_master": {"name": "Wartungsmeister", "desc": "Alle Wartungen rechtzeitig", "icon": "WM", "category": "Wartung"},
        "clean_machine": {"name": "Saubere Maschine", "desc": "Erste Wartung durchgeführt", "icon": "CL", "category": "Wartung"},
        
        # Experimentell
        "barista": {"name": "Barista", "desc": "Alle Getränketypen probiert", "icon": "BA", "category": "Experimentell"},
        "happy_bean_day": {"name": "Happy Bean Day", "desc": "10 Kaffees an einem Tag", "icon": "HB", "category": "Experimentell"}
    }

def check_achievements():
    global daily_achievement_unlocked
    achievements = load_achievements()
    definitions = get_achievement_definitions()
    new_achievements = []
    
    # Gesamtkaffee-Statistiken berechnen
    total_coffee = calculate_total_coffee_count()
    print(f"DEBUG: Total coffee count: {total_coffee}")
    
    # Meilenstein-Achievements
    milestones = [1, 10, 50, 100, 500, 1000]
    achievement_keys = ["first_coffee", "coffee_10", "coffee_50", "coffee_100", "coffee_500", "coffee_1000"]
    
    for i, milestone in enumerate(milestones):
        key = achievement_keys[i]
        already_has = key in achievements
        print(f"DEBUG: Checking {key} - milestone: {milestone}, total: {total_coffee}, has: {already_has}")
        if total_coffee >= milestone and key not in achievements:
            achievements[key] = format_date(time.localtime(current_date))
            new_achievements.append(key)
            print(f"DEBUG: NEW ACHIEVEMENT: {key}")
    
    # Happy Bean Day Debug
    today_drinks = espresso_count + cappuccino_count + sum(drink_counts)
    print(f"DEBUG: Today drinks: {today_drinks}, Happy Bean Day check: {all_drinks_today()}")
    
    # Getränke-spezifische Achievements
    if has_drunk_drink("iced latte") and "stay_cool" not in achievements:
        achievements["stay_cool"] = format_date(time.localtime(current_date))
        new_achievements.append("stay_cool")
    
    if has_drunk_drink("affogato") and "dessert" not in achievements:
        achievements["dessert"] = format_date(time.localtime(current_date))
        new_achievements.append("dessert")
    
    if has_drunk_drink("shakerato") and "shaker" not in achievements:
        achievements["shaker"] = format_date(time.localtime(current_date))
        new_achievements.append("shaker")
    
    # Barista Achievement (alle Getränke probiert)
    if all_drinks_tried() and "barista" not in achievements:
        achievements["barista"] = format_date(time.localtime(current_date))
        new_achievements.append("barista")
    
    # Happy Bean Day (10 Kaffees an einem Tag)
    if all_drinks_today() and "happy_bean_day" not in achievements:
        achievements["happy_bean_day"] = format_date(time.localtime(current_date))
        new_achievements.append("happy_bean_day")
    
    # Wartungs-Achievements
    if has_done_maintenance() and "clean_machine" not in achievements:
        achievements["clean_machine"] = format_date(time.localtime(current_date))
        new_achievements.append("clean_machine")
    
    # Streak-Achievements
    current_streak = calculate_coffee_streak()
    if current_streak >= 7 and "streak_7" not in achievements:
        achievements["streak_7"] = format_date(time.localtime(current_date))
        new_achievements.append("streak_7")
    
    if current_streak >= 30 and "streak_30" not in achievements:
        achievements["streak_30"] = format_date(time.localtime(current_date))
        new_achievements.append("streak_30")
    
    # Speichere Achievements und zeige Benachrichtigung
    if new_achievements:
        save_achievements(achievements)
        show_notification("achievement", new_achievements[0])  # Zeige das erste neue Achievement
        print(f"DEBUG: Showing achievement notification for: {new_achievements[0]}")
    
    return new_achievements

def calculate_total_coffee_count():
    # Hole historische Daten aus dem Logfile
    total_espresso, total_cappuccino, total_other, _ = calculate_total_statistics_and_first_date()
    
    # Addiere die aktuellen Zähler für heute (falls sie noch nicht gespeichert wurden)
    current_total = espresso_count + cappuccino_count + sum(drink_counts)
    
    # Prüfe, ob die heutigen Daten bereits im Logfile sind
    today_str = format_date(time.localtime(current_date))
    today_in_log = get_day_total_coffee(today_str)
    
    # Falls heute noch nicht im Log ist, addiere die aktuellen Zähler
    if today_in_log == 0 and current_total > 0:
        return total_espresso + total_cappuccino + total_other + current_total
    else:
        return total_espresso + total_cappuccino + total_other

def has_drunk_drink(drink_name):
    if log_file not in uos.listdir():
        return False
    
    drink_index = drink_menu_options.index(drink_name) if drink_name in drink_menu_options else -1
    if drink_index == -1:
        return False
    
    with open(log_file, 'r') as file:
        lines = file.readlines()[1:]  # Skip header
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) > 3 + drink_index and not parts[1].startswith("WARTUNG:"):
                if int(parts[3 + drink_index]) > 0:
                    return True
    return False

def all_drinks_tried():
    for drink in drink_menu_options:
        if not has_drunk_drink(drink):
            return False
    return True

def all_drinks_today():
    today_str = format_date(time.localtime(current_date))
    
    # Hole gespeicherte Daten für heute
    today_in_log = get_day_total_coffee(today_str)
    
    # Addiere aktuelle Zähler (falls noch nicht gespeichert)
    current_total = espresso_count + cappuccino_count + sum(drink_counts)
    
    # Falls heute noch nicht im Log oder Log-Wert ist kleiner als aktuelle Zähler
    if today_in_log == 0 or current_total > today_in_log:
        total_today = current_total
    else:
        total_today = today_in_log
    
    return total_today >= 10

def has_done_maintenance():
    if log_file not in uos.listdir():
        return False
    
    with open(log_file, 'r') as file:
        lines = file.readlines()[1:]  # Skip header
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) == 2 and parts[1].startswith("WARTUNG:"):
                return True
    return False

def calculate_coffee_streak():
    if log_file not in uos.listdir():
        return 0
    
    streak = 0
    current_check_date = current_date
    
    while True:
        date_str = format_date(time.localtime(current_check_date))
        day_total = get_day_total_coffee(date_str)
        
        if day_total > 0:
            streak += 1
            current_check_date -= 86400  # Ein Tag zurück
        else:
            break
    
    return streak

def get_day_total_coffee(date_str):
    if log_file not in uos.listdir():
        return 0
    
    with open(log_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith(date_str):
                parts = line.strip().split(',')
                if len(parts) >= 3 and not parts[1].startswith("WARTUNG:"):
                    espresso = int(parts[1]) if parts[1].isdigit() else 0
                    cappuccino = int(parts[2]) if parts[2].isdigit() else 0
                    other = sum(int(parts[i]) for i in range(3, len(parts)) if parts[i].isdigit())
                    return espresso + cappuccino + other
    return 0

def draw_progress_bar(x, y, current, maximum):
    """Zeichnet einen Fortschrittsbalken mit kleinen Kästchen"""
    box_width = 6
    box_height = 6
    box_spacing = 2
    total_width = min(maximum, 20) * (box_width + box_spacing) - box_spacing  # Max 20 Kästchen für Platz
    
    # Zeichne die Kästchen
    for i in range(min(maximum, 20)):  # Maximal 20 Kästchen anzeigen
        box_x = x + i * (box_width + box_spacing)
        
        if i < current:
            # Gefülltes Kästchen (erreicht)
            display.rectangle(box_x, y, box_width, box_height)
        else:
            # Leeres Kästchen (nicht erreicht) - nur Rand zeichnen
            display.set_pen(0)
            display.rectangle(box_x, y, box_width, 1)  # Oben
            display.rectangle(box_x, y + box_height - 1, box_width, 1)  # Unten  
            display.rectangle(box_x, y, 1, box_height)  # Links
            display.rectangle(box_x + box_width - 1, y, 1, box_height)  # Rechts
    
    # Fortschrittstext rechts neben den Kästchen
    progress_text = f"{current}/{maximum}"
    text_x = x + total_width + 10
    display.text(progress_text, text_x, y - 1, scale=1)

def show_error(msg):
    display.set_update_speed(badger2040.UPDATE_NORMAL)
    display.set_pen(0)
    display.clear()
    display.set_pen(15)
    display.text("FEHLER!", 10, 30, scale=2)
    display.text(msg, 10, 60, scale=1)
    display.update()

def debug_display_content():
    """Debug-Funktion: Gibt den aktuellen Bildschirminhalt in der Konsole aus"""
    print("=== DISPLAY DEBUG ===")
    print("Achievement Screen Content:")
    
    achievements = load_achievements()
    definitions = get_achievement_definitions()
    
    # Gleiche Logik wie im Display
    categories = {}
    for key, achievement in definitions.items():
        category = achievement.get("category", "Andere")
        date = achievements.get(key, None)
        
        if date or category == "Streaks":
            if category not in categories:
                categories[category] = []
            categories[category].append((key, date, achievement))
    
    if not categories:
        print("  Noch keine Achievements erreicht!")
        return
    
    # Sortiere und erstelle Display-Liste
    category_order = ["Meilensteine", "Streaks", "Spezialgetränke", "Wartung", "Experimentell", "Andere"]
    sorted_categories = []
    for cat in category_order:
        if cat in categories:
            sorted_categories.append((cat, categories[cat]))
    
    display_items = []
    for category, items in sorted_categories:
        display_items.append(("category", category, ""))
        for key, date, achievement in items:
            display_items.append(("achievement", key, date, achievement))
    
    print(f"Total display items: {len(display_items)}")
    print(f"Current selection: {achievement_selected}")
    
    # Zeige alle Items wie sie dargestellt werden
    for i, item in enumerate(display_items):
        prefix = "> " if i == achievement_selected else "  "
        
        if item[0] == "category":
            category_name = item[1]
            print(f"[{i:2d}] {prefix}=== {category_name} ===")
        else:
            key, date, achievement = item[1], item[2], item[3]
            if date:
                name_text = f"{prefix}[{achievement['icon']}] {achievement['name']}"
                print(f"[{i:2d}] {name_text} | {date}")
            else:
                name_text = f"{prefix}[ ] {achievement['name']}"
                print(f"[{i:2d}] {name_text} | Nicht erreicht")
            print(f"     Desc: {achievement['desc']}")
            
            # Progress bar info für Streaks
            if key in ["streak_7", "streak_30"] and not date:
                current_streak = calculate_coffee_streak()
                max_streak = 7 if key == "streak_7" else 30
                print(f"     Progress: {current_streak}/{max_streak}")
    
    print("=== END DEBUG ===")

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
    global statistics_page, menu_active, achievement_selected
    
    # Prüfe zuerst auf Benachrichtigungen
    if handle_notification_display():
        return
    
    if view_maintenance_history_active:
        menu_active = False
        # Vollständiges Clearing für Wartungshistorie-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Wartungshistorie", 10, 2)
        
        # Datum rechts (ohne Achievement-Icon oder andere Störungen)
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 10, 2)
        
        # Weißer Hintergrund für Inhalt
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
        # Aktuelle Warnungen abrufen für die Markierung
        current_warnings = check_maintenance_warnings()
        for i, (typ, name) in enumerate(wartungstypen):
            datum = wartung_dict.get(typ, "")
            prefix = "> " if i == maintenance_history_selected else "  "
            # Fällige Wartung mit ! markieren
            warning_marker = "! " if typ in current_warnings else ""
            if datum:
                # Jahr als '25 anzeigen
                try:
                    tag, monat, jahr = datum.split('.')
                    jahr_kurz = jahr[-2:]
                    datum_kurz = f"{tag}.{monat}.'{jahr_kurz}"
                except Exception:
                    datum_kurz = datum
                display.text(f"{prefix}{warning_marker}{name}: {datum_kurz}", 10, 30 + i*18)
            else:
                display.text(f"{prefix}{warning_marker}{name}: ", 10, 30 + i*18)
        display.update()
        return
    if view_achievements_active:
        menu_active = False
        # Debug-Output für Achievement-Screen
        debug_display_content()
        
        # Vollständiges Clearing für Achievement-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Achievements", 10, 2)
        
        # Weißer Hintergrund für Inhalt
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        
        achievements = load_achievements()
        definitions = get_achievement_definitions()
        
        # Gruppiere erreichte Achievements + alle Streak-Achievements nach Kategorien
        categories = {}
        for key, achievement in definitions.items():
            category = achievement.get("category", "Andere")
            date = achievements.get(key, None)
            
            # Nur erreichte Achievements ODER Streak-Achievements anzeigen
            if date or category == "Streaks":
                if category not in categories:
                    categories[category] = []
                categories[category].append((key, date, achievement))
        
        # Sortiere Achievements innerhalb der Kategorien
        for category in categories:
            if category == "Meilensteine":
                # Sortiere Meilensteine nach der Zahl im Icon
                milestone_order = {"1": 1, "10": 10, "50": 50, "100": 100, "500": 500, "1K": 1000}
                categories[category].sort(key=lambda x: milestone_order.get(x[2]["icon"], 999))
            else:
                # Andere Kategorien alphabetisch nach Name
                categories[category].sort(key=lambda x: x[2]["name"])
        
        if not categories:
            display.text("  Noch keine Achievements", 10, 50)
            display.text("  erreicht!", 10, 68)
        else:
            # Sortiere Kategorien für konsistente Reihenfolge
            category_order = ["Meilensteine", "Streaks", "Spezialgetränke", "Wartung", "Experimentell", "Andere"]
            sorted_categories = []
            for cat in category_order:
                if cat in categories:
                    sorted_categories.append((cat, categories[cat]))
            
            # Erstelle flache Liste für Scroll-Navigation
            display_items = []
            for category, items in sorted_categories:
                display_items.append(("category", category, ""))  # Kategorie-Header
                for key, date, achievement in items:
                    display_items.append(("achievement", key, date, achievement))
            
            # Zeige maximal 3 Items gleichzeitig (wegen größerem Abstand)
            max_visible = 3
            total_items = len(display_items)
            
            # Bestimme Start-Index basierend auf aktueller Auswahl
            if achievement_selected < max_visible - 1:
                start_index = 0
            elif achievement_selected >= total_items - 1:
                start_index = max(0, total_items - max_visible)
            else:
                start_index = achievement_selected - 1
            
            end_index = min(total_items, start_index + max_visible)
            
            y_pos = 30
            for i in range(start_index, end_index):
                if i < len(display_items):
                    item = display_items[i]
                    prefix = "> " if i == achievement_selected else "  "
                    
                    if item[0] == "category":
                        # Kategorie-Header
                        category_name = item[1]
                        display.text(f"{prefix}=== {category_name} ===", 10, y_pos)
                        y_pos += 24
                    else:
                        # Achievement
                        key, date, achievement = item[1], item[2], item[3]
                        
                        # Zeile 1: [Icon] Name
                        if date:  # Achievement erreicht
                            name_text = f"{prefix}[{achievement['icon']}] {achievement['name']}"
                        else:  # Achievement nicht erreicht
                            name_text = f"{prefix}[ ] {achievement['name']}"
                        display.text(name_text, 10, y_pos)
                        
                        # Zeile 2: Datum rechtsbündig
                        if date:
                            date_x = WIDTH - display.measure_text(date, 1) - 49
                            display.text(date, date_x, y_pos + 12)
                        else:
                            not_reached_text = "Nicht erreicht"
                            not_reached_x = WIDTH - display.measure_text(not_reached_text, 1) - 49
                            display.text(not_reached_text, not_reached_x, y_pos + 12)
                        
                        # Zeile 3: Beschreibung
                        display.text(f"  {achievement['desc']}", 10, y_pos + 24)
                        
                        # Zeile 4: Fortschrittsbalken für Streak-Achievements (falls nicht erreicht)
                        if key in ["streak_7", "streak_30"] and not date:
                            current_streak = calculate_coffee_streak()
                            max_streak = 7 if key == "streak_7" else 30
                            draw_progress_bar(10, y_pos + 36, current_streak, max_streak)
                            y_pos += 52  # Mehr Platz für Fortschrittsbalken
                        else:
                            y_pos += 40  # Normaler Abstand: 3 Zeilen * 12px + 4px Abstand
            
            # Zeige Scroll-Indikatoren wenn nötig
            display.set_pen(0)  # Schwarz für Pfeile
            if start_index > 0:
                display.text("↑", WIDTH - 15, 30)
            if end_index < total_items:
                display.text("↓", WIDTH - 15, HEIGHT - 25)
        
        display.update()
        return
    global refresh_count, maintenance_warning_hidden
    # Wartungswarnungen prüfen (nur einmal)
    maintenance_warnings = check_maintenance_warnings()
    
    # Zeige Wartungswarnung über das Notification-System
    if maintenance_warnings and not maintenance_warning_hidden and not notification_active:
        show_notification("maintenance", maintenance_warnings)
        return
        
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
    # Balken-Beschriftung je nach Modus
    if view_statistics_active:
        if statistics_page == 0:
            balken_text = "Gesamtstatistik"
        elif statistics_page == 1:
            balken_text = "Bohnenstatistik"
        else:
            balken_text = "Statistik"
    elif view_info_active:
        balken_text = "Information"
    else:
        balken_text = "beanOS"
    display.text(balken_text, 10, 2)
    date_str = format_date(time.localtime(current_date))
    
    # Achievement-Icon zentriert in der Titelleiste
    if daily_achievement_unlocked:
        achievement_icon = "★"
        icon_width = display.measure_text(achievement_icon, 1)
        icon_x = (WIDTH - icon_width) // 2
        display.text(achievement_icon, icon_x, 2)
    
    # Datum rechts
    display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
    
    # Kleines Wartungsicon links vom Datum
    if maintenance_warnings and maintenance_warning_hidden:
        display.text("!", WIDTH - display.measure_text(date_str, 1) - 60, 2)

    display.set_pen(0)

    if change_date_active:
        date_str = format_date(time.localtime(temp_date))
        display.text(date_str, (WIDTH - display.measure_text(date_str, 2)) // 2, HEIGHT // 2 - 10, scale=2)
    elif view_statistics_active:
        display.set_font("bitmap8")
        if statistics_page == 0:
            # Seite 0: Gesamtstatistik
            total_espresso, total_cappuccino, total_other, first_date = calculate_total_statistics_and_first_date()
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
        display.text(f"Version: {version}", 10, 44)
        display.text("by Joao Neisinger", 10, 66)
        display.text("Lizenz: GNU GPLv3", 10, 88)
    elif drink_menu_active:
        display.set_font("bitmap8")  # Schriftart auf bitmap8 setzen
        for i, option in enumerate(drink_menu_options):
            display.text("> " + option if i == current_drink_menu_option else option, 10, 22 + i * 18)  # Abstand zu oberem Rand auf 22 Pixel gesetzt
    elif menu_active:
        display.set_font("bitmap8")  # Schriftart auf bitmap8 setzen
        
        # Berechne sichtbaren Bereich (maximal 5 Menüpunkte)
        max_visible = 5
        total_options = len(menu_options)
        
        # Bestimme Start-Index basierend auf aktueller Auswahl
        if current_menu_option < max_visible - 2:
            start_index = 0
        elif current_menu_option >= total_options - 2:
            start_index = max(0, total_options - max_visible)
        else:
            start_index = current_menu_option - 2
        
        end_index = min(total_options, start_index + max_visible)
        
        for i in range(start_index, end_index):
            option = menu_options[i]
            prefix = "> " if i == current_menu_option else "  "
            display_y = 22 + (i - start_index) * 18
            display.text(prefix + option, 10, display_y)
        
        # Zeige Scroll-Indikatoren wenn nötig
        if start_index > 0:
            display.text("↑", WIDTH - 15, 22)  # Pfeil nach oben
        if end_index < total_options:
            display.text("↓", WIDTH - 15, 22 + (max_visible - 1) * 18)  # Pfeil nach unten
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
    global espresso_count, cappuccino_count, current_date, button_press_count, menu_active, current_menu_option, change_date_active, view_statistics_active, view_info_active, battery_reminder_active, drink_menu_active, current_drink_menu_option, drink_counts, battery_reminder_count, temp_date, last_interaction_time, maintenance_warning_hidden, maintenance_warning_tasks, view_maintenance_history_active, view_achievements_active, notification_active, notification_data, achievement_selected, statistics_page, daily_achievement_unlocked

    last_interaction_time = time.time()  # Update last interaction time on button press
    button_name = {BUTTON_A: "A", BUTTON_B: "B", BUTTON_C: "C", BUTTON_UP: "UP", BUTTON_DOWN: "DOWN"}.get(pin, "Unknown")
    print(f"Button pressed: {button_name}, last interaction time updated")

    # Notification-System (muss ganz am Anfang stehen)
    if notification_active:
        if handle_notification_input():
            return

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
                check_achievements()  # Prüfe Achievements nach Getränk
            drink_menu_active = False  # Menü schließen
        elif display.pressed(BUTTON_C):
            drink_menu_active = False
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
            # Wartungswarnung zurücksetzen da eine Wartung durchgeführt wurde
            maintenance_warning_hidden = False
            check_achievements()  # Prüfe Achievements nach Wartung
            update_display(True)
            return
        if display.pressed(BUTTON_C):
            view_maintenance_history_active = False
            menu_active = True
            update_display(True)
            return
        update_display(True)
        return

    if view_achievements_active:
        # Lade erreichte Achievements für Navigation
        achievements = load_achievements()
        definitions = get_achievement_definitions()
        
        # Erstelle die gleiche Liste wie im Display (erreichte + Streak-Achievements)
        categories = {}
        for key, achievement in definitions.items():
            category = achievement.get("category", "Andere")
            date = achievements.get(key, None)
            
            # Nur erreichte Achievements ODER Streak-Achievements anzeigen
            if date or category == "Streaks":
                if category not in categories:
                    categories[category] = []
                categories[category].append((key, date, achievement))
        
        # Erstelle flache Liste für Navigation
        category_order = ["Meilensteine", "Streaks", "Spezialgetränke", "Wartung", "Experimentell", "Andere"]
        sorted_categories = []
        for cat in category_order:
            if cat in categories:
                sorted_categories.append((cat, categories[cat]))
        
        display_items = []
        for category, items in sorted_categories:
            display_items.append(("category", category, ""))
            for key, date, achievement in items:
                display_items.append(("achievement", key, date, achievement))
        
        if display_items:
            if display.pressed(BUTTON_UP):
                achievement_selected = (achievement_selected - 1) % len(display_items)
                update_display(False)
                return
            if display.pressed(BUTTON_DOWN):
                achievement_selected = (achievement_selected + 1) % len(display_items)
                update_display(False)
                return
        
        if display.pressed(BUTTON_C):
            view_achievements_active = False
            menu_active = True
            achievement_selected = 0  # Reset selection
            update_display(True)
            return
        update_display(True)
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
            save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, drink_counts)
            current_date += 86400
            update_file(date_file, format_date(time.localtime(current_date)))
            espresso_count = 0
            cappuccino_count = 0
            battery_reminder_count += 1
            drink_counts = [0] * len(drink_menu_options)  # Reset additional counts
            battery_reminder_active = battery_reminder_count >= 10
            button_press_count = 0
            daily_achievement_unlocked = False  # Achievement-Icon für neuen Tag zurücksetzen
            update_display(True)

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
                view_achievements_active = True
                menu_active = False
                update_display(True)
            elif current_menu_option == 6:
                view_info_active = True
            update_display(True)
            return
        espresso_count += 1
        button_press_count += 1
        check_achievements()  # Prüfe Achievements nach Espresso

    if display.pressed(BUTTON_B):
        if not menu_active:
            cappuccino_count += 1
            button_press_count += 1
            check_achievements()  # Prüfe Achievements nach Cappuccino

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
            # Nicht in den Schlafmodus gehen, wenn eine Wartungswarnung angezeigt wird
            maintenance_warnings = check_maintenance_warnings()
            if not (maintenance_warnings and not maintenance_warning_hidden):
                nap()
