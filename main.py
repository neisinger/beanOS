#!/usr/bin/env python3
"""
beanOS - Smart Coffee Consumption Tracker for Badger2040
========================================================

A comprehensive MicroPython application for tracking coffee consumption with 
gamification features, maintenance reminders, and detailed analytics.

Features:
- Coffee tracking (Espresso, Cappuccino, 6 additional drinks)
- Achievement system with 20+ unlockable achievements
- Smart maintenance reminders with time and usage-based triggers
- Comprehensive statistics and analytics
- Bean consumption tracking
- Daily streak monitoring
- Automatic data logging to CSV

Hardware Requirements:
- Pimoroni Badger2040 (RP2040-based e-ink display)
- MicroPython firmware

File Dependencies:
- maintenance_config.json: Maintenance task configuration
- kaffee_log.csv: Coffee consumption data (auto-created)
- achievements.json: Achievement progress (auto-created)
- maintenance_status.json: Maintenance tracking (auto-created)

Author: Joao Neisinger
License: GNU GPLv3
Version: 2.3.2
Repository: https://github.com/neisinger/beanOS

This code must not be used by fascists! No code for the AfD or Musk or Trump!
"""

# Global Variables
bean_pack_count = 0
bean_pack_notification_start_time = 0  # Zeit für automatisches Ausblenden
achievement_notification_start_time = 0  # Zeit für Achievement Auto-Hide

import badger2040, machine, time, json, uos

# =============================================================================
# HARDWARE INITIALIZATION
# =============================================================================

# Initialize Badger2040 display and configure basic settings
display = badger2040.Badger2040()
display.set_font("bitmap8")  # Set font for consistent text rendering

# Display dimensions for layout calculations
WIDTH, HEIGHT = 296, 128

# Hardware button pin assignments
BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP, BUTTON_DOWN, LED = badger2040.BUTTON_A, badger2040.BUTTON_B, badger2040.BUTTON_C, badger2040.BUTTON_UP, badger2040.BUTTON_DOWN, 25

# Initialize LED pin for status indication
led = machine.Pin(LED, machine.Pin.OUT)
# =============================================================================
# FILE CONFIGURATION  
# =============================================================================

# Data file names - these files store persistent application data
log_file, date_file, count_file = "kaffee_log.csv", "current_date.txt", "current_counts.txt"

# =============================================================================
# MENU SYSTEM CONFIGURATION
# =============================================================================

# Main menu options (German labels for user interface)
menu_options = ["Bohnen", "Statistiken anzeigen", "Tagesstatistiken zurücksetzen", "Datum ändern", "Wartungshistorie", "Achievements", "Information"]

# Menu state variables - control which screen/mode is currently active
current_menu_option, menu_active, change_date_active, view_statistics_active, view_info_active, view_maintenance_history_active, view_achievements_active, bean_pack_menu_active = 0, False, False, False, False, False, False, False

# Application version - update for each release
version = "2.3.5"
# =============================================================================
# NAVIGATION AND SELECTION VARIABLES
# =============================================================================

# Maintenance history navigation
maintenance_history_selected = 0          # Selected maintenance type in history
maintenance_history_scroll = 0            # Scroll offset for maintenance history

# Achievement menu navigation  
achievement_selected = 0                   # Currently selected achievement

# Statistics page navigation (multi-page statistics view)
statistics_page = 0  # 0 = Total statistics, 1 = Bean statistics

# =============================================================================
# DRINK TRACKING SYSTEM
# =============================================================================

# Drink menu system for additional beverages beyond espresso/cappuccino
drink_menu_active = False                 # Drink selection menu visibility
drink_menu_options = ["lungo", "iced latte", "affogato", "shakerato", "espresso tonic", "other"]
current_drink_menu_option = 0             # Currently selected drink type
drink_counts = [0] * len(drink_menu_options)  # Counters for each drink type

# =============================================================================
# NOTIFICATION AND ACHIEVEMENT SYSTEM
# =============================================================================

# Generic notification system for achievements, warnings, etc.
notification_active = False               # Whether a notification is currently displayed
notification_type = ""                    # Type: "achievement" or "maintenance" 
notification_data = {}                    # Data payload for current notification
achievements_file = "achievements.json"   # Achievement progress storage

# Daily achievement tracking for title bar indicator
daily_achievement_unlocked = False        # Flag for daily achievement icon (★)

# =============================================================================
# POWER AND HARDWARE MANAGEMENT
# =============================================================================

# Battery reminder system
battery_reminder_active = False           # Low battery warning display

# Bean package consumption tracking
bean_pack_input_active = False            # Bean pack size input mode
bean_pack_sizes = [125, 200, 250, 500, 750, 1000]  # Available pack sizes in grams
bean_pack_size_index = 5                  # Default: 1000g package
bean_pack_notification_active = False     # Flag for new pack started notification
bean_pack_count = 0                       # Counter for new packages started

# =============================================================================
# MAINTENANCE SYSTEM
# =============================================================================

# Maintenance data persistence
maintenance_status_file = "maintenance_status.json"  # Maintenance tracking storage

# Maintenance warning variables are defined later in the code
# (maintenance_warning_hidden, maintenance_warning_tasks)

def load_maintenance_status():
    """
    Load maintenance status from JSON file.
    
    Returns:
        dict: Maintenance status data with task names as keys and last completion 
              dates as values. Returns empty dict if file doesn't exist or is corrupted.
    
    Error Handling:
        - Missing file: Returns empty dict
        - JSON corruption: Shows error message and returns empty dict
    """
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
    """
    Save maintenance status to JSON file.
    
    Args:
        status (dict): Maintenance status data to save
        
    Note:
        Overwrites existing file completely. No error handling for write failures.
    """
    with open(maintenance_status_file, 'w') as f:
        json.dump(status, f)

def load_maintenance_config():
    """
    Load maintenance configuration from maintenance_config.json.
    
    Returns:
        list: List of maintenance task dictionaries. Each task contains:
              - name (str): Task identifier
              - interval (int): Days between maintenance
              - drink_limit (int, optional): For brew_group_cleaning task
              
    Error Handling:
        - Missing file: Shows error and returns empty list
        - Invalid JSON: Shows error and returns empty list  
        - Missing 'tasks' key: Shows error and returns empty list
    """
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

# =============================================================================
# NOTIFICATION SYSTEM
# =============================================================================

def show_notification(notification_type, data):
    """
    Trigger a full-screen notification display.
    
    Args:
        notification_type (str): Type of notification ("achievement", "maintenance", etc.)
        data (dict): Notification data payload
        
    Note:
        Sets global flags to activate notification display in main loop.
    """
    global notification_active, notification_data, bean_pack_notification_start_time, achievement_notification_start_time
    notification_active = True
    notification_data = {"type": notification_type, "data": data}
    
    # Speichere Startzeit für Bean Pack Notifications
    if notification_type == "bean_pack":
        bean_pack_notification_start_time = time.time()
    # Speichere Startzeit für Achievement Notifications
    elif notification_type == "achievement":
        achievement_notification_start_time = time.time()

def handle_notification_display():
    """
    Render and handle notification display if active.
    
    Returns:
        bool: True if notification was displayed, False otherwise
        
    Note:
        Called from main display update loop. Handles button input for dismissing
        notifications. Uses NORMAL update speed for immediate visibility.
    """
    global notification_active, notification_data, bean_pack_notification_start_time, achievement_notification_start_time
    if not notification_active:
        return False
    
    # Auto-Hide für Bean Pack Notifications nach 0.5 Sekunden
    if (notification_data["type"] == "bean_pack" and 
        bean_pack_notification_start_time > 0 and 
        time.time() - bean_pack_notification_start_time >= 0.5):
        notification_active = False
        notification_data = {}
        bean_pack_notification_start_time = 0
        update_display(True)
        return False
    
    # Auto-Hide für Achievement Notifications nach 1 Sekunde
    if (notification_data["type"] == "achievement" and 
        achievement_notification_start_time > 0 and 
        time.time() - achievement_notification_start_time >= 1.0):
        notification_active = False
        notification_data = {}
        achievement_notification_start_time = 0
        update_display(True)
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
        
    elif notification_data["type"] == "bean_pack":
        # Bean Pack Benachrichtigung
        pack_size = notification_data["data"]["size"]
        
        # Titel zentrieren
        title_text = "Neue Packung gestartet!"
        title_width = display.measure_text(title_text, 2)
        title_x = (WIDTH - title_width) // 2
        display.text(title_text, title_x, 40, scale=2)
        
        # Packungsgröße anzeigen
        size_text = f"{pack_size}g Bohnen"
        size_width = display.measure_text(size_text, 2)
        size_x = (WIDTH - size_width) // 2
        display.text(size_text, size_x, 70, scale=2)
        
        # Button-Hinweise
        ok_text = "OK"
        ok_x = 41 - display.measure_text(ok_text, 1) // 2
        display.text(ok_text, ok_x, HEIGHT - 15, scale=1)
    
    display.update()
    return True

def handle_notification_input():
    global notification_active, notification_data, maintenance_warning_hidden, daily_achievement_unlocked, bean_pack_notification_start_time, achievement_notification_start_time
    
    if notification_data["type"] == "achievement":
        if display.pressed(BUTTON_A) or display.pressed(BUTTON_B) or display.pressed(BUTTON_C):
            daily_achievement_unlocked = True  # Zeige Icon in Titelleiste
            notification_active = False
            notification_data = {}
            achievement_notification_start_time = 0
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
            
    elif notification_data["type"] == "bean_pack":
        if display.pressed(BUTTON_A) or display.pressed(BUTTON_B) or display.pressed(BUTTON_C):
            notification_active = False
            notification_data = {}
            bean_pack_notification_start_time = 0
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
        "first_coffee": {"name": "Erster Kaffee", "desc": "Dein allererster Kaffee!", "icon": "#1", "category": "Meilensteine"},
        "coffee_10": {"name": "Kaffee-Starter", "desc": "10 Kaffees getrunken", "icon": "#10", "category": "Meilensteine"},
        "coffee_50": {"name": "Kaffee-Fan", "desc": "50 Kaffees getrunken", "icon": "#50", "category": "Meilensteine"},
        "coffee_100": {"name": "Kaffee-Liebhaber", "desc": "100 Kaffees getrunken", "icon": "#100", "category": "Meilensteine"},
        "coffee_500": {"name": "Kaffee-Experte", "desc": "500 Kaffees getrunken", "icon": "#500", "category": "Meilensteine"},
        "coffee_1000": {"name": "Kaffee-Meister", "desc": "1000 Kaffees getrunken", "icon": "#1000", "category": "Meilensteine"},
        
        # Streak-basiert
        "streak_7": {"name": "Consistency Expert", "desc": "7 Tage in Folge Kaffee", "icon": "=7", "category": "Streaks"},
        "streak_30": {"name": "Consistency Master", "desc": "30 Tage in Folge Kaffee", "icon": "=30", "category": "Streaks"},
        
        # Spezialgetränke
        "stay_cool": {"name": "Stay Cool", "desc": "Ersten Iced Latte getrunken", "icon": "~", "category": "Spezialgetränke"},
        "dessert": {"name": "Dessert", "desc": "Ersten Affogato getrunken", "icon": "o", "category": "Spezialgetränke"},
        "shaker": {"name": "Shake it!", "desc": "Ersten Shakerato getrunken", "icon": "%", "category": "Spezialgetränke"},
        
        # Wartungsbezogen
        "maintenance_master": {"name": "Wartungsmeister", "desc": "Alle Wartungen rechtzeitig", "icon": "[]", "category": "Wartung"},
        "clean_machine": {"name": "Saubere Maschine", "desc": "Erste Wartung durchgeführt", "icon": "<>", "category": "Wartung"},
        
        # Experimentell
        "barista": {"name": "Barista", "desc": "Alle Getränketypen probiert", "icon": ">>", "category": "Experimentell"},
        "happy_bean_day": {"name": "Happy Bean Day", "desc": "10 Kaffees an einem Tag", "icon": "^^", "category": "Experimentell"}
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
    """
    Check if user has consumed 10+ drinks today (Happy Bean Day achievement).
    
    Returns:
        bool: True if total drinks today >= 10, False otherwise
    """
    # Get current live counters (most accurate)
    current_total = espresso_count + cappuccino_count + sum(drink_counts)
    
    print(f"DEBUG Happy Bean Day: current_total = {current_total}")
    print(f"DEBUG: espresso={espresso_count}, cappuccino={cappuccino_count}, other={sum(drink_counts)}")
    
    return current_total >= 10

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
    global menu_active, view_statistics_active, change_date_active, view_info_active, drink_menu_active, bean_pack_menu_active
    print("System will turn off in 5 seconds...")
    # Alle Menüs deaktivieren
    menu_active = False
    view_statistics_active = False
    change_date_active = False
    view_info_active = False
    drink_menu_active = False
    bean_pack_menu_active = False
    
    # Spezielles nap-Display mit Titelzeile aber ohne Counter-Rahmen
    display.set_pen(15)
    display.clear()
    
    # Titelzeile wie im normalen Hauptbildschirm
    display.set_pen(0)
    display.set_font("bitmap8")
    display.text("beanOS", 10, 2)
    
    # Datum rechts (gleiche Position wie normal)
    date_str = format_date(time.localtime(current_date))
    display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
    
    # Achievement Symbol zentriert zwischen Logo und Datum
    if daily_achievement_unlocked:
        # Berechne Position für zentriertes Achievement-Symbol
        logo_end = 10 + display.measure_text("beanOS", 1)
        date_start = WIDTH - display.measure_text(date_str, 1) - 49
        center_x = (logo_end + date_start) // 2
        symbol_width = display.measure_text("*", 1)
        symbol_x = center_x - symbol_width // 2
        display.text("*", symbol_x, 2)
    
    # Counter ohne Rahmen aber an gleicher horizontaler Position, nur tiefer
    box_width = 90
    box_height = 60
    box_spacing = 8
    start_x = (WIDTH - (3 * box_width + 2 * box_spacing)) // 2
    
    terms = ["ESPRESSO", "CAPPUCCINO", "ANDERE"]
    counts = [espresso_count, cappuccino_count, sum(drink_counts)]
    
    # Counter nach unten verschieben (Y: 80 statt HEIGHT - 70)
    for i, (term, count) in enumerate(zip(terms, counts)):
        box_x = start_x + i * (box_width + box_spacing)
        box_y = 80  # Etwas nach unten verschoben
        
        # Nur Text ohne Rahmen
        display.set_pen(0)
        
        # Zähler (große Zahl)
        count_str = str(count)
        count_width = display.measure_text(count_str, 3)
        count_x = box_x + (box_width - count_width) // 2
        display.text(count_str, count_x, box_y + 8, scale=3)
        
        # Label (kleiner Text) - Position angepasst damit sie nicht zu weit unten stehen
        label_width = display.measure_text(term, 1)
        label_x = box_x + (box_width - label_width) // 2
        display.text(term, label_x, box_y + 35, scale=1)  # 35 statt box_height - 15 (45)
    
    display.update()
    
    for i in range(5, 0, -1):
        print(f"{i}...")
        for _ in range(5):
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            time.sleep(0.1)
    
    # Sleep-Screen mit "wake me up" Text
    display.set_update_speed(badger2040.UPDATE_FAST)
    display.set_pen(4)
    text1 = "wake me up"
    text2 = "when the caffeine ends"
    text_width1 = display.measure_text(text1, 2)
    text_width2 = display.measure_text(text2, 2)
    # Text nach oben verschieben, damit er nicht vor den Zählern steht
    display.text(text1, (WIDTH - text_width1) // 2, 35, scale=2)
    display.text(text2, (WIDTH - text_width2) // 2, 55, scale=2)
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

def calculate_bean_pack_count():
    """
    Zählt die Anzahl der gestarteten Bohnenpackungen aus dem Logfile.
    
    Returns:
        int: Anzahl der gestarteten Packungen
    """
    if log_file not in uos.listdir():
        return 0
    
    pack_count = 0
    try:
        with open(log_file, 'r') as file:
            lines = file.readlines()[1:]  # Skip header
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) == 2 and parts[1].startswith("NEUE_PACKUNG:"):
                    pack_count += 1
    except Exception as e:
        print(f"DEBUG: Error counting bean packs: {e}")
        return 0
    
    return pack_count

def get_last_bean_packs():
    """
    Holt die letzten beiden Bohnenpackungen mit Datum und Größe.
    
    Returns:
        list: Liste der letzten beiden Packungen als (datum, groesse) Tupel
    """
    if log_file not in uos.listdir():
        return []
    
    bean_packs = []
    try:
        with open(log_file, 'r') as file:
            lines = file.readlines()[1:]  # Skip header
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) == 2 and parts[1].startswith("NEUE_PACKUNG:"):
                    datum = parts[0]
                    groesse = parts[1][13:]  # Remove "NEUE_PACKUNG:" prefix
                    bean_packs.append((datum, groesse))
    except Exception as e:
        print(f"DEBUG: Error reading bean packs: {e}")
        return []
    
    # Rückgabe der letzten beiden Packungen (neueste zuerst)
    return bean_packs[-2:] if len(bean_packs) >= 2 else bean_packs

def calculate_total_statistics_and_first_date():
    """
    Calculate total statistics from log file and find first recorded date.
    
    Returns:
        tuple: (total_espresso, total_cappuccino, total_other, first_date)
               Returns (0, 0, 0, None) if log file doesn't exist
    """
    if log_file not in uos.listdir():
        print("DEBUG: Log file not found")
        return 0, 0, 0, None
        
    total_espresso, total_cappuccino, total_other = 0, 0, 0
    first_date = None
    
    try:
        with open(log_file, 'r') as file:
            lines = file.readlines()
            print(f"DEBUG: Found {len(lines)} lines in log file")
            
            # Skip header line if it exists
            data_lines = lines[1:] if len(lines) > 1 else lines
            
            for i, line in enumerate(data_lines):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                parts = line.split(',')
                print(f"DEBUG: Line {i+2}: {parts}")
                
                # Only process day entries (not maintenance entries)
                if len(parts) >= 3 and not parts[1].startswith("WARTUNG:"):
                    try:
                        date = parts[0]
                        espresso = int(parts[1]) if parts[1].isdigit() else 0
                        cappuccino = int(parts[2]) if parts[2].isdigit() else 0
                        
                        # Handle additional drink counts safely
                        other_drinks = []
                        for j in range(3, len(parts)):
                            if parts[j].isdigit():
                                other_drinks.append(int(parts[j]))
                            else:
                                other_drinks.append(0)
                        
                        total_espresso += espresso
                        total_cappuccino += cappuccino
                        total_other += sum(other_drinks)
                        
                        if first_date is None:
                            first_date = date
                            
                        print(f"DEBUG: Processed day {date}: E={espresso}, C={cappuccino}, O={sum(other_drinks)}")
                        
                    except (ValueError, IndexError) as e:
                        print(f"DEBUG: Error processing line {i+2}: {e}")
                        continue
                        
    except Exception as e:
        print(f"DEBUG: Error reading log file: {e}")
        return 0, 0, 0, None
    
    print(f"DEBUG: Final totals: E={total_espresso}, C={total_cappuccino}, O={total_other}, First={first_date}")
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
    global statistics_page, menu_active, achievement_selected, maintenance_history_scroll
    
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
        
        # Datum rechts (gleiche Position wie im Hauptmenü)
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
        
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
        
        # Scrolling-Berechnung
        items_per_page = (HEIGHT - 26) // 24  # Verfügbare Höhe geteilt durch Item-Höhe
        total_items = len(wartungstypen)
        max_scroll = max(0, total_items - items_per_page)
        
        # Automatisches Scrolling wenn Selection außerhalb des sichtbaren Bereichs
        if maintenance_history_selected < maintenance_history_scroll:
            maintenance_history_scroll = maintenance_history_selected
        elif maintenance_history_selected >= maintenance_history_scroll + items_per_page:
            maintenance_history_scroll = maintenance_history_selected - items_per_page + 1
        
        # Scroll-Grenzen einhalten
        maintenance_history_scroll = max(0, min(maintenance_history_scroll, max_scroll))
        
        y_pos = 26
        for i in range(maintenance_history_scroll, min(total_items, maintenance_history_scroll + items_per_page)):
            typ, name = wartungstypen[i]
            datum = wartung_dict.get(typ, "")
            is_selected = (i == maintenance_history_selected)
            warning_marker = "! " if typ in current_warnings else ""
            
            # Zeichne Auswahlrahmen für ausgewähltes Item
            if is_selected:
                display.set_pen(0)
                display.rectangle(5, y_pos - 2, WIDTH - 10, 24)
                display.set_pen(15)
                display.rectangle(7, y_pos, WIDTH - 14, 20)
                display.set_pen(0)
            
            # Wartungstyp und Datum anzeigen
            if datum:
                # Jahr als '25 anzeigen
                try:
                    tag, monat, jahr = datum.split('.')
                    jahr_kurz = jahr[-2:]
                    datum_kurz = f"{tag}.{monat}.'{jahr_kurz}"
                except Exception:
                    datum_kurz = datum
                display.text(f"{warning_marker}{name}", 12, y_pos + 3, scale=2)
                # Datum rechts ausgerichtet
                datum_width = display.measure_text(datum_kurz, 1)
                display.text(datum_kurz, WIDTH - datum_width - 12, y_pos + 3, scale=1)
            else:
                display.text(f"{warning_marker}{name}: --", 12, y_pos + 3, scale=2)
            
            # Trennlinie (außer beim letzten sichtbaren Item)
            if i < min(total_items - 1, maintenance_history_scroll + items_per_page - 1):
                line_y = y_pos + 22
                display.rectangle(15, line_y, WIDTH - 30, 1)
            
            y_pos += 24
        
        display.update()
        return
    if view_achievements_active:
        menu_active = False
        
        # Vollständiges Clearing für Achievement-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Achievements", 10, 2)
        
        # Datum rechts im Titel (gleiche Position wie im Hauptmenü)
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
        
        # Weißer Hintergrund für Inhalt
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        
        achievements = load_achievements()
        definitions = get_achievement_definitions()
        
        # Nur erreichte Achievements + incomplete Streaks anzeigen
        display_items = []
        
        # Erreichte Achievements sammeln
        reached_achievements = []
        for key, achievement in definitions.items():
            if key in achievements:
                reached_achievements.append((key, achievements[key], achievement))
        
        # Sortiere erreichte nach Datum (neueste zuerst)
        reached_achievements.sort(key=lambda x: x[1], reverse=True)
        
        # Unvollständige Streaks hinzufügen
        current_streak = calculate_coffee_streak()
        for key in ["streak_7", "streak_30"]:
            if key not in achievements:
                display_items.append(("incomplete", key, definitions[key], current_streak))
        
        # Erreichte Achievements hinzufügen
        for key, date, achievement in reached_achievements:
            display_items.append(("complete", key, achievement, date))
        
        if not display_items:
            # Zentrierte Nachricht für keine Achievements
            display.text("Noch keine Achievements erreicht!", 
                        (WIDTH - display.measure_text("Noch keine Achievements erreicht!", 1)) // 2, 50, scale=1)
            display.text("Trinke deinen ersten Kaffee!", 
                        (WIDTH - display.measure_text("Trinke deinen ersten Kaffee!", 1)) // 2, 70, scale=1)
        else:
            # Zeige maximal 3 Items gleichzeitig für mehr Platz pro Item
            max_visible = 3
            total_items = len(display_items)
            
            # Bestimme Start-Index basierend auf aktueller Auswahl
            if achievement_selected < 1:
                start_index = 0
            elif achievement_selected >= total_items - 1:
                start_index = max(0, total_items - max_visible)
            else:
                start_index = achievement_selected - 1
            
            end_index = min(total_items, start_index + max_visible)
            
            y_pos = 26
            for i in range(start_index, end_index):
                if i < len(display_items):
                    item = display_items[i]
                    is_selected = (i == achievement_selected)
                    
                    # Zeichne Auswahlrahmen für ausgewähltes Item
                    if is_selected:
                        display.set_pen(0)
                        display.rectangle(5, y_pos - 2, WIDTH - 10, 36)
                        display.set_pen(15)
                        display.rectangle(7, y_pos, WIDTH - 14, 32)
                        display.set_pen(0)
                    
                    if item[0] == "incomplete":
                        # Unvollständiges Streak-Achievement
                        key, achievement, current_streak = item[1], item[2], item[3]
                        max_streak = 7 if key == "streak_7" else 30
                        
                        # Icon und Name in größerer Schrift
                        icon_text = f"[ ] {achievement['name']}"
                        display.text(icon_text, 12, y_pos + 2, scale=2)
                        
                        # Fortschrittsbalken zeichnen
                        bar_x, bar_y = 12, y_pos + 20
                        bar_width = 100
                        bar_height = 8
                        
                        # Rahmen
                        display.rectangle(bar_x, bar_y, bar_width, bar_height)
                        display.set_pen(15)
                        display.rectangle(bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2)
                        display.set_pen(0)
                        
                        # Fortschritt
                        if max_streak > 0:
                            # Begrenze current_streak auf max_streak um Überlauf zu vermeiden
                            capped_streak = min(current_streak, max_streak)
                            progress_width = int((capped_streak / max_streak) * (bar_width - 2))
                            if progress_width > 0:
                                display.rectangle(bar_x + 1, bar_y + 1, progress_width, bar_height - 2)
                        
                        # Fortschrittstext rechts (zeige capped values)
                        capped_streak = min(current_streak, max_streak)
                        progress_text = f"{capped_streak}/{max_streak}"
                        display.text(progress_text, bar_x + bar_width + 8, y_pos + 18, scale=1)
                        
                    else:
                        # Vollständiges Achievement
                        key, achievement, date = item[1], item[2], item[3]
                        
                        # Icon und Name mit besserem Icon-Design
                        icon_design = f"[{achievement['icon']}]"
                        icon_width = display.measure_text(icon_design, 2)
                        display.text(icon_design, 12, y_pos + 2, scale=2)
                        
                        name_text = achievement['name']
                        display.text(name_text, 12 + icon_width + 4, y_pos + 2, scale=2)
                        
                        # Datum rechts ausgerichtet
                        date_width = display.measure_text(date, 1)
                        display.text(date, WIDTH - date_width - 12, y_pos + 20, scale=1)
                    
                    # Trennlinie (außer beim letzten Item)
                    if i < end_index - 1:
                        line_y = y_pos + 34
                        display.rectangle(15, line_y, WIDTH - 30, 1)
                    
                    y_pos += 38
            
        display.update()
        return
    if bean_pack_menu_active:
        menu_active = False
        
        # Vollständiges Clearing für Bean Package Menu-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Bohnen Tracking", 10, 2)
        
        # Datum rechts im Titel (gleiche Position wie im Hauptmenü)
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
        
        # Weißer Hintergrund für Inhalt
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        
        # Berechne Bohnenverbrauch
        bean_pack_size = bean_pack_sizes[bean_pack_size_index]
        log_days = 0
        total_beans_used = 0
        if log_file in uos.listdir():
            with open(log_file, 'r') as file:
                lines = file.readlines()[1:]
                for line in lines:
                    parts = line.strip().split(',')
                    if len(parts) > 2 and not parts[1].startswith("WARTUNG:"):
                        log_days += 1
                        date, espresso, cappuccino, *other = parts
                        daily_beans = int(espresso)*8 + int(cappuccino)*16 + sum(map(int, other))*10
                        total_beans_used += daily_beans
        
        days_per_pack = bean_pack_size / (total_beans_used / log_days) if log_days > 0 and total_beans_used > 0 else 0
        grams_per_day = total_beans_used / log_days if log_days > 0 else 0
        
        # Zeige alle verfügbaren Packungsgrößen mit Auswahl
        y_pos = 24
        for i, size in enumerate(bean_pack_sizes):
            is_selected = (i == bean_pack_size_index)
            
            # Zeichne Auswahlrahmen für ausgewählte Größe
            if is_selected:
                display.set_pen(0)
                display.rectangle(5, y_pos - 1, 80, 18)
                display.set_pen(15)
                display.rectangle(6, y_pos, 78, 16)
                display.set_pen(0)
            
            # Packungsgröße anzeigen
            size_text = f"{size}g"
            display.text(size_text, 12, y_pos + 2, scale=2)
            
            y_pos += 17
        
        # Statistiken rechts
        stats_x = 95
        
        # Gesamtzahl der Packungen
        display.text(f"Packungen: {bean_pack_count}", stats_x, 26, scale=2)
        
        # Letzte beiden Packungen mit Datum (neueste zuerst)
        last_packs = get_last_bean_packs()
        y_offset = 46
        
        if len(last_packs) >= 2:
            # Letzte Packung (neueste)  
            datum1, groesse1 = last_packs[1]
            display.text(f"{groesse1} {datum1}", stats_x, y_offset, scale=2)
            y_offset += 20
            
            # Zweitletzte Packung (ältere)
            datum2, groesse2 = last_packs[0]
            display.text(f"{groesse2} {datum2}", stats_x, y_offset, scale=2)
        elif len(last_packs) == 1:
            # Nur eine Packung vorhanden
            datum1, groesse1 = last_packs[0]
            display.text(f"{groesse1} {datum1}", stats_x, y_offset, scale=2)
        else:
            # Keine Packungen vorhanden
            display.text("Keine Packungen", stats_x, y_offset, scale=1)
        
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
    # Balken-Beschriftung nur für Hauptbildschirm (andere Menüs haben eigene Titel)
    if not (view_statistics_active or change_date_active or view_info_active or menu_active or drink_menu_active or view_maintenance_history_active or view_achievements_active or bean_pack_menu_active):
        balken_text = "beanOS"
        display.text(balken_text, 10, 2)
        
        # Achievement-Icon zentriert in der Titelleiste
        if daily_achievement_unlocked:
            achievement_icon = "★"
            icon_width = display.measure_text(achievement_icon, 1)
            icon_x = (WIDTH - icon_width) // 2
            display.text(achievement_icon, icon_x, 2)
        
        # Datum rechts
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
        
        # Kleines Wartungsicon links vom Datum
        maintenance_warnings = check_maintenance_warnings()
        if maintenance_warnings and maintenance_warning_hidden:
            display.text("!", WIDTH - display.measure_text(date_str, 1) - 60, 2)

    display.set_pen(0)

    if change_date_active:
        menu_active = False
        
        # Vollständiges Clearing für Datum-Ändern-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Datum ändern", 10, 2)
        
        # Aktuelles Datum rechts im Titel (gleiche Position wie im Hauptmenü)
        current_date_str = format_date(time.localtime(current_date))
        display.text(current_date_str, WIDTH - display.measure_text(current_date_str, 1) - 49, 2)
        
        # Weißer Hintergrund für Inhalt
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        
        # Neues Datum zentriert anzeigen
        new_date_str = format_date(time.localtime(temp_date))
        date_width = display.measure_text(new_date_str, 3)
        date_x = (WIDTH - date_width) // 2
        display.text(new_date_str, date_x, HEIGHT // 2 - 15, scale=3)
        
        # Button-Hinweise
        display.text("UP/DOWN: Datum  A: Übernehmen  C: Abbrechen", 10, HEIGHT - 15, scale=1)
        
        display.update()
        return
    elif view_statistics_active:
        menu_active = False
        
        # Vollständiges Clearing für Statistik-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        
        # Titel je nach Seite
        if statistics_page == 0:
            display.text("Gesamtstatistik", 10, 2)
        elif statistics_page == 1:
            display.text("Bohnenstatistik", 10, 2)
        else:
            display.text("Statistik", 10, 2)
        
        # Datum rechts im Titel (gleiche Position wie im Hauptmenü)
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
        
        # Weißer Hintergrund für Inhalt
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        
        if statistics_page == 0:
            # Seite 0: Gesamtstatistik mit schönem Layout
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
            
            # Schöne Boxen für die Statistiken
            y_pos = 28
            
            # Espresso Box
            display.rectangle(5, y_pos, WIDTH-10, 22)
            display.set_pen(15)
            display.rectangle(6, y_pos+1, WIDTH-12, 20)
            display.set_pen(0)
            display.text(f"Espresso: {total_espresso}", 10, y_pos + 4, scale=2)
            display.text(f"({espresso_avg:.1f}/Tag)", WIDTH - 80, y_pos + 4, scale=1)
            y_pos += 24
            
            # Cappuccino Box
            display.rectangle(5, y_pos, WIDTH-10, 22)
            display.set_pen(15)
            display.rectangle(6, y_pos+1, WIDTH-12, 20)
            display.set_pen(0)
            display.text(f"Cappuccino: {total_cappuccino}", 10, y_pos + 4, scale=2)
            display.text(f"({cappuccino_avg:.1f}/Tag)", WIDTH - 80, y_pos + 4, scale=1)
            y_pos += 24
            
            # Andere Box
            display.rectangle(5, y_pos, WIDTH-10, 22)
            display.set_pen(15)
            display.rectangle(6, y_pos+1, WIDTH-12, 20)
            display.set_pen(0)
            display.text(f"Andere: {total_other}", 10, y_pos + 4, scale=2)
            display.text(f"({other_avg:.1f}/Tag)", WIDTH - 80, y_pos + 4, scale=1)
            y_pos += 27
            
            # Gesamt-Box (hervorgehoben)
            display.rectangle(5, y_pos, WIDTH-10, 22)
            display.set_pen(0)
            display.rectangle(6, y_pos+1, WIDTH-12, 20)
            display.set_pen(15)
            total_drinks = total_espresso + total_cappuccino + total_other
            display.text(f"Gesamt: {total_drinks} Getränke", 10, y_pos + 4, scale=2)
            display.set_pen(0)
            y_pos += 27
            
            # Zeitraum
            if first_date:
                display.text(f"Seit: {first_date}", 10, y_pos, scale=1)
            else:
                display.text("Keine Daten verfügbar", 10, y_pos, scale=1)
            
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
            
            # Schöne Boxen für die Bohnenstatistik
            y_pos = 28
            
            # Packungsgröße Box
            display.rectangle(5, y_pos, WIDTH-10, 22)
            display.set_pen(15)
            display.rectangle(6, y_pos+1, WIDTH-12, 20)
            display.set_pen(0)
            display.text(f"Packungsgröße: {bean_pack_size}g", 10, y_pos + 4, scale=2)
            y_pos += 24
            
            # Tage pro Packung Box
            display.rectangle(5, y_pos, WIDTH-10, 22)
            display.set_pen(15)
            display.rectangle(6, y_pos+1, WIDTH-12, 20)
            display.set_pen(0)
            display.text(f"Tage/Packung: {days_per_pack:.1f}", 10, y_pos + 4, scale=2)
            y_pos += 24
            
            # Gramm pro Tag Box
            display.rectangle(5, y_pos, WIDTH-10, 22)
            display.set_pen(15)
            display.rectangle(6, y_pos+1, WIDTH-12, 20)
            display.set_pen(0)
            display.text(f"Gramm/Tag: {grams_per_day:.1f}g", 10, y_pos + 4, scale=2)
            y_pos += 24
            
            # Gesamtverbrauch Box (hervorgehoben)
            display.rectangle(5, y_pos, WIDTH-10, 22)
            display.set_pen(0)
            display.rectangle(6, y_pos+1, WIDTH-12, 20)
            display.set_pen(15)
            display.text(f"Gesamt: {total_beans_used}g", 10, y_pos + 4, scale=2)
            display.set_pen(0)
        else:
            display.text("Unbekannte Statistik-Seite", 10, 30)
        
        display.update()
        return
    elif view_info_active:
        menu_active = False
        
        # Vollständiges Clearing für Info-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Information", 10, 2)
        
        # Datum rechts im Titel (gleiche Position wie im Hauptmenü)
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
        
        # Weißer Hintergrund für Inhalt
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        
        # Informationen in strukturierter Form anzeigen
        y_pos = 28
        
        # Version Info
        display.text(f"beanOS v{version}", 12, y_pos, scale=2)
        y_pos += 22
        
        # Autor
        display.text("Entwickelt von:", 12, y_pos, scale=1)
        display.text("Joao Neisinger", 120, y_pos, scale=1)
        y_pos += 18
        
        # Lizenz
        display.text("Lizenz:", 12, y_pos, scale=1)
        display.text("GNU GPLv3", 120, y_pos, scale=1)
        y_pos += 18
        
        # Hardware Info
        display.text("Hardware:", 12, y_pos, scale=1)
        display.text("Badger2040", 120, y_pos, scale=1)
        y_pos += 18
        
        # Button Hinweise unten
        display.text("C: Zurück", WIDTH - display.measure_text("C: Zurück", 1) - 12, HEIGHT - 15, scale=1)
        
        display.update()
        return
    elif drink_menu_active:
        menu_active = False
        
        # Vollständiges Clearing für Getränkemenü-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Bohnen", 10, 2)
        
        # Datum rechts im Titel (gleiche Position wie im Hauptmenü)
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
        
        # Weißer Hintergrund für Inhalt
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        
        # Zeige maximal 4 Getränke gleichzeitig für mehr Platz pro Item
        max_visible = 4
        total_items = len(drink_menu_options)
        
        # Bestimme Start-Index basierend auf aktueller Auswahl
        if current_drink_menu_option < 2:
            start_index = 0
        elif current_drink_menu_option >= total_items - 2:
            start_index = max(0, total_items - max_visible)
        else:
            start_index = current_drink_menu_option - 1
        
        end_index = min(total_items, start_index + max_visible)
        
        y_pos = 26
        for i in range(start_index, end_index):
            if i < len(drink_menu_options):
                option = drink_menu_options[i]
                count = drink_counts[i]
                is_selected = (i == current_drink_menu_option)
                
                # Zeichne Auswahlrahmen für ausgewähltes Item
                if is_selected:
                    display.set_pen(0)
                    display.rectangle(5, y_pos - 2, WIDTH - 10, 26)
                    display.set_pen(15)
                    display.rectangle(7, y_pos, WIDTH - 14, 22)
                    display.set_pen(0)
                
                # Getränkename
                display_name = option[0].upper() + option[1:] if option else option
                display.text(display_name, 12, y_pos + 4, scale=2)
                
                # Anzahl rechts ausgerichtet
                count_text = f"x{count}"
                count_width = display.measure_text(count_text, 2)
                display.text(count_text, WIDTH - count_width - 12, y_pos + 4, scale=2)
                
                # Trennlinie (außer beim letzten Item)
                if i < end_index - 1:
                    line_y = y_pos + 24
                    display.rectangle(15, line_y, WIDTH - 30, 1)
                
                y_pos += 26
        
        
        display.update()
        return
    elif menu_active:
        # Vollständiges Clearing für Hauptmenü-Anzeige
        display.set_pen(15)
        display.clear()
        
        # Schwarzer Balken für Titel
        display.set_pen(0)
        display.rectangle(0, 0, WIDTH, 20)
        display.set_pen(15)
        display.set_font("bitmap8")
        display.text("Menü", 10, 2)
        
        # Datum rechts im Titel (gleiche Position wie im Hauptmenü)
        date_str = format_date(time.localtime(current_date))
        display.text(date_str, WIDTH - display.measure_text(date_str, 1) - 49, 2)
        
        # Weißer Hintergrund für Inhalt
        display.set_pen(15)
        display.rectangle(0, 20, WIDTH, HEIGHT-20)
        display.set_pen(0)
        
        # Berechne sichtbaren Bereich dynamisch basierend auf verfügbarem Platz
        available_height = HEIGHT - 20 - 6  # Abzüglich Titel und Margin
        item_height = 30  # Box-Höhe plus Abstand
        max_visible = min(available_height // item_height, len(menu_options))
        total_options = len(menu_options)
        
        # Bestimme Start-Index basierend auf aktueller Auswahl
        if current_menu_option < max_visible // 2:
            start_index = 0
        elif current_menu_option >= total_options - max_visible // 2:
            start_index = max(0, total_options - max_visible)
        else:
            start_index = current_menu_option - max_visible // 2
        
        end_index = min(total_options, start_index + max_visible)
        
        y_pos = 26
        for i in range(start_index, end_index):
            option = menu_options[i]
            is_selected = (i == current_menu_option)
            
            # Zeichne Auswahlrahmen für ausgewähltes Item
            if is_selected:
                display.set_pen(0)
                display.rectangle(5, y_pos - 2, WIDTH - 10, 30)
                display.set_pen(15)
                display.rectangle(7, y_pos, WIDTH - 14, 26)
                display.set_pen(0)
            
            # Menüpunkt anzeigen mit besserer Zentrierung
            display.text(option, 12, y_pos + 8, scale=2)
            
            # Trennlinie (außer beim letzten Item)
            if i < end_index - 1:
                line_y = y_pos + 28
                display.rectangle(15, line_y, WIDTH - 30, 1)
            
            y_pos += 30
        
        display.update()
        return
    else:
        # Hauptbildschirm - Zähler im schönen Design        
        # Drei Boxen für die Getränke
        box_width = 90
        box_height = 60
        box_spacing = 8
        start_x = (WIDTH - (3 * box_width + 2 * box_spacing)) // 2
        
        terms = ["ESPRESSO", "CAPPUCCINO", "ANDERE"]
        counts = [espresso_count, cappuccino_count, sum(drink_counts)]
        
        for i, (term, count) in enumerate(zip(terms, counts)):
            box_x = start_x + i * (box_width + box_spacing)
            box_y = HEIGHT - box_height - 10
            
            # Box-Rahmen
            display.set_pen(0)
            display.rectangle(box_x, box_y, box_width, box_height)
            display.set_pen(15)
            display.rectangle(box_x + 1, box_y + 1, box_width - 2, box_height - 2)
            display.set_pen(0)
            
            # Zähler (große Zahl)
            count_str = str(count)
            count_width = display.measure_text(count_str, 3)
            count_x = box_x + (box_width - count_width) // 2
            display.text(count_str, count_x, box_y + 8, scale=3)
            
            # Label (kleiner Text)
            label_width = display.measure_text(term, 1)
            label_x = box_x + (box_width - label_width) // 2
            display.text(term, label_x, box_y + box_height - 15, scale=1)

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
    global espresso_count, cappuccino_count, current_date, button_press_count, menu_active, current_menu_option, change_date_active, view_statistics_active, view_info_active, battery_reminder_active, drink_menu_active, current_drink_menu_option, drink_counts, battery_reminder_count, temp_date, last_interaction_time, maintenance_warning_hidden, maintenance_warning_tasks, view_maintenance_history_active, view_achievements_active, notification_active, notification_data, achievement_selected, statistics_page, daily_achievement_unlocked, bean_pack_menu_active, bean_pack_size_index, bean_pack_notification_start_time, achievement_notification_start_time

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
            menu_active = True
            update_display(True)
            return
        update_display(False)
        return

    if view_info_active:
        if display.pressed(BUTTON_C): 
            view_info_active = False
            menu_active = True
        update_display(True)
        return

    if bean_pack_menu_active:
        print(f"DEBUG: bean_pack_menu_active is True, button pressed: {button_name}")
        if display.pressed(BUTTON_UP):
            # Packungsgröße verringern
            bean_pack_size_index = (bean_pack_size_index - 1) % len(bean_pack_sizes)
            print(f"DEBUG: BUTTON_UP - bean_pack_size_index: {bean_pack_size_index}")
            update_display(False)
            return
        elif display.pressed(BUTTON_DOWN):
            # Packungsgröße erhöhen
            bean_pack_size_index = (bean_pack_size_index + 1) % len(bean_pack_sizes)
            print(f"DEBUG: BUTTON_DOWN - bean_pack_size_index: {bean_pack_size_index}")
            update_display(False)
            return
        elif display.pressed(BUTTON_A):
            print(f"DEBUG: BUTTON_A pressed in bean_pack_menu_active")
            # Neue Packung beginnen - logge die ausgewählte Packungsgröße
            global bean_pack_count
            selected_size = bean_pack_sizes[bean_pack_size_index]
            pack_entry = f'{format_date(time.localtime(current_date))},NEUE_PACKUNG:{selected_size}g'
            
            # Stelle sicher, dass das Logfile existiert
            if log_file not in uos.listdir():
                with open(log_file, 'w') as file:
                    headers = "Datum,Espresso,Cappuccino," + ",".join(drink_menu_options)
                    file.write(headers + "\n")
            
            # Füge den Packungseintrag hinzu
            with open(log_file, 'a') as file:
                file.write(pack_entry + "\n")
            
            # Erhöhe Bean Pack Counter
            bean_pack_count += 1
            print(f"Bean pack count incremented: {bean_pack_count}")
            
            # Zeige sofortige Bestätigung 
            show_notification("bean_pack", {"size": selected_size})
            
            # Aktualisiere Anzeige sofort für neue Packung in der Liste
            update_display(True)
            print(f"DEBUG: Added new pack entry: {pack_entry}")
            return
        elif display.pressed(BUTTON_C):
            print(f"DEBUG: BUTTON_C pressed in bean_pack_menu_active")
            bean_pack_menu_active = False
            menu_active = True
            update_display(True)
            return

    if drink_menu_active:
        if display.pressed(BUTTON_UP):
            current_drink_menu_option = (current_drink_menu_option - 1) % len(drink_menu_options)
            print(f"BUTTON_UP pressed in drink_menu_active: {current_drink_menu_option}")
            update_display(False)
            return
        elif display.pressed(BUTTON_DOWN):
            current_drink_menu_option = (current_drink_menu_option + 1) % len(drink_menu_options)
            update_display(False)
            return
        elif display.pressed(BUTTON_A):
            if 0 <= current_drink_menu_option < len(drink_counts):
                drink_counts[current_drink_menu_option] += 1
                save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, drink_counts)
                check_achievements()  # Prüfe Achievements nach Getränk
            drink_menu_active = False  # Menü schließen
            menu_active = True  # Zurück zum Hauptmenü
            update_display(True)
            return
        elif display.pressed(BUTTON_C):
            drink_menu_active = False
            menu_active = True
            update_display(True)
            return

    if view_maintenance_history_active:
        global maintenance_history_selected, maintenance_history_scroll
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
        
        # Erstelle die gleiche Liste wie im Display
        display_items = []
        
        # Unvollständige Streaks
        current_streak = calculate_coffee_streak()
        for key in ["streak_7", "streak_30"]:
            if key not in achievements:
                display_items.append(("incomplete", key, definitions[key], current_streak))
        
        # Erreichte Achievements (nach Datum sortiert)
        reached_achievements = []
        for key, achievement in definitions.items():
            if key in achievements:
                reached_achievements.append((key, achievements[key], achievement))
        reached_achievements.sort(key=lambda x: x[1], reverse=True)
        
        for key, date, achievement in reached_achievements:
            display_items.append(("complete", key, achievement, date))
        
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
                bean_pack_menu_active = True
                menu_active = False  # Schließe Hauptmenü
            elif current_menu_option == 1:
                view_statistics_active = True
                menu_active = False  # Schließe Hauptmenü
                statistics_page = 0  # Immer mit Seite 0 starten
            elif current_menu_option == 2:
                clear_today_log_entries(log_file, format_date(time.localtime(current_date)))
                espresso_count, cappuccino_count = 0, 0
                menu_active = False  # Schließe Hauptmenü
            elif current_menu_option == 3:
                change_date_active, temp_date = True, current_date
                menu_active = False  # Schließe Hauptmenü
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
                menu_active = False  # Schließe Hauptmenü
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
            # Button C im Hauptbildschirm öffnet das Getränkemenü (other drinks)
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
    
    # Lade Bean Pack Counter
    bean_pack_count = calculate_bean_pack_count()
    print(f"Bean pack count initialized: {bean_pack_count}")
    
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
