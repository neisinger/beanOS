#!/usr/bin/env python3
"""
beanOS Android – Coffee Consumption Tracker
============================================

A Kivy-based Android companion app for beanOS.
Tracks coffee consumption, achievements and statistics –
the same data model as the Badger2040 version.

Visual style: E-Paper / E-Ink (white background, black ink, bordered boxes,
separator lines), mirroring the Pimoroni Badger2040 display aesthetic.
Locked to landscape orientation (buildozer.spec: orientation = landscape).

Home screen mirrors the Badger2040 main_screen.svg:
  - Three tappable counter boxes: ESPRESSO (+1), CAPPUCCINO (+1), ANDERE (opens drink sub-menu)
  - Bottom action bar: Tageswechsel | Statistik | Wartung | Menü

Build for Android:
    pip install buildozer
    cd android && buildozer android debug

Author: Joao Neisinger
License: GNU GPLv3
Repository: https://github.com/neisinger/beanOS

This code must not be used by fascists! No code for the AfD or Musk or Trump!
"""

import json
import os
from datetime import date, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_FILE = "beanos_data.json"
APP_VERSION = "1.0.0 (Android)"

# Other drinks beyond Espresso / Cappuccino (matches Badger2040 drink_menu_options)
OTHER_DRINKS = ["Lungo", "Iced Latte", "Affogato", "Shakerato", "Espresso Tonic", "Other"]

# All tracked drinks
DRINKS = ["Espresso", "Cappuccino"] + OTHER_DRINKS

# Caffeine estimates in mg
CAFFEINE_MG = {
    "Espresso": 63, "Cappuccino": 63, "Lungo": 80,
    "Iced Latte": 63, "Affogato": 63, "Shakerato": 63,
    "Espresso Tonic": 63, "Other": 63,
}

# Bean usage in grams per drink
BEAN_GRAMS = {
    "Espresso": 7, "Cappuccino": 7, "Lungo": 10,
    "Iced Latte": 14, "Affogato": 7, "Shakerato": 7,
    "Espresso Tonic": 7, "Other": 7,
}

# Maintenance tasks (matches MAINTENANCE_TASKS in Badger2040 main.py)
MAINTENANCE_TASKS = [
    {"key": "cleaning",            "name": "Reinigung",          "interval_days": 7},
    {"key": "descaling",           "name": "Entkalken",          "interval_days": 28},
    {"key": "brew_group_cleaning", "name": "Brühgruppe reinigen","interval_days": 42},
    {"key": "grinder_cleaning",    "name": "Mühle reinigen",     "interval_days": 56},
    {"key": "deep_cleaning",       "name": "Grundreinigung",     "interval_days": 365},
]

# ---------------------------------------------------------------------------
# E-Paper colour palette (Badger2040 E-Ink display aesthetics)
# ---------------------------------------------------------------------------

COLOR_PAPER   = (1, 1, 1, 1)             # white paper
COLOR_INK     = (0, 0, 0, 1)             # black ink
COLOR_INK_DIM = (0.45, 0.45, 0.45, 1)   # gray (secondary / locked)

# ---------------------------------------------------------------------------
# Achievement definitions (identical to Badger2040 version)
# ---------------------------------------------------------------------------

ACHIEVEMENT_DEFINITIONS = {
    "first_coffee":   {"name": "Erster Kaffee",      "desc": "Dein allererster Kaffee!",         "category": "Meilensteine"},
    "coffee_10":      {"name": "Kaffee-Starter",     "desc": "10 Kaffees getrunken",             "category": "Meilensteine"},
    "coffee_50":      {"name": "Kaffee-Fan",         "desc": "50 Kaffees getrunken",             "category": "Meilensteine"},
    "coffee_100":     {"name": "Kaffee-Liebhaber",   "desc": "100 Kaffees getrunken",            "category": "Meilensteine"},
    "coffee_500":     {"name": "Kaffee-Experte",     "desc": "500 Kaffees getrunken",            "category": "Meilensteine"},
    "coffee_1000":    {"name": "Kaffee-Meister",     "desc": "1000 Kaffees getrunken",           "category": "Meilensteine"},
    "streak_7":       {"name": "Consistency Expert", "desc": "7 Tage in Folge Kaffee",          "category": "Streaks"},
    "streak_30":      {"name": "Consistency Master", "desc": "30 Tage in Folge Kaffee",         "category": "Streaks"},
    "stay_cool":      {"name": "Stay Cool",          "desc": "Ersten Iced Latte getrunken",      "category": "Spezialgetränke"},
    "dessert":        {"name": "Dessert",            "desc": "Ersten Affogato getrunken",        "category": "Spezialgetränke"},
    "shaker":         {"name": "Shake it!",          "desc": "Ersten Shakerato getrunken",       "category": "Spezialgetränke"},
    "tonic":          {"name": "Tonic Twist",        "desc": "Ersten Espresso Tonic getrunken",  "category": "Spezialgetränke"},
    "clean_machine":  {"name": "Saubere Maschine",   "desc": "Erste Wartung durchgeführt",       "category": "Wartung"},
    "barista":        {"name": "Barista",            "desc": "Alle Getränketypen probiert",     "category": "Experimentell"},
    "happy_bean_day": {"name": "Happy Bean Day",     "desc": "10 Kaffees an einem Tag",          "category": "Experimentell"},
}

# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------

def _today():
    return date.today().isoformat()


def _default_data():
    return {
        "log": {},           # { "YYYY-MM-DD": { drink: count } }
        "achievements": {},  # { key: "YYYY-MM-DD" }
        "maintenance": {},   # { task_key: "YYYY-MM-DD" }
    }


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                d.setdefault("maintenance", {})
                return d
        except (json.JSONDecodeError, OSError):
            pass
    return _default_data()


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def today_counts(data):
    return data["log"].get(_today(), {})


def total_counts(data):
    totals = {d: 0 for d in DRINKS}
    for day_entry in data["log"].values():
        for drink, count in day_entry.items():
            if drink in totals:
                totals[drink] += count
    return totals


def total_coffee(data):
    return sum(total_counts(data).values())


def add_drink(data, drink):
    today = _today()
    data["log"].setdefault(today, {})
    data["log"][today][drink] = data["log"][today].get(drink, 0) + 1


def reset_today(data):
    data["log"].pop(_today(), None)


def calculate_streak(data):
    streak = 0
    check = date.today()
    while data["log"].get(check.isoformat()):
        streak += 1
        check -= timedelta(days=1)
    return streak


def check_achievements(data):
    unlocked = data["achievements"]
    new_keys = []
    today = _today()
    tc = total_coffee(data)

    for threshold, key in [(1, "first_coffee"), (10, "coffee_10"), (50, "coffee_50"),
                           (100, "coffee_100"), (500, "coffee_500"), (1000, "coffee_1000")]:
        if tc >= threshold and key not in unlocked:
            unlocked[key] = today
            new_keys.append(key)

    day = today_counts(data)
    for drink, key in [("Iced Latte", "stay_cool"), ("Affogato", "dessert"),
                       ("Shakerato", "shaker"), ("Espresso Tonic", "tonic")]:
        if day.get(drink, 0) > 0 and key not in unlocked:
            unlocked[key] = today
            new_keys.append(key)

    if all(any(e.get(d, 0) > 0 for e in data["log"].values()) for d in DRINKS):
        if "barista" not in unlocked:
            unlocked["barista"] = today
            new_keys.append("barista")

    if sum(day.values()) >= 10 and "happy_bean_day" not in unlocked:
        unlocked["happy_bean_day"] = today
        new_keys.append("happy_bean_day")

    streak = calculate_streak(data)
    if streak >= 7 and "streak_7" not in unlocked:
        unlocked["streak_7"] = today
        new_keys.append("streak_7")
    if streak >= 30 and "streak_30" not in unlocked:
        unlocked["streak_30"] = today
        new_keys.append("streak_30")

    if data["maintenance"] and "clean_machine" not in unlocked:
        unlocked["clean_machine"] = today
        new_keys.append("clean_machine")

    return new_keys


def maintenance_overdue(data):
    """Return list of task keys that are overdue."""
    overdue = []
    today = date.today()
    for task in MAINTENANCE_TASKS:
        last = data["maintenance"].get(task["key"])
        if last is None:
            overdue.append(task["key"])
        else:
            if (today - date.fromisoformat(last)).days > task["interval_days"]:
                overdue.append(task["key"])
    return overdue


# ---------------------------------------------------------------------------
# UI helpers – E-Paper style
# ---------------------------------------------------------------------------

def _set_bg(widget, color):
    with widget.canvas.before:
        Color(*color)
        r = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(
        pos=lambda w, v: setattr(r, "pos", v),
        size=lambda w, v: setattr(r, "size", v),
    )


def _label(text, font_size=dp(15), bold=False, color=COLOR_INK, **kw):
    lbl = Label(text=text, font_size=font_size, bold=bold, color=color, **kw)
    if kw.get("halign") in ("left", "right"):
        lbl.bind(size=lambda w, _: setattr(w, "text_size", (w.width, None)))
    return lbl


def _button(text, on_press=None, bg=COLOR_INK, text_color=COLOR_PAPER,
            font_size=dp(15), **kw):
    btn = Button(
        text=text, font_size=font_size,
        background_normal="", background_color=bg, color=text_color, **kw,
    )
    if on_press:
        btn.bind(on_press=on_press)
    return btn


def _title_bar(text, right_text=""):
    """Full-width black title bar – mirrors Badger2040 style."""
    bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40),
                    padding=(dp(10), dp(4)), spacing=dp(4))
    _set_bg(bar, COLOR_INK)
    bar.add_widget(_label(text, font_size=dp(16), bold=True, color=COLOR_PAPER,
                          halign="left"))
    if right_text:
        bar.add_widget(_label(right_text, font_size=dp(12), color=COLOR_PAPER,
                              halign="right"))
    return bar


def _section_header(text):
    bar = BoxLayout(size_hint_y=None, height=dp(26), padding=(dp(8), dp(3)))
    _set_bg(bar, COLOR_INK)
    bar.add_widget(_label(text, font_size=dp(12), bold=True, color=COLOR_PAPER))
    return bar


def _separator():
    sep = BoxLayout(size_hint_y=None, height=dp(1))
    _set_bg(sep, COLOR_INK)
    return sep


def _eink_progress_bar(current, maximum):
    outer = BoxLayout(size_hint_y=None, height=dp(14), padding=dp(1))
    _set_bg(outer, COLOR_INK)
    inner = BoxLayout()
    _set_bg(inner, COLOR_PAPER)
    ratio = min(current / maximum, 1.0) if maximum > 0 else 0.0
    if ratio > 0:
        fill = BoxLayout(size_hint_x=ratio)
        _set_bg(fill, COLOR_INK)
        inner.add_widget(fill)
    if ratio < 1.0:
        space = BoxLayout(size_hint_x=1.0 - ratio)
        _set_bg(space, COLOR_PAPER)
        inner.add_widget(space)
    outer.add_widget(inner)
    return outer


def _bottom_bar(buttons):
    """
    Bottom action bar matching the Badger2040 button layout.
    buttons: list of (label, callback) tuples.
    """
    wrapper = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(50))
    _set_bg(wrapper, COLOR_PAPER)
    wrapper.add_widget(_separator())
    bar = BoxLayout(orientation="horizontal")
    _set_bg(bar, COLOR_PAPER)
    for i, (lbl_text, cb) in enumerate(buttons):
        btn = _button(lbl_text, on_press=lambda _, c=cb: c(),
                      bg=COLOR_PAPER, text_color=COLOR_INK, font_size=dp(13))
        bar.add_widget(btn)
        if i < len(buttons) - 1:
            vsep = BoxLayout(size_hint_x=None, width=dp(1))
            _set_bg(vsep, COLOR_INK)
            bar.add_widget(vsep)
    wrapper.add_widget(bar)
    return wrapper


# ---------------------------------------------------------------------------
# Counter box widget – tappable bordered box (mimics Badger2040 main_screen.svg)
# ---------------------------------------------------------------------------

class CounterBox(ButtonBehavior, BoxLayout):
    """Bordered counter box that acts as a tap button."""
    def __init__(self, caption, on_tap=None, **kwargs):
        super().__init__(orientation="vertical", padding=dp(1), **kwargs)
        _set_bg(self, COLOR_INK)

        self._inner = BoxLayout(orientation="vertical",
                                padding=(dp(6), dp(4)), spacing=dp(2))
        _set_bg(self._inner, COLOR_PAPER)

        self._count_lbl = _label("0", font_size=dp(36), bold=True, color=COLOR_INK)
        self._name_lbl  = _label(caption, font_size=dp(10), color=COLOR_INK)

        self._inner.add_widget(self._count_lbl)
        self._inner.add_widget(self._name_lbl)
        self.add_widget(self._inner)

        if on_tap:
            self.bind(on_press=lambda *_: on_tap())

    @property
    def count(self):
        return int(self._count_lbl.text)

    @count.setter
    def count(self, value):
        self._count_lbl.text = str(value)


# ---------------------------------------------------------------------------
# Popup helpers
# ---------------------------------------------------------------------------

def _make_popup(content, size_hint=(0.92, 0.85)):
    return Popup(
        title="", content=content,
        size_hint=size_hint,
        background_color=COLOR_PAPER,
        separator_height=0,
        title_size=0,
    )


def show_drinks_popup(app, on_drink_added):
    """Getränkeauswahl popup – list of OTHER_DRINKS with count + + button."""
    content = BoxLayout(orientation="vertical", spacing=0, padding=0)
    _set_bg(content, COLOR_PAPER)
    content.add_widget(_title_bar("GETRÄNKEAUSWAHL",
                                  date.today().strftime("%d.%m.%y")))

    scroll = ScrollView()
    container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
    container.bind(minimum_height=container.setter("height"))
    _set_bg(container, COLOR_PAPER)

    count_labels = {}
    counts = today_counts(app.data)
    for drink in OTHER_DRINKS:
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52),
                        padding=(dp(10), dp(6)), spacing=dp(8))
        _set_bg(row, COLOR_PAPER)
        row.add_widget(_label(drink, font_size=dp(15), color=COLOR_INK,
                              halign="left"))
        c_lbl = _label(str(counts.get(drink, 0)), font_size=dp(15), bold=True,
                       color=COLOR_INK, size_hint_x=None, width=dp(36))
        count_labels[drink] = c_lbl
        row.add_widget(c_lbl)

        def _add(_, d=drink):
            add_drink(app.data, d)
            count_labels[d].text = str(today_counts(app.data).get(d, 0))
            new_ach = check_achievements(app.data)
            save_data(app.data)
            on_drink_added()
            for key in new_ach:
                show_achievement_popup(key)

        row.add_widget(_button("+", on_press=_add, bg=COLOR_INK,
                               text_color=COLOR_PAPER, font_size=dp(20),
                               size_hint_x=None, width=dp(44)))
        container.add_widget(row)
        container.add_widget(_separator())

    scroll.add_widget(container)
    content.add_widget(scroll)

    popup = _make_popup(content, size_hint=(0.90, 0.90))
    close_btn = _button("Zurück", bg=COLOR_INK, text_color=COLOR_PAPER,
                        size_hint_y=None, height=dp(44))
    close_btn.bind(on_press=lambda *_: popup.dismiss())
    content.add_widget(close_btn)
    popup.open()


def show_menu_popup(app, screen_manager):
    """Badger-style menu popup with all menu options."""
    content = BoxLayout(orientation="vertical", spacing=0, padding=0)
    _set_bg(content, COLOR_PAPER)
    content.add_widget(_title_bar("MENÜ", date.today().strftime("%d.%m.%y")))

    popup = _make_popup(content, size_hint=(0.70, 0.90))

    scroll = ScrollView()
    container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
    container.bind(minimum_height=container.setter("height"))
    _set_bg(container, COLOR_PAPER)

    def _nav(name):
        popup.dismiss()
        screen_manager.current = name

    def _item(label, action):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52),
                        padding=(dp(12), dp(8)))
        _set_bg(row, COLOR_PAPER)
        row.add_widget(_label(label, font_size=dp(15), color=COLOR_INK,
                              halign="left"))
        btn = _button(">", bg=COLOR_PAPER, text_color=COLOR_INK,
                      font_size=dp(16), size_hint_x=None, width=dp(36))
        btn.bind(on_press=lambda *_: action())
        row.add_widget(btn)
        container.add_widget(row)
        container.add_widget(_separator())

    def _reset_today():
        popup.dismiss()
        show_confirm_reset(app, screen_manager)

    _item("Bohnen",                        lambda: show_beans_popup(app))
    _item("Statistiken anzeigen",          lambda: _nav("stats"))
    _item("Tagesstatistiken zurücksetzen", _reset_today)
    _item("Datum ändern",                 lambda: show_date_popup())
    _item("Wartungshistorie",              lambda: _nav("wartung"))
    _item("Achievements",                  lambda: _nav("achievements"))
    _item("Information",                   lambda: show_info_popup())

    scroll.add_widget(container)
    content.add_widget(scroll)

    close_btn = _button("Schließen", bg=COLOR_INK, text_color=COLOR_PAPER,
                        size_hint_y=None, height=dp(44))
    close_btn.bind(on_press=lambda *_: popup.dismiss())
    content.add_widget(close_btn)
    popup.open()


def show_beans_popup(app):
    content = BoxLayout(orientation="vertical", spacing=0, padding=0)
    _set_bg(content, COLOR_PAPER)
    content.add_widget(_title_bar("BOHNEN", date.today().strftime("%d.%m.%y")))

    body = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(8))
    _set_bg(body, COLOR_PAPER)

    tot = total_counts(app.data)
    total_beans = sum(BEAN_GRAMS.get(d, 7) * c for d, c in tot.items())
    bean_packs = total_beans / 250

    body.add_widget(_label(f"Bohnen gesamt: ~{total_beans} g",
                           font_size=dp(14), color=COLOR_INK))
    body.add_widget(_separator())
    body.add_widget(_label(f"Bohnenpakete (250g): ~{bean_packs:.1f}",
                           font_size=dp(14), color=COLOR_INK))
    body.add_widget(_separator())
    body.add_widget(_label(f"Kaffees gesamt: {total_coffee(app.data)}",
                           font_size=dp(14), color=COLOR_INK))
    body.add_widget(BoxLayout())

    popup = _make_popup(content, size_hint=(0.70, 0.65))
    ok_btn = _button("OK", bg=COLOR_INK, text_color=COLOR_PAPER,
                     size_hint_y=None, height=dp(44))
    ok_btn.bind(on_press=lambda *_: popup.dismiss())
    body.add_widget(ok_btn)
    content.add_widget(body)
    popup.open()


def show_date_popup():
    content = BoxLayout(orientation="vertical", spacing=0, padding=0)
    _set_bg(content, COLOR_PAPER)
    content.add_widget(_title_bar("DATUM ÄNDERN", date.today().strftime("%d.%m.%y")))

    body = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
    _set_bg(body, COLOR_PAPER)
    body.add_widget(_label(date.today().strftime("%d.%m.%Y"),
                           font_size=dp(28), bold=True, color=COLOR_INK))
    body.add_widget(_separator())
    body.add_widget(_label("Datum wird automatisch\nvom Gerät bezogen.",
                           font_size=dp(13), color=COLOR_INK_DIM))
    body.add_widget(BoxLayout())

    popup = _make_popup(content, size_hint=(0.60, 0.55))
    ok_btn = _button("OK", bg=COLOR_INK, text_color=COLOR_PAPER,
                     size_hint_y=None, height=dp(44))
    ok_btn.bind(on_press=lambda *_: popup.dismiss())
    body.add_widget(ok_btn)
    content.add_widget(body)
    popup.open()


def show_info_popup():
    content = BoxLayout(orientation="vertical", spacing=0, padding=0)
    _set_bg(content, COLOR_PAPER)
    content.add_widget(_title_bar("INFORMATION", date.today().strftime("%d.%m.%y")))

    body = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(6))
    _set_bg(body, COLOR_PAPER)

    rows = [
        ("beanOS Android", APP_VERSION),
        ("Entwickelt von:", "Joao Neisinger"),
        ("Lizenz:", "GNU GPLv3"),
        ("Hardware:", "Badger2040 (Original)"),
    ]
    for lbl, val in rows:
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36))
        _set_bg(row, COLOR_PAPER)
        row.add_widget(_label(lbl, font_size=dp(13), color=COLOR_INK_DIM,
                              halign="left"))
        row.add_widget(_label(val, font_size=dp(13), bold=True, color=COLOR_INK,
                              halign="right"))
        body.add_widget(row)
        body.add_widget(_separator())
    body.add_widget(BoxLayout())

    popup = _make_popup(content, size_hint=(0.75, 0.70))
    ok_btn = _button("OK", bg=COLOR_INK, text_color=COLOR_PAPER,
                     size_hint_y=None, height=dp(44))
    ok_btn.bind(on_press=lambda *_: popup.dismiss())
    body.add_widget(ok_btn)
    content.add_widget(body)
    popup.open()


def show_confirm_reset(app, screen_manager):
    content = BoxLayout(orientation="vertical", spacing=0, padding=0)
    _set_bg(content, COLOR_PAPER)
    content.add_widget(_title_bar("TAGESWECHSEL"))

    body = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
    _set_bg(body, COLOR_PAPER)
    body.add_widget(_label("Tagesstatistiken zurücksetzen?",
                           font_size=dp(15), color=COLOR_INK))
    body.add_widget(_separator())
    body.add_widget(_label("Alle Einträge fuer heute werden gelöscht.",
                           font_size=dp(13), color=COLOR_INK_DIM))
    body.add_widget(BoxLayout())

    popup = _make_popup(content, size_hint=(0.70, 0.55))

    btn_row = BoxLayout(orientation="horizontal", size_hint_y=None,
                        height=dp(44), spacing=dp(1))
    _set_bg(btn_row, COLOR_INK)

    cancel_btn = _button("Abbrechen", bg=COLOR_PAPER, text_color=COLOR_INK,
                         font_size=dp(14))
    cancel_btn.bind(on_press=lambda *_: popup.dismiss())

    def _do_reset(*_):
        reset_today(app.data)
        save_data(app.data)
        popup.dismiss()
        home = screen_manager.get_screen("home")
        home._refresh()

    confirm_btn = _button("Zurücksetzen", bg=COLOR_INK, text_color=COLOR_PAPER,
                          font_size=dp(14))
    confirm_btn.bind(on_press=_do_reset)

    btn_row.add_widget(cancel_btn)
    btn_row.add_widget(confirm_btn)
    body.add_widget(btn_row)
    content.add_widget(body)
    popup.open()


def show_achievement_popup(key):
    defn = ACHIEVEMENT_DEFINITIONS.get(key, {})
    content = BoxLayout(orientation="vertical", spacing=0, padding=0)
    _set_bg(content, COLOR_PAPER)
    content.add_widget(_title_bar("[*] Achievement freigeschaltet!"))

    body = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
    _set_bg(body, COLOR_PAPER)
    body.add_widget(_label(defn.get("name", key), font_size=dp(20), bold=True,
                           color=COLOR_INK))
    body.add_widget(_separator())
    body.add_widget(_label(defn.get("desc", ""), font_size=dp(14), color=COLOR_INK))
    body.add_widget(BoxLayout())

    popup = _make_popup(content, size_hint=(0.85, 0.50))
    ok_btn = _button("OK", bg=COLOR_INK, text_color=COLOR_PAPER,
                     size_hint_y=None, height=dp(40))
    ok_btn.bind(on_press=lambda *_: popup.dismiss())
    body.add_widget(ok_btn)
    content.add_widget(body)
    popup.open()
    Clock.schedule_once(lambda dt: popup.dismiss(), 4)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

class HomeScreen(Screen):
    """
    Main screen – mirrors Badger2040 main_screen.svg layout.
    Three tappable counter boxes fill the middle area.
    Bottom bar: Tageswechsel | Statistik | Wartung | Menü
    """
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="home", **kwargs)
        self.app = app_ref
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        _set_bg(root, COLOR_PAPER)

        # Title bar
        root.add_widget(_title_bar("beanOS", date.today().strftime("%d.%m.%y")))

        # Three counter boxes (fill all remaining vertical space between title and nav)
        boxes_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            padding=(dp(10), dp(10)),
        )
        _set_bg(boxes_row, COLOR_PAPER)

        self.espresso_box   = CounterBox("ESPRESSO",
                                         on_tap=lambda: self._add("Espresso"))
        self.cappuccino_box = CounterBox("CAPPUCCINO",
                                         on_tap=lambda: self._add("Cappuccino"))
        self.andere_box     = CounterBox("ANDERE",
                                         on_tap=self._open_drinks)

        boxes_row.add_widget(self.espresso_box)
        boxes_row.add_widget(self.cappuccino_box)
        boxes_row.add_widget(self.andere_box)
        root.add_widget(boxes_row)

        # Bottom action bar
        root.add_widget(_bottom_bar([
            ("Tageswechsel", self._tageswechsel),
            ("Statistik",    self._to_stats),
            ("Wartung",      self._to_wartung),
            ("Menü",        self._open_menu),
        ]))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        t = today_counts(self.app.data)
        self.espresso_box.count   = t.get("Espresso", 0)
        self.cappuccino_box.count = t.get("Cappuccino", 0)
        self.andere_box.count     = sum(t.get(d, 0) for d in OTHER_DRINKS)

    def _add(self, drink):
        add_drink(self.app.data, drink)
        new_ach = check_achievements(self.app.data)
        save_data(self.app.data)
        self._refresh()
        for key in new_ach:
            show_achievement_popup(key)

    def _open_drinks(self):
        show_drinks_popup(self.app, on_drink_added=self._refresh)

    def _tageswechsel(self):
        show_confirm_reset(self.app, self.manager)

    def _to_stats(self):
        self.manager.current = "stats"

    def _to_wartung(self):
        self.manager.current = "wartung"

    def _open_menu(self):
        show_menu_popup(self.app, self.manager)


class StatsScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="stats", **kwargs)
        self.app = app_ref
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        _set_bg(root, COLOR_PAPER)
        root.add_widget(_title_bar("GESAMTSTATISTIK", date.today().strftime("%d.%m.%y")))

        scroll = ScrollView()
        self.layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
        self.layout.bind(minimum_height=self.layout.setter("height"))
        _set_bg(self.layout, COLOR_PAPER)
        scroll.add_widget(self.layout)
        root.add_widget(scroll)

        root.add_widget(_bottom_bar([
            ("< Zurück", lambda: setattr(self.manager, "current", "home")),
        ]))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        self.layout.clear_widgets()
        data = self.app.data
        t_counts = today_counts(data)
        tot_counts = total_counts(data)
        streak = calculate_streak(data)
        tc_total = total_coffee(data)
        total_days = len(data["log"])

        def _row(text, value, invert=False):
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(36),
                            padding=(dp(10), dp(4)))
            if invert:
                _set_bg(box, COLOR_INK)
                box.add_widget(_label(text, font_size=dp(13), bold=True,
                                      color=COLOR_PAPER, halign="left"))
                box.add_widget(_label(str(value), font_size=dp(13), bold=True,
                                      color=COLOR_PAPER, halign="right"))
            else:
                _set_bg(box, COLOR_PAPER)
                box.add_widget(_label(text, font_size=dp(13), color=COLOR_INK,
                                      halign="left"))
                box.add_widget(_label(str(value), font_size=dp(13), bold=True,
                                      color=COLOR_INK, halign="right"))
            return box

        # Today section – mirroring statistics_view.svg
        t_esp = t_counts.get("Espresso", 0)
        t_cap = t_counts.get("Cappuccino", 0)
        t_other = sum(t_counts.get(d, 0) for d in OTHER_DRINKS)
        today_total = t_esp + t_cap + t_other
        caffeine = sum(CAFFEINE_MG.get(d, 63) * c for d, c in t_counts.items())
        beans_today = sum(BEAN_GRAMS.get(d, 7) * c for d, c in t_counts.items())

        self.layout.add_widget(_section_header("HEUTE"))
        self.layout.add_widget(_row("Espresso", t_esp))
        self.layout.add_widget(_separator())
        self.layout.add_widget(_row("Cappuccino", t_cap))
        self.layout.add_widget(_separator())
        self.layout.add_widget(_row("Andere", t_other))
        self.layout.add_widget(_separator())
        self.layout.add_widget(_row("Koffein", f"~{caffeine} mg"))
        self.layout.add_widget(_separator())
        self.layout.add_widget(_row("Bohnen", f"~{beans_today} g"))
        self.layout.add_widget(_separator())
        self.layout.add_widget(_row(f"Gesamt: {today_total}  Streak: {streak}d", "", invert=True))

        # Overall section
        tot_esp = tot_counts.get("Espresso", 0)
        tot_cap = tot_counts.get("Cappuccino", 0)
        tot_other = sum(tot_counts.get(d, 0) for d in OTHER_DRINKS)
        total_beans_g = sum(BEAN_GRAMS.get(d, 7) * c for d, c in tot_counts.items())
        avg_per_day = round(tc_total / max(total_days, 1), 1)

        self.layout.add_widget(_section_header("GESAMT"))
        self.layout.add_widget(_row(f"Espresso: {tot_esp}", f"({round(tot_esp/max(total_days,1),1)}/Tag)"))
        self.layout.add_widget(_separator())
        self.layout.add_widget(_row(f"Cappuccino: {tot_cap}", f"({round(tot_cap/max(total_days,1),1)}/Tag)"))
        self.layout.add_widget(_separator())
        self.layout.add_widget(_row(f"Andere: {tot_other}", f"({round(tot_other/max(total_days,1),1)}/Tag)"))
        self.layout.add_widget(_separator())
        self.layout.add_widget(_row(f"Gesamt: {tc_total}  |  {total_beans_g}g  |  {avg_per_day}g/Tag", "",
                                    invert=True))

        # Streak progress
        next_ms = 7 if streak < 7 else 30 if streak < 30 else None
        if next_ms:
            self.layout.add_widget(_section_header(f"STREAK ZIEL: {next_ms} TAGE"))
            pb_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24),
                               padding=(dp(8), dp(4)), spacing=dp(6))
            _set_bg(pb_row, COLOR_PAPER)
            pb_row.add_widget(_eink_progress_bar(streak, next_ms))
            pb_row.add_widget(_label(f"{streak}/{next_ms}", font_size=dp(12),
                                     color=COLOR_INK, size_hint_x=None, width=dp(50)))
            self.layout.add_widget(pb_row)


class WartungScreen(Screen):
    """Maintenance history screen – mirrors maintenance_menu.svg."""
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="wartung", **kwargs)
        self.app = app_ref
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        _set_bg(root, COLOR_PAPER)
        root.add_widget(_title_bar("WARTUNGSHISTORIE", date.today().strftime("%d.%m.%y")))

        scroll = ScrollView()
        self.layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
        self.layout.bind(minimum_height=self.layout.setter("height"))
        _set_bg(self.layout, COLOR_PAPER)
        scroll.add_widget(self.layout)
        root.add_widget(scroll)

        root.add_widget(_bottom_bar([
            ("< Zurück", lambda: setattr(self.manager, "current", "home")),
        ]))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        self.layout.clear_widgets()
        data = self.app.data
        today = date.today()
        overdue_keys = maintenance_overdue(data)

        for task in MAINTENANCE_TASKS:
            key = task["key"]
            last = data["maintenance"].get(key)
            is_overdue = key in overdue_keys

            if last:
                last_date = date.fromisoformat(last)
                days_ago = (today - last_date).days
                due_in = task["interval_days"] - days_ago
                last_display = last_date.strftime("%d.%m.'%y")
                val_text = last_display if not is_overdue else f"! {last_display}"
            else:
                val_text = "--"

            name_text = ("! " if is_overdue else "") + task["name"]

            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52),
                            padding=(dp(8), dp(6)), spacing=dp(6))
            # First entry gets inverted background like the Badger SVG
            bg = COLOR_INK if task == MAINTENANCE_TASKS[0] and not is_overdue else COLOR_PAPER
            txt_c = COLOR_PAPER if bg == COLOR_INK else COLOR_INK
            _set_bg(row, bg)

            row.add_widget(_label(name_text, font_size=dp(14),
                                  bold=(is_overdue or bg == COLOR_INK),
                                  color=txt_c if not is_overdue else COLOR_INK,
                                  halign="left"))
            row.add_widget(_label(val_text, font_size=dp(11),
                                  color=COLOR_INK_DIM if bg != COLOR_INK else COLOR_PAPER,
                                  halign="right"))

            def _mark_done(_, k=key):
                data["maintenance"][k] = _today()
                new_ach = check_achievements(data)
                save_data(data)
                self._refresh()
                for ach_key in new_ach:
                    show_achievement_popup(ach_key)

            done_btn = _button("Erledigt", on_press=_mark_done,
                               bg=COLOR_PAPER if bg == COLOR_INK else COLOR_INK,
                               text_color=COLOR_INK if bg == COLOR_INK else COLOR_PAPER,
                               font_size=dp(12), size_hint_x=None, width=dp(80))
            row.add_widget(done_btn)
            self.layout.add_widget(row)
            self.layout.add_widget(_separator())


class AchievementsScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="achievements", **kwargs)
        self.app = app_ref
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", spacing=0)
        _set_bg(root, COLOR_PAPER)
        root.add_widget(_title_bar("ACHIEVEMENTS", date.today().strftime("%d.%m.%y")))

        scroll = ScrollView()
        self.layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
        self.layout.bind(minimum_height=self.layout.setter("height"))
        _set_bg(self.layout, COLOR_PAPER)
        scroll.add_widget(self.layout)
        root.add_widget(scroll)

        root.add_widget(_bottom_bar([
            ("< Zurück", lambda: setattr(self.manager, "current", "home")),
        ]))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        self.layout.clear_widgets()
        data = self.app.data
        unlocked = data["achievements"]
        total = len(ACHIEVEMENT_DEFINITIONS)
        done = len(unlocked)

        summary = BoxLayout(size_hint_y=None, height=dp(28), padding=(dp(8), dp(4)))
        _set_bg(summary, COLOR_PAPER)
        summary.add_widget(_label(f"{done}/{total} freigeschaltet",
                                  font_size=dp(12), color=COLOR_INK))
        self.layout.add_widget(summary)

        pb_row = BoxLayout(size_hint_y=None, height=dp(20), padding=(dp(8), dp(3)))
        _set_bg(pb_row, COLOR_PAPER)
        pb_row.add_widget(_eink_progress_bar(done, total))
        self.layout.add_widget(pb_row)
        self.layout.add_widget(_separator())

        categories = {}
        for key, defn in ACHIEVEMENT_DEFINITIONS.items():
            categories.setdefault(defn["category"], []).append(key)

        for cat, keys in categories.items():
            self.layout.add_widget(_section_header(cat.upper()))
            for key in keys:
                defn = ACHIEVEMENT_DEFINITIONS[key]
                is_unlocked = key in unlocked
                icon = "[*]" if is_unlocked else "[ ]"
                color = COLOR_INK if is_unlocked else COLOR_INK_DIM
                right = unlocked[key] if is_unlocked else defn["desc"]

                row = BoxLayout(orientation="horizontal", size_hint_y=None,
                                height=dp(42), padding=(dp(8), dp(5)), spacing=dp(6))
                _set_bg(row, COLOR_PAPER)
                row.add_widget(_label(icon, font_size=dp(12), color=color,
                                      size_hint_x=None, width=dp(28)))
                row.add_widget(_label(defn["name"], font_size=dp(13),
                                      bold=is_unlocked, color=color, halign="left"))
                row.add_widget(_label(right, font_size=dp(11),
                                      color=COLOR_INK_DIM, halign="right"))
                self.layout.add_widget(row)
                self.layout.add_widget(_separator())


# ---------------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------------

class BeanOSApp(App):
    def build(self):
        self.title = "beanOS"
        self.data = load_data()
        Window.clearcolor = COLOR_PAPER

        sm = ScreenManager()
        sm.add_widget(HomeScreen(app_ref=self))
        sm.add_widget(StatsScreen(app_ref=self))
        sm.add_widget(WartungScreen(app_ref=self))
        sm.add_widget(AchievementsScreen(app_ref=self))
        sm.current = "home"
        return sm

    def on_stop(self):
        save_data(self.data)


if __name__ == "__main__":
    BeanOSApp().run()
