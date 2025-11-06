#!/usr/bin/env python3

# Test der Scrolling-Logik für beanOS Menüs

def test_main_menu_scrolling():
    """Test der Hauptmenü-Scrolling-Logik"""
    print("=== Hauptmenü Scrolling Test ===")
    
    # Simuliere die Parameter
    HEIGHT = 128
    menu_options = ["Bohnen", "Statistiken anzeigen", "Tagesstatistiken zurücksetzen", 
                   "Datum ändern", "Wartungshistorie", "Achievements", "Information"]
    
    # Berechne verfügbaren Platz
    available_height = HEIGHT - 20 - 6  # Abzüglich Titel und Margin
    item_height = 30  # Box-Höhe plus Abstand
    max_visible = min(available_height // item_height, len(menu_options))
    total_options = len(menu_options)
    
    print(f"Verfügbare Höhe: {available_height}px")
    print(f"Item-Höhe: {item_height}px") 
    print(f"Max sichtbare Items: {max_visible}")
    print(f"Gesamt Optionen: {total_options}")
    print()
    
    # Test verschiedene Auswahl-Positionen
    for current_menu_option in range(len(menu_options)):
        # Scrolling-Logik
        if current_menu_option < max_visible // 2:
            start_index = 0
        elif current_menu_option >= total_options - max_visible // 2:
            start_index = max(0, total_options - max_visible)
        else:
            start_index = current_menu_option - max_visible // 2
            
        end_index = min(total_options, start_index + max_visible)
        
        print(f"Auswahl: {current_menu_option} ({menu_options[current_menu_option]})")
        print(f"  Sichtbar: {start_index}-{end_index-1}")
        print(f"  Items: {[menu_options[i] for i in range(start_index, end_index)]}")
        print()

def test_maintenance_scrolling():
    """Test der Wartungshistorie-Scrolling-Logik"""
    print("=== Wartungshistorie Scrolling Test ===")
    
    HEIGHT = 128
    wartungstypen = [
        ("cleaning", "Reinigung"),
        ("descaling", "Entkalken"), 
        ("brew_group_cleaning", "Brühgruppe reinigen"),
        ("grinder_cleaning", "Mühle reinigen"),
        ("deep_cleaning", "Grundreinigung")
    ]
    
    items_per_page = (HEIGHT - 26) // 24  # Verfügbare Höhe geteilt durch Item-Höhe
    total_items = len(wartungstypen)
    max_scroll = max(0, total_items - items_per_page)
    
    print(f"Items pro Seite: {items_per_page}")
    print(f"Gesamt Items: {total_items}")
    print(f"Max Scroll: {max_scroll}")
    print()
    
    for selected in range(len(wartungstypen)):
        # Automatisches Scrolling
        maintenance_history_scroll = 0
        
        if selected < maintenance_history_scroll:
            maintenance_history_scroll = selected
        elif selected >= maintenance_history_scroll + items_per_page:
            maintenance_history_scroll = selected - items_per_page + 1
            
        maintenance_history_scroll = max(0, min(maintenance_history_scroll, max_scroll))
        
        start = maintenance_history_scroll
        end = min(total_items, maintenance_history_scroll + items_per_page)
        
        print(f"Auswahl: {selected} ({wartungstypen[selected][1]})")
        print(f"  Scroll: {maintenance_history_scroll}")
        print(f"  Sichtbar: {start}-{end-1}")
        print()

if __name__ == "__main__":
    test_main_menu_scrolling()
    test_maintenance_scrolling()