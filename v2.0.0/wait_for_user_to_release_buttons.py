import badger2040
import time

def wait_for_user_to_release_buttons():
    display = badger2040.Badger2040()
    while display.pressed_any():
        time.sleep(0.01)