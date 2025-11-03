#!/usr/bin/env python3
"""
Test-Skript für das beanOS Achievement-System
Demonstriert die neuen Funktionen:
1. Happy Bean Day = 10 Kaffees an einem Tag
2. Generisches Notification-System 
3. Achievement-Icon in der Titelleiste
"""

def test_happy_bean_day_logic():
    """Teste die neue Happy Bean Day Logik"""
    
    # Simuliere get_day_total_coffee Funktion
    def mock_get_day_total_coffee(date_str):
        # Simuliere verschiedene Kaffee-Mengen
        test_cases = {
            "01.01.2025": 5,   # Zu wenig für Happy Bean Day
            "02.01.2025": 10,  # Genau genug für Happy Bean Day
            "03.01.2025": 15,  # Mehr als genug
        }
        return test_cases.get(date_str, 0)
    
    # Teste verschiedene Szenarien
    test_dates = ["01.01.2025", "02.01.2025", "03.01.2025", "04.01.2025"]
    
    print("🧪 Test: Happy Bean Day Logik")
    print("=" * 40)
    
    for date in test_dates:
        total = mock_get_day_total_coffee(date)
        qualifies = total >= 10
        
        print(f"📅 {date}: {total} Kaffees")
        print(f"   🏆 Happy Bean Day: {'✅ JA' if qualifies else '❌ NEIN'}")
        print()

def test_notification_system():
    """Teste das Notification-System Konzept"""
    
    print("🔔 Test: Notification-System")
    print("=" * 40)
    
    # Simuliere verschiedene Benachrichtigungs-Typen
    notifications = [
        {"type": "achievement", "data": "happy_bean_day"},
        {"type": "achievement", "data": "coffee_100"},
        {"type": "maintenance", "data": ["cleaning", "descaling"]},
    ]
    
    for notif in notifications:
        print(f"📨 Notification-Typ: {notif['type']}")
        print(f"   📋 Daten: {notif['data']}")
        
        if notif['type'] == 'achievement':
            achievement_names = {
                "happy_bean_day": "Happy Bean Day - 10 Kaffees an einem Tag",
                "coffee_100": "Kaffee-Liebhaber - 100 Kaffees getrunken"
            }
            print(f"   🏆 Achievement: {achievement_names.get(notif['data'], 'Unbekannt')}")
            print(f"   🌟 Nach Bestätigung: Stern in Titelleiste bis nächster Tag")
            
        elif notif['type'] == 'maintenance':
            maintenance_names = {
                "cleaning": "Maschine reinigen",
                "descaling": "Maschine entkalken"
            }
            print(f"   🔧 Wartungsaufgaben:")
            for task in notif['data']:
                print(f"      - {maintenance_names.get(task, task)}")
                
        print()

def test_title_bar_logic():
    """Teste die Titelleisten-Icon Logik"""
    
    print("📊 Test: Titelleisten-Icon System")
    print("=" * 40)
    
    # Simuliere verschiedene Zustände
    states = [
        {"daily_achievement": False, "maintenance_warning": False},
        {"daily_achievement": True, "maintenance_warning": False},
        {"daily_achievement": False, "maintenance_warning": True},
        {"daily_achievement": True, "maintenance_warning": True},
    ]
    
    for i, state in enumerate(states, 1):
        print(f"🔍 Szenario {i}:")
        print(f"   🏆 Achievement heute: {'✅ JA' if state['daily_achievement'] else '❌ NEIN'}")
        print(f"   ⚠️  Wartung fällig: {'✅ JA' if state['maintenance_warning'] else '❌ NEIN'}")
        
        # Titelleisten-Layout von rechts nach links: Datum | ! | ★
        title_icons = []
        title_icons.append("31.10.25")  # Datum immer da
        
        if state['maintenance_warning']:
            title_icons.insert(0, "!")
            
        if state['daily_achievement']:
            title_icons.insert(0, "★")
        
        print(f"   📱 Titelleiste: {' '.join(title_icons)}")
        print()

if __name__ == "__main__":
    print("🚀 beanOS Achievement-System Tests")
    print("="*50)
    print()
    
    test_happy_bean_day_logic()
    test_notification_system()
    test_title_bar_logic()
    
    print("✅ Alle Tests abgeschlossen!")
    print()
    print("📝 Zusammenfassung der Neuerungen:")
    print("   1. ✨ Happy Bean Day: 10 Kaffees statt alle 6 Getränketypen")
    print("   2. 🔔 Generisches Notification-System für Achievements + Wartung")
    print("   3. 🌟 Achievement-Stern in Titelleiste bis zum nächsten Tag")
    print("   4. 🏗️  Wiederverwendbare Notification-Infrastruktur für Zukunft")