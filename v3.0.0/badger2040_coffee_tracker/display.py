import badger2040

# Initialize Badger2040
badger = badger2040.Badger2040()

def display_main(current_date, espresso_count=0, cappuccino_count=0, other_count=0):
    badger.pen(0)
    badger.clear()
    badger.pen(15)
    badger.text(f"Date: {current_date}", 10, 10)
    badger.text(f"Espresso: {espresso_count}", 10, 30)
    badger.text(f"Cappuccino: {cappuccino_count}", 10, 50)
    badger.text(f"Other: {other_count}", 10, 70)
    badger.update()

def display_menu(current_menu):
    badger.pen(0)
    badger.clear()
    badger.pen(15)
    if current_menu == "main_menu":
        badger.text("> Einstellungen", 10, 10)
        badger.text("  Auswertung", 10, 30)
        badger.text("  Achievements", 10, 50)
        badger.text("  Impressum", 10, 70)
    badger.update()