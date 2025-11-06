#!/usr/bin/env python3

# Test der neuen Bean-Pack Anzeige Funktionalität

def test_bean_pack_display():
    """Test der Bean-Pack Anzeige mit verschiedenen Szenarien"""
    
    print("=== Bean-Pack Anzeige Test ===")
    
    # Simuliere verschiedene Szenarien
    scenarios = [
        # Scenario 1: Keine Packungen
        {
            "name": "Keine Packungen",
            "packs": [],
            "count": 0
        },
        # Scenario 2: Eine Packung
        {
            "name": "Eine Packung", 
            "packs": [("15.10.2024", "1000g")],
            "count": 1
        },
        # Scenario 3: Zwei Packungen
        {
            "name": "Zwei Packungen",
            "packs": [("10.10.2024", "500g"), ("15.10.2024", "1000g")],
            "count": 2
        },
        # Scenario 4: Mehrere Packungen (zeige nur letzte zwei)
        {
            "name": "Mehrere Packungen",
            "packs": [("01.10.2024", "750g"), ("10.10.2024", "500g"), ("15.10.2024", "1000g")],
            "count": 3
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"Packungen: {scenario['count']}")
        
        # Simuliere die Anzeige-Logik
        last_packs = scenario['packs'][-2:] if len(scenario['packs']) >= 2 else scenario['packs']
        
        if len(last_packs) >= 2:
            # Zweitletzte und letzte Packung
            datum2, groesse2 = last_packs[0]
            datum1, groesse1 = last_packs[1]
            print(f"{groesse2} {datum2}")
            print(f"{groesse1} {datum1}")
        elif len(last_packs) == 1:
            # Nur eine Packung
            datum1, groesse1 = last_packs[0]
            print(f"{groesse1} {datum1}")
        else:
            # Keine Packungen
            print("Keine Packungen")
    
    print("\n=== Layout Test ===")
    HEIGHT = 128
    positions = [26, 46, 66]  # Packungen, Pack1, Pack2
    
    for i, (label, y) in enumerate(zip(["Packungen: 5", "1000g 15.10.2024", "500g 10.10.2024"], positions)):
        text_height = 16  # scale=2
        bottom = y + text_height
        print(f"{label}: y={y}, bottom={bottom}, fits={'✅' if bottom <= HEIGHT else '❌'}")

if __name__ == "__main__":
    test_bean_pack_display()