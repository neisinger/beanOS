import time
import badger2040
import machine
import os

# Initialisierung des Badger2040
display = badger2040.Badger2040()

# Bildschirmgröße
WIDTH = 296
HEIGHT = 128

# GPIO Pins für die Tasten und LED
BUTTON_A = badger2040.BUTTON_A
BUTTON_B = badger2040.BUTTON_B
BUTTON_C = badger2040.BUTTON_C
BUTTON_UP = badger2040.BUTTON_UP
BUTTON_DOWN = badger2040.BUTTON_DOWN
LED = 25

# Initialisiere die LED als Ausgang
led = machine.Pin(LED, machine.Pin.OUT)

# Logdatei und Hilfsdateien für das Datum und die Zählerstände
log_file = "kaffee_log.csv"
date_file = "current_date.txt"
count_file = "current_counts.txt"

# Menü-Optionen
menu_options = ["Statistiken anzeigen", "Tagesstatistiken zurücksetzen", "Gesamtstatistiken zurücksetzen", "Datum ändern", "Information", "Beenden"]
current_menu_option = 0
menu_active = False
change_date_active = False
view_statistics_active = False
view_info_active = False
battery_reminder_active = False

# Software-Version
version = "1.5.0"

# Funktion zum manuellen Parsen von Datum im Format "DD.MM.YYYY"
def parse_date(date_str):
    try:
        day, month, year = map(int, date_str.split('.'))
        return time.mktime((year, month, day, 0, 0, 0, 0, 0, -1))
    except ValueError as e:
        print(f"Fehler beim Parsen des Datums: {e}")
        return None

# Überprüfen, ob die Hilfsdatei existiert und das aktuelle Datum extrahieren
def get_current_date_from_file(date_file):
    if date_file in os.listdir():
        with open(date_file, 'r') as file:
            date_str = file.readline().strip()
            parsed_date = parse_date(date_str)
            if parsed_date:
                return parsed_date
    # Standardwert, wenn die Datei nicht existiert oder leer ist oder ein Fehler auftritt
    return time.mktime((2025, 2, 5, 0, 0, 0, 0, 0, -1))

# Hilfsfunktion zum Formatieren des Datums
def format_date(t):
    return f"{t[2]:02d}.{t[1]:02d}.{t[0]}"

# Überprüfen, ob die Hilfsdatei existiert und die Zählerstände extrahieren
def get_counts_from_file(count_file):
    if count_file in os.listdir():
        with open(count_file, 'r') as file:
            counts = file.readline().strip().split(',')
            if len(counts) == 4:
                try:
                    return int(counts[0]), int(counts[1]), int(counts[2]), int(counts[3])
                except ValueError:
                    print("Fehler beim Parsen der Zählerstände.")
                    return 0, 0, 0, 0
    # Standardwerte, wenn die Datei nicht existiert oder leer ist oder ein Fehler auftritt
    return 0, 0, 0, 0

# Initialisierte Werte
current_date = get_current_date_from_file(date_file)  # Letztes Datum aus der Hilfsdatei einlesen
espresso_count, cappuccino_count, other_count, battery_reminder_count = get_counts_from_file(count_file)  # Zählerstände aus der Hilfsdatei einlesen
button_press_count = 0
temp_date = current_date  # Temporäres Datum für die Änderung
refresh_count = 0  # Zähler für die Anzahl der Refreshes

# Speichere Daten in der Logdatei
def save_data(date, espresso, cappuccino, other):
    with open(log_file, 'a') as file:
        file.write(f'{date},{espresso},{cappuccino},{other}\n')

# Aktualisiere die Hilfsdatei mit dem aktuellen Datum
def update_date_file(date_file, current_date):
    with open(date_file, 'w') as file:
        file.write(format_date(time.localtime(current_date)))

# Aktualisiere die Hilfsdatei mit den aktuellen Zählerständen
def update_count_file(count_file, espresso, cappuccino, other, battery_reminder_count):
    with open(count_file, 'w') as file:
        file.write(f'{espresso},{cappuccino},{other},{battery_reminder_count}')

# Leert die Logdatei (Gesamtstatistiken zurücksetzen)
def clear_log_file(log_file):
    with open(log_file, 'w') as file:
        file.write("")

# Leert die Zählerstanddatei (Gesamtstatistiken zurücksetzen)
def clear_count_file(count_file):
    with open(count_file, 'w') as file:
        file.write("")

# Löscht die Daten des aktuellen Tages aus der Logdatei und Zählerstanddatei
def clear_today_log_entries(log_file, count_file, date_str):
    if log_file in os.listdir():
        with open(log_file, 'r') as file:
            lines = file.readlines()
        with open(log_file, 'w') as file:
            for line in lines:
                if not line.startswith(date_str):
                    file.write(line)
    
    # Setze die Zählerstände für den aktuellen Tag zurück
    with open(count_file, 'w') as file:
        file.write("0,0,0,0")

# Berechne Gesamtstatistiken und das erste Datum in der Logdatei
def calculate_total_statistics_and_first_date():
    total_espresso = espresso_count  # Einschließen der aktuellen Tageszählerstände
    total_cappuccino = cappuccino_count  # Einschließen der aktuellen Tageszählerstände
    total_other = other_count  # Einschließen der aktuellen Tageszählerstände
    first_date = None
    if log_file in os.listdir():
        with open(log_file, 'r') as file:
            for line in file:
                try:
                    date, espresso, cappuccino, other = line.strip().split(',')
                    total_espresso += int(espresso)
                    total_cappuccino += int(cappuccino)
                    total_other += int(other)
                    if first_date is None:
                        first_date = date
                except ValueError:
                    print("Fehler beim Parsen einer Zeile in der Logdatei.")
                    continue
    return total_espresso, total_cappuccino, total_other, first_date

# Aktualisiere den Bildschirm
def update_display(full_update=False):
    global refresh_count

    if battery_reminder_active:
        display.set_update_speed(badger2040.UPDATE_NORMAL)
        display.set_pen(0)  # Schwarzer Hintergrund
        display.clear()
        display.set_pen(15)  # Weißer Text
        display.text("Batterien wechseln!", 10, 50, scale=2)
        display.update()
        return

    if full_update or refresh_count >= 14:
        display.set_update_speed(badger2040.UPDATE_NORMAL)  # Setze die Update-Geschwindigkeit auf normal für volle Updates
        refresh_count = 0  # Reset the refresh counter after a full refresh
    else:
        display.set_update_speed(badger2040.UPDATE_TURBO)  # Setze die Update-Geschwindigkeit auf Turbo für schnelle Updates
        refresh_count += 1
    
    display.set_pen(15)  # Weißer Hintergrund
    display.clear()
    display.set_pen(0)  # Schwarzer Text

    if change_date_active:
        # Aktuelles Datum groß und mittig anzeigen
        date_str = format_date(time.localtime(temp_date))
        date_width = display.measure_text(date_str, 2)  # Größere Schrift
        display.text(date_str, (WIDTH - date_width) // 2, HEIGHT // 2 - 10, scale=2)
    elif view_statistics_active:
        # Statistiken anzeigen
        total_espresso, total_cappuccino, total_other, first_date = calculate_total_statistics_and_first_date()
        display.text("Gesamtstatistiken:", 10, 10)
        display.text(f"Espresso: {total_espresso}", 10, 30)
        display.text(f"Cappuccino: {total_cappuccino}", 10, 50)
        display.text(f"Anderes: {total_other}", 10, 70)
        if first_date:
            display.text(f"Seit: {first_date}", 10, 90)
        else:
            display.text("Keine Daten verfügbar", 10, 90)
    elif view_info_active:
        # Information anzeigen
        display.text("Information:", 10, 10)
        display.text(f"Version: {version}", 10, 30)
        display.text("by Joao Neisinger", 10, 50)
        display.text("Lizenz: None", 10, 70)
    elif menu_active:
        # Menü anzeigen
        for i, option in enumerate(menu_options):
            if i == current_menu_option:
                display.text("> " + option, 10, 20 + i * 20)
            else:
                display.text(option, 10, 20 + i * 20)
    else:
        # Hauptanzeige
        # "BeanCounter" oben links anzeigen
        display.text("BeanCounter", 10, 10)

        # Datum rechtsbündig anzeigen
        date_str = format_date(time.localtime(current_date))
        date_width = display.measure_text(date_str, 1)
        display.text(date_str, WIDTH - date_width - 49, 10)  # 4 Pixel weiter links

        # Begriffe und deren Zähler zentriert anzeigen
        term_espresso = "ESPRESSO"
        term_cappu = "CAPPU"
        term_andere = "ANDERES"
        
        count_espresso = espresso_count
        count_cappu = cappuccino_count
        count_andere = other_count
        
        term_y = HEIGHT - 20
        count_y = HEIGHT - 40
        
        # ESPRESSO linksbündig
        term_espresso_width = display.measure_text(term_espresso, 1)
        count_espresso_width = display.measure_text(str(count_espresso), 1)
        x_espresso = 10
        display.text(str(count_espresso), x_espresso + (term_espresso_width - count_espresso_width) // 2, count_y)
        display.text(term_espresso, x_espresso, term_y)
        
        # CAPPU zentriert
        term_cappu_width = display.measure_text(term_cappu, 1)
        count_cappu_width = display.measure_text(str(count_cappu), 1)
        x_cappu = (WIDTH - term_cappu_width) // 2
        display.text(str(count_cappu), x_cappu + (term_cappu_width - count_cappu_width) // 2, count_y)
        display.text(term_cappu, x_cappu, term_y)

        # ANDERES rechtsbündig
        term_andere_width = display.measure_text(term_andere, 1)
        count_andere_width = display.measure_text(str(count_andere), 1)
        x_andere = WIDTH - term_andere_width - 40  # 5 Pixel weiter rechts
        display.text(str(count_andere), x_andere + (term_andere_width - count_andere_width) // 2, count_y)
        display.text(term_andere, x_andere, term_y)

    display.update()

# Tasten-Event-Handler
def button_pressed(pin):
    global espresso_count, cappuccino_count, other_count, current_date, button_press_count, menu_active, current_menu_option, change_date_active, view_statistics_active, view_info_active, battery_reminder_active, temp_date, battery_reminder_count

    if battery_reminder_active:
        if display.pressed(BUTTON_A):
            battery_reminder_active = False
            battery_reminder_count = 0
            update_count_file(count_file, espresso_count, cappuccino_count, other_count, battery_reminder_count)
            update_display(full_update=True)
        return

    if change_date_active:
        # Datum ändern Modus
        if display.pressed(BUTTON_UP):
            temp_date -= 86400  # Datum um einen Tag verringern (86400 Sekunden)
        elif display.pressed(BUTTON_DOWN):
            temp_date += 86400  # Datum um einen Tag erhöhen (86400 Sekunden)
        elif display.pressed(BUTTON_A):
            # Datum bestätigen
            current_date = temp_date
            update_date_file(date_file, current_date)
            change_date_active = False
            menu_active = False
        elif display.pressed(BUTTON_C):
            # Datum ändern abbrechen
            temp_date = current_date
            change_date_active = False
        update_display(full_update=False)
        return

    if view_statistics_active:
        # Statistiken anzeigen Modus
        if display.pressed(BUTTON_C):
            # Statistiken anzeigen abbrechen
            view_statistics_active = False
        update_display(full_update=False)
        return

    if view_info_active:
        # Information anzeigen Modus
        if display.pressed(BUTTON_C):
            # Information anzeigen abbrechen
            view_info_active = False
        update_display(full_update=False)
        return

    if display.pressed(BUTTON_UP):
        if menu_active:
            # Menüoption ändern
            current_menu_option = (current_menu_option - 1) % len(menu_options)
        else:
            # Menü öffnen
            menu_active = True
            current_menu_option = 0
        update_display(full_update=False)
        return

    if display.pressed(BUTTON_DOWN):
        if menu_active:
            # Menüoption ändern
            current_menu_option = (current_menu_option + 1) % len(menu_options)
        else:
            # Tagesstatistiken speichern und zurücksetzen
            save_data(format_date(time.localtime(current_date)), espresso_count, cappuccino_count, other_count)
            current_date += 86400  # Inkrementiere das Datum um einen Tag (86400 Sekunden)
            update_date_file(date_file, current_date)  # Aktualisiere die Hilfsdatei mit dem neuen Datum
            espresso_count = 0
            cappuccino_count = 0
            other_count = 0
            battery_reminder_count += 1  # Erhöhe den Batterie-Erinnerungszähler
            if battery_reminder_count >= 10:
                battery_reminder_active = True
            button_press_count = 0  # Reset button press count after saving
            update_display(full_update=True)  # Führe ein volles Update beim Tageswechsel durch
            update_count_file(count_file, espresso_count, cappuccino_count, other_count, battery_reminder_count)  # Aktualisiere die Hilfsdatei mit den aktuellen Zählerständen und dem Batterie-Erinnerungszähler
        update_display(full_update=False)
        return

    if display.pressed(BUTTON_A):
        if menu_active:
            # Menüoption auswählen
            if current_menu_option == 0:  # Statistiken anzeigen
                view_statistics_active = True
            elif current_menu_option == 1:  # Tagesstatistiken zurücksetzen
                date_str = format_date(time.localtime(current_date))
                clear_today_log_entries(log_file, count_file, date_str)
                espresso_count = 0
                cappuccino_count = 0
                other_count = 0
            elif current_menu_option == 2:  # Gesamtstatistiken zurücksetzen
                clear_log_file(log_file)
                clear_count_file(count_file)
                espresso_count = 0
                cappuccino_count = 0
                other_count = 0
            elif current_menu_option == 3:  # Datum ändern
                change_date_active = True
                temp_date = current_date
            elif current_menu_option == 4:  # Information anzeigen
                view_info_active = True
            elif current_menu_option == 5:  # Beenden
                menu_active = False
            update_display(full_update=True)
            return
        else:
            espresso_count += 1
            button_press_count += 1

    if display.pressed(BUTTON_B):
        if not menu_active:
            cappuccino_count += 1
            button_press_count += 1

    if display.pressed(BUTTON_C):
        if menu_active:
            # Gehe eine Ebene nach oben im Menü
            if change_date_active:
                change_date_active = False
            elif view_statistics_active:
                view_statistics_active = False
            elif view_info_active:
                view_info_active = False
            else:
                menu_active = False
            update_display(full_update=True)
            return
        if not menu_active:
            other_count += 1
            button_press_count += 1

    # Display immer mit einem schnellen Update aktualisieren
    update_display(full_update=False)

    # Volles Update nur alle 10 Tastendrücke
    if button_press_count >= 10:
        update_display(full_update=True)
        button_press_count = 0

    # Aktualisiere die Hilfsdatei mit den aktuellen Zählerständen und dem Batterie-Erinnerungszähler
    update_count_file(count_file, espresso_count, cappuccino_count, other_count, battery_reminder_count)

# Hauptschleife
if __name__ == "__main__":
    # Aktivitäts-LED einschalten
    led.value(1)

    # Update display at start
    update_display(full_update=True)

    while True:
        if display.pressed(BUTTON_A) or display.pressed(BUTTON_B) or display.pressed(BUTTON_C) or display.pressed(BUTTON_UP) or display.pressed(BUTTON_DOWN):
            button_pressed(None)
        else:
            # LED ausschalten, wenn keine Aktivität stattfindet
            led.value(0)
        time.sleep(0.1)  # Kurze Pause, um Tastenanschläge zu erkennen

    # Aktivitäts-LED ausschalten
    led.value(0)