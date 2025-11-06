#!/usr/bin/env python3
"""
Test script to debug the Bohnen menu issue
"""

# Simulate the menu logic without hardware dependencies
menu_options = ["Bohnen", "Statistiken anzeigen", "Tagesstatistiken zurücksetzen", "Datum ändern", "Wartungshistorie", "Achievements", "Information"]
drink_menu_options = ["lungo", "iced latte", "affogato", "shakerato", "espresso tonic", "other"]

# State variables
current_menu_option = 0
menu_active = False
drink_menu_active = False
current_drink_menu_option = 0

def test_menu_navigation():
    global current_menu_option, menu_active, drink_menu_active
    
    print("=== Menu Navigation Test ===")
    print(f"Initial state: menu_active={menu_active}, drink_menu_active={drink_menu_active}")
    
    # Simulate opening main menu
    menu_active = True
    print(f"After opening menu: menu_active={menu_active}")
    print(f"Current menu option: {current_menu_option} ({menu_options[current_menu_option]})")
    
    # Simulate selecting "Bohnen" (option 0)
    if current_menu_option == 0:
        print(f"Selecting 'Bohnen' menu...")
        drink_menu_active = True
        menu_active = False
        print(f"After selection: menu_active={menu_active}, drink_menu_active={drink_menu_active}")
        
        # Display drink menu
        print("\nDrink menu should show:")
        for i, option in enumerate(drink_menu_options):
            prefix = "> " if i == current_drink_menu_option else "  "
            print(f"{prefix}{option}")

if __name__ == "__main__":
    test_menu_navigation()