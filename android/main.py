#!/usr/bin/env python3
"""
beanOS Android – Coffee Consumption Tracker
============================================

A Kivy-based Android companion app for beanOS.
Tracks coffee consumption, achievements and statistics –
the same data model as the Badger2040 version.

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
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_FILE = "beanos_data.json"

DRINKS = [
    "Espresso",
    "Cappuccino",
    "Lungo",
    "Iced Latte",
    "Affogato",
    "Shakerato",
    "Espresso Tonic",
    "Other",
]

# Caffeine estimates in mg
CAFFEINE_MG = {
    "Espresso": 63,
    "Cappuccino": 63,
    "Lungo": 80,
    "Iced Latte": 63,
    "Affogato": 63,
    "Shakerato": 63,
    "Espresso Tonic": 63,
    "Other": 63,
}

# Bean usage in grams per drink
BEAN_GRAMS = {
    "Espresso": 7,
    "Cappuccino": 7,
    "Lungo": 10,
    "Iced Latte": 14,
    "Affogato": 7,
    "Shakerato": 7,
    "Espresso Tonic": 7,
    "Other": 7,
}

# ---------------------------------------------------------------------------
# Colour palette (matching beanOS dark-coffee theme)
# ---------------------------------------------------------------------------

COLOR_BG = (0.12, 0.07, 0.04, 1)       # very dark brown
COLOR_CARD = (0.22, 0.13, 0.07, 1)     # medium dark brown
COLOR_ACCENT = (0.80, 0.50, 0.10, 1)   # golden amber
COLOR_TEXT = (0.95, 0.90, 0.80, 1)     # cream
COLOR_SUCCESS = (0.20, 0.65, 0.30, 1)  # green
COLOR_WARN = (0.85, 0.35, 0.10, 1)     # orange-red
COLOR_BTN = (0.35, 0.20, 0.08, 1)      # mid brown

# ---------------------------------------------------------------------------
# Achievement definitions (identical to Badger2040 version)
# ---------------------------------------------------------------------------

ACHIEVEMENT_DEFINITIONS = {
    "first_coffee":        {"name": "Erster Kaffee",         "desc": "Dein allererster Kaffee!",              "category": "Meilensteine"},
    "coffee_10":           {"name": "Kaffee-Starter",        "desc": "10 Kaffees getrunken",                  "category": "Meilensteine"},
    "coffee_50":           {"name": "Kaffee-Fan",            "desc": "50 Kaffees getrunken",                  "category": "Meilensteine"},
    "coffee_100":          {"name": "Kaffee-Liebhaber",      "desc": "100 Kaffees getrunken",                 "category": "Meilensteine"},
    "coffee_500":          {"name": "Kaffee-Experte",        "desc": "500 Kaffees getrunken",                 "category": "Meilensteine"},
    "coffee_1000":         {"name": "Kaffee-Meister",        "desc": "1000 Kaffees getrunken",                "category": "Meilensteine"},
    "streak_7":            {"name": "Consistency Expert",    "desc": "7 Tage in Folge Kaffee",               "category": "Streaks"},
    "streak_30":           {"name": "Consistency Master",    "desc": "30 Tage in Folge Kaffee",              "category": "Streaks"},
    "stay_cool":           {"name": "Stay Cool",             "desc": "Ersten Iced Latte getrunken",           "category": "Spezialgetränke"},
    "dessert":             {"name": "Dessert",               "desc": "Ersten Affogato getrunken",             "category": "Spezialgetränke"},
    "shaker":              {"name": "Shake it!",             "desc": "Ersten Shakerato getrunken",            "category": "Spezialgetränke"},
    "tonic":               {"name": "Tonic Twist",           "desc": "Ersten Espresso Tonic getrunken",       "category": "Spezialgetränke"},
    "clean_machine":       {"name": "Saubere Maschine",      "desc": "Erste Wartung durchgeführt",            "category": "Wartung"},
    "barista":             {"name": "Barista",               "desc": "Alle Getränketypen probiert",           "category": "Experimentell"},
    "happy_bean_day":      {"name": "Happy Bean Day",        "desc": "10 Kaffees an einem Tag",              "category": "Experimentell"},
}

# ---------------------------------------------------------------------------
# Data layer
# ---------------------------------------------------------------------------

def _today() -> str:
    return date.today().isoformat()


def load_data() -> dict:
    """Load persisted data or return a fresh default structure."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return _default_data()


def _default_data() -> dict:
    return {
        "log": {},            # { "YYYY-MM-DD": { drink: count, ... } }
        "achievements": {},   # { achievement_key: "YYYY-MM-DD" }
    }


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def today_counts(data: dict) -> dict:
    return data["log"].get(_today(), {})


def total_counts(data: dict) -> dict:
    totals = {d: 0 for d in DRINKS}
    for day_entry in data["log"].values():
        for drink, count in day_entry.items():
            if drink in totals:
                totals[drink] += count
    return totals


def total_coffee(data: dict) -> int:
    return sum(total_counts(data).values())


def add_drink(data: dict, drink: str) -> None:
    today = _today()
    data["log"].setdefault(today, {})
    data["log"][today][drink] = data["log"][today].get(drink, 0) + 1


def calculate_streak(data: dict) -> int:
    """Return the current consecutive-day streak."""
    streak = 0
    check = date.today()
    while True:
        if data["log"].get(check.isoformat()):
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak


def check_achievements(data: dict) -> list:
    """Return list of newly unlocked achievement keys."""
    unlocked = data["achievements"]
    new_keys = []
    today = _today()
    tc = total_coffee(data)

    milestones = [
        (1,    "first_coffee"),
        (10,   "coffee_10"),
        (50,   "coffee_50"),
        (100,  "coffee_100"),
        (500,  "coffee_500"),
        (1000, "coffee_1000"),
    ]
    for threshold, key in milestones:
        if tc >= threshold and key not in unlocked:
            unlocked[key] = today
            new_keys.append(key)

    day_counts = today_counts(data)

    # Special drink achievements
    drink_achievements = [
        ("Iced Latte",      "stay_cool"),
        ("Affogato",        "dessert"),
        ("Shakerato",       "shaker"),
        ("Espresso Tonic",  "tonic"),
    ]
    for drink, key in drink_achievements:
        if day_counts.get(drink, 0) > 0 and key not in unlocked:
            unlocked[key] = today
            new_keys.append(key)

    # Barista: all drink types tried at least once
    all_tried = all(
        any(entry.get(d, 0) > 0 for entry in data["log"].values())
        for d in DRINKS
    )
    if all_tried and "barista" not in unlocked:
        unlocked["barista"] = today
        new_keys.append("barista")

    # Happy Bean Day: 10 coffees in a single day
    if sum(day_counts.values()) >= 10 and "happy_bean_day" not in unlocked:
        unlocked["happy_bean_day"] = today
        new_keys.append("happy_bean_day")

    # Streak achievements
    streak = calculate_streak(data)
    if streak >= 7 and "streak_7" not in unlocked:
        unlocked["streak_7"] = today
        new_keys.append("streak_7")
    if streak >= 30 and "streak_30" not in unlocked:
        unlocked["streak_30"] = today
        new_keys.append("streak_30")

    return new_keys


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def _label(text, font_size=dp(16), bold=False, color=COLOR_TEXT, **kw):
    return Label(
        text=text,
        font_size=font_size,
        bold=bold,
        color=color,
        **kw,
    )


def _button(text, on_press=None, bg=COLOR_BTN, font_size=dp(15), **kw):
    btn = Button(
        text=text,
        font_size=font_size,
        background_normal="",
        background_color=bg,
        color=COLOR_TEXT,
        **kw,
    )
    if on_press:
        btn.bind(on_press=on_press)
    return btn


def _nav_bar(screen_manager, current):
    """Bottom navigation bar shared by all screens."""
    bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52))
    screens = [
        ("🏠 Home",         "home"),
        ("☕ Getränke",     "drinks"),
        ("📊 Statistiken",  "stats"),
        ("🏆 Achievements", "achievements"),
    ]
    for label, name in screens:
        color = COLOR_ACCENT if name == current else COLOR_BTN
        btn = _button(label, bg=color, font_size=dp(13))
        btn.screen_name = name

        def _go(instance, sm=screen_manager):
            sm.current = instance.screen_name

        btn.bind(on_press=_go)
        bar.add_widget(btn)
    return bar


def _show_achievement_popup(key):
    defn = ACHIEVEMENT_DEFINITIONS.get(key, {})
    name = defn.get("name", key)
    desc = defn.get("desc", "")
    content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
    content.add_widget(_label("🏆 Achievement freigeschaltet!", font_size=dp(18), bold=True, color=COLOR_ACCENT))
    content.add_widget(_label(name, font_size=dp(20), bold=True))
    content.add_widget(_label(desc, font_size=dp(15)))
    popup = Popup(
        title="",
        content=content,
        size_hint=(0.85, 0.45),
        background_color=COLOR_CARD,
        separator_color=COLOR_ACCENT,
    )
    content.add_widget(_button("OK 🎉", on_press=lambda *_: popup.dismiss(), bg=COLOR_SUCCESS))
    popup.open()
    # Auto-close after 4 seconds
    Clock.schedule_once(lambda dt: popup.dismiss(), 4)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

class HomeScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="home", **kwargs)
        self.app = app_ref
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        # Title bar
        title_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
        )
        title_bar.add_widget(
            _label("☕ beanOS", font_size=dp(26), bold=True, color=COLOR_ACCENT)
        )
        root.add_widget(title_bar)

        # Today summary card
        self.today_label = _label("", font_size=dp(22), bold=True)
        self.streak_label = _label("", font_size=dp(15), color=COLOR_ACCENT)
        self.caffeine_label = _label("", font_size=dp(14))

        card = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(12),
            size_hint_y=None,
            height=dp(110),
        )
        card.add_widget(self.today_label)
        card.add_widget(self.streak_label)
        card.add_widget(self.caffeine_label)
        root.add_widget(card)

        # Quick-add buttons for the two most common drinks
        quick_label = _label("Schnell hinzufügen:", font_size=dp(15), size_hint_y=None, height=dp(28))
        root.add_widget(quick_label)

        quick_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(80))
        for drink in ("Espresso", "Cappuccino"):
            d = drink
            btn = _button(
                f"+ {d}",
                on_press=lambda _, drink=d: self._add(drink),
                bg=COLOR_ACCENT,
                font_size=dp(18),
            )
            quick_grid.add_widget(btn)
        root.add_widget(quick_grid)

        # Spacer
        root.add_widget(Label())

        # Nav bar
        root.add_widget(_nav_bar(self.manager, "home"))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        data = self.app.data
        tc_today = sum(today_counts(data).values())
        tc_total = total_coffee(data)
        streak = calculate_streak(data)

        self.today_label.text = f"Heute: {tc_today} ☕   |   Gesamt: {tc_total}"
        self.streak_label.text = f"🔥 Streak: {streak} Tage"

        caffeine_today = sum(
            CAFFEINE_MG.get(d, 63) * c
            for d, c in today_counts(data).items()
        )
        self.caffeine_label.text = f"⚡ Koffein heute: ~{caffeine_today} mg"

    def _add(self, drink):
        add_drink(self.app.data, drink)
        new_achievements = check_achievements(self.app.data)
        save_data(self.app.data)
        self._refresh()
        for key in new_achievements:
            _show_achievement_popup(key)


class DrinksScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="drinks", **kwargs)
        self.app = app_ref
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        root.add_widget(
            _label("☕ Getränke hinzufügen", font_size=dp(20), bold=True,
                   size_hint_y=None, height=dp(44))
        )

        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, padding=dp(4))
        grid.bind(minimum_height=grid.setter("height"))

        self.count_labels = {}
        for drink in DRINKS:
            d = drink
            card = BoxLayout(
                orientation="vertical",
                spacing=dp(4),
                padding=dp(8),
                size_hint_y=None,
                height=dp(90),
            )
            name_lbl = _label(d, font_size=dp(15), bold=True, size_hint_y=None, height=dp(24))
            count_lbl = _label("0", font_size=dp(20), color=COLOR_ACCENT,
                               size_hint_y=None, height=dp(28))
            add_btn = _button(
                "+ Hinzufügen",
                on_press=lambda _, drink=d: self._add(drink),
                bg=COLOR_BTN,
                size_hint_y=None,
                height=dp(30),
            )
            card.add_widget(name_lbl)
            card.add_widget(count_lbl)
            card.add_widget(add_btn)
            grid.add_widget(card)
            self.count_labels[d] = count_lbl

        scroll.add_widget(grid)
        root.add_widget(scroll)
        root.add_widget(_nav_bar(self.manager, "drinks"))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        counts = today_counts(self.app.data)
        for drink, lbl in self.count_labels.items():
            lbl.text = str(counts.get(drink, 0))

    def _add(self, drink):
        add_drink(self.app.data, drink)
        new_achievements = check_achievements(self.app.data)
        save_data(self.app.data)
        self._refresh()
        for key in new_achievements:
            _show_achievement_popup(key)


class StatsScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="stats", **kwargs)
        self.app = app_ref
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        root.add_widget(
            _label("📊 Statistiken", font_size=dp(20), bold=True,
                   size_hint_y=None, height=dp(44))
        )

        scroll = ScrollView()
        self.stats_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
            padding=dp(4),
        )
        self.stats_layout.bind(minimum_height=self.stats_layout.setter("height"))
        scroll.add_widget(self.stats_layout)
        root.add_widget(scroll)
        root.add_widget(_nav_bar(self.manager, "stats"))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        self.stats_layout.clear_widgets()
        data = self.app.data
        today = _today()
        t_counts = today_counts(data)
        tot_counts = total_counts(data)
        streak = calculate_streak(data)
        total_days = len(data["log"])
        tc_total = total_coffee(data)

        def row(text, value, color=COLOR_TEXT):
            box = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(32),
            )
            box.add_widget(_label(text, font_size=dp(15), halign="left"))
            box.add_widget(_label(str(value), font_size=dp(15), bold=True,
                                  color=color, halign="right"))
            return box

        self.stats_layout.add_widget(
            _label("— Heute —", font_size=dp(16), bold=True, color=COLOR_ACCENT,
                   size_hint_y=None, height=dp(30))
        )
        for drink in DRINKS:
            c = t_counts.get(drink, 0)
            if c:
                self.stats_layout.add_widget(row(drink, c, COLOR_ACCENT))

        today_total = sum(t_counts.values())
        caffeine_today = sum(CAFFEINE_MG.get(d, 63) * c for d, c in t_counts.items())
        beans_today = sum(BEAN_GRAMS.get(d, 7) * c for d, c in t_counts.items())
        self.stats_layout.add_widget(row("Gesamt heute", today_total))
        self.stats_layout.add_widget(row("Koffein heute", f"~{caffeine_today} mg"))
        self.stats_layout.add_widget(row("Bohnen heute", f"~{beans_today} g"))

        self.stats_layout.add_widget(
            _label("— Gesamt —", font_size=dp(16), bold=True, color=COLOR_ACCENT,
                   size_hint_y=None, height=dp(30))
        )
        for drink in DRINKS:
            c = tot_counts.get(drink, 0)
            if c:
                self.stats_layout.add_widget(row(drink, c))

        total_beans = sum(BEAN_GRAMS.get(d, 7) * c for d, c in tot_counts.items())
        bean_packs = total_beans / 250  # assuming 250 g packs

        self.stats_layout.add_widget(row("Alle Kaffees", tc_total, COLOR_ACCENT))
        self.stats_layout.add_widget(row("Tage erfasst", total_days))
        self.stats_layout.add_widget(row("Aktueller Streak", f"{streak} Tage", COLOR_ACCENT))
        self.stats_layout.add_widget(row("Bohnen gesamt", f"~{total_beans} g"))
        self.stats_layout.add_widget(row("Bohnenpakete (250 g)", f"~{bean_packs:.1f}"))

        # Streak progress bar towards next milestone
        next_milestone = 7 if streak < 7 else 30 if streak < 30 else None
        if next_milestone:
            self.stats_layout.add_widget(
                _label(f"Streak → {next_milestone} Tage", font_size=dp(14),
                       size_hint_y=None, height=dp(24))
            )
            pb = ProgressBar(
                max=next_milestone,
                value=min(streak, next_milestone),
                size_hint_y=None,
                height=dp(18),
            )
            self.stats_layout.add_widget(pb)


class AchievementsScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(name="achievements", **kwargs)
        self.app = app_ref
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        root.add_widget(
            _label("🏆 Achievements", font_size=dp(20), bold=True,
                   size_hint_y=None, height=dp(44))
        )

        scroll = ScrollView()
        self.ach_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            size_hint_y=None,
            padding=dp(4),
        )
        self.ach_layout.bind(minimum_height=self.ach_layout.setter("height"))
        scroll.add_widget(self.ach_layout)
        root.add_widget(scroll)
        root.add_widget(_nav_bar(self.manager, "achievements"))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        self.ach_layout.clear_widgets()
        data = self.app.data
        unlocked = data["achievements"]
        total = len(ACHIEVEMENT_DEFINITIONS)
        done = len(unlocked)

        self.ach_layout.add_widget(
            _label(f"{done}/{total} freigeschaltet", font_size=dp(15),
                   color=COLOR_ACCENT, size_hint_y=None, height=dp(28))
        )

        pb = ProgressBar(max=total, value=done, size_hint_y=None, height=dp(14))
        self.ach_layout.add_widget(pb)

        categories = {}
        for key, defn in ACHIEVEMENT_DEFINITIONS.items():
            cat = defn["category"]
            categories.setdefault(cat, []).append(key)

        for cat, keys in categories.items():
            self.ach_layout.add_widget(
                _label(f"— {cat} —", font_size=dp(15), bold=True,
                       color=COLOR_ACCENT, size_hint_y=None, height=dp(30))
            )
            for key in keys:
                defn = ACHIEVEMENT_DEFINITIONS[key]
                if key in unlocked:
                    icon = "✅"
                    color = COLOR_SUCCESS
                    date_str = f"  ({unlocked[key]})"
                else:
                    icon = "🔒"
                    color = (0.5, 0.5, 0.5, 1)
                    date_str = ""

                row = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(48),
                    spacing=dp(6),
                )
                row.add_widget(_label(icon, font_size=dp(18), size_hint_x=None, width=dp(30)))
                info = BoxLayout(orientation="vertical")
                info.add_widget(
                    _label(defn["name"] + date_str, font_size=dp(14), bold=True,
                           color=color, halign="left")
                )
                info.add_widget(
                    _label(defn["desc"], font_size=dp(12),
                           color=(0.75, 0.70, 0.60, 1), halign="left")
                )
                row.add_widget(info)
                self.ach_layout.add_widget(row)


# ---------------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------------

class BeanOSApp(App):
    def build(self):
        self.title = "beanOS"
        self.data = load_data()

        sm = ScreenManager()

        home = HomeScreen(app_ref=self)
        drinks = DrinksScreen(app_ref=self)
        stats = StatsScreen(app_ref=self)
        achievements = AchievementsScreen(app_ref=self)

        sm.add_widget(home)
        sm.add_widget(drinks)
        sm.add_widget(stats)
        sm.add_widget(achievements)

        sm.current = "home"
        return sm

    def on_stop(self):
        save_data(self.data)


if __name__ == "__main__":
    BeanOSApp().run()
