from show_menu import show_menu
from settings_sub_options import settings_sub_options
from beancounter import show_beancounter
import badger2040
import machine
import time

# Initialisierung des Badger2040
display = badger2040.Badger2040()

# GPIO-Pins für die Tasten
BUTTON_A = badger2040.BUTTON_A
BUTTON_B = badger2040.BUTTON_B
BUTTON_C = badger2040.BUTTON_C
BUTTON_UP = badger2040.BUTTON_UP
BUTTON_DOWN = badger2040.BUTTON_DOWN
LED = 25

# Initialisiere die LED als Ausgang
led = machine.Pin(LED, machine.Pin.OUT)

# Einstellungen, Auswertung, Achievements, Impressum-Menü
settings_options = ["BeanCounter", "Einstellungen", "Auswertung", "Achievements", "Impressum"]

def button_pressed(pin):
    if pin == BUTTON_A:
        show_beancounter()
    elif pin == BUTTON_UP:
        show_menu(settings_options, "Hauptmenü")

def main():
    led.value(1)
    show_beancounter()
    while True:
        if display.pressed(BUTTON_A):
            button_pressed(BUTTON_A)
        elif display.pressed(BUTTON_UP):
            button_pressed(BUTTON_UP)
        time.sleep(0.1)
    led.value(0)

if __name__ == "__main__":
    main()