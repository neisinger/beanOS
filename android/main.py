#!/usr/bin/env python3
"""
beanOS Android – Coffee Consumption Tracker
============================================

A Kivy-based Android companion app for beanOS.
Tracks coffee consumption, achievements and statistics –
the same data model as the Badger2040 version.

Visual style: E-Paper / E-Ink (white background, black ink, bordered boxes,
separator lines), mirroring the Pimoroni Badger2040 display aesthetic.

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
# E-Paper colour palette (Badger2040 E-Ink display aesthetics)
# ---------------------------------------------------------------------------

COLOR_PAPER = (1, 1, 1, 1)               # white paper
COLOR_INK = (0, 0, 0, 1)                 # black ink
COLOR_INK_DIM = (0.45, 0.45, 0.45, 1)   # gray (secondary / locked)

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
# UI helpers – E-Paper style
# ---------------------------------------------------------------------------

def _set_bg(widget, color):
    """Attach a solid background colour to a widget via canvas.before."""
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
        text=text,
        font_size=font_size,
        background_normal="",
        background_color=bg,
        color=text_color,
        **kw,
    )
    if on_press:
        btn.bind(on_press=on_press)
    return btn


def _title_bar(text, right_text=""):
    """Full-width black title bar with white text – mirrors Badger2040 style."""
    bar = BoxLayout(
        orientation="horizontal",
        size_hint_y=None,
        height=dp(44),
        padding=(dp(10), dp(6)),
        spacing=dp(4),
    )
    _set_bg(bar, COLOR_INK)
    bar.add_widget(_label(text, font_size=dp(17), bold=True, color=COLOR_PAPER,
                          halign="left"))
    if right_text:
        bar.add_widget(_label(right_text, font_size=dp(12), color=COLOR_PAPER,
                              halign="right"))
    return bar


def _section_header(text):
    """Smaller black bar for sub-section headings."""
    bar = BoxLayout(size_hint_y=None, height=dp(28), padding=(dp(8), dp(4)))
    _set_bg(bar, COLOR_INK)
    bar.add_widget(_label(text, font_size=dp(13), bold=True, color=COLOR_PAPER))
    return bar


def _separator():
    """1 dp horizontal black line – matches E-Ink separator style."""
    sep = BoxLayout(size_hint_y=None, height=dp(1))
    _set_bg(sep, COLOR_INK)
    return sep


def _bordered_box(**kw):
    """Return (outer, inner): 1 dp black border around a white interior card."""
    outer = BoxLayout(padding=dp(1), **kw)
    _set_bg(outer, COLOR_INK)
    inner = BoxLayout(orientation="vertical", padding=dp(6), spacing=dp(2))
    _set_bg(inner, COLOR_PAPER)
    outer.add_widget(inner)
    return outer, inner


def _eink_progress_bar(current, maximum):
    """E-Ink progress bar: white box, black outline, black fill."""
    outer = BoxLayout(size_hint_y=None, height=dp(16), padding=dp(1))
    _set_bg(outer, COLOR_INK)
    inner = BoxLayout()
    _set_bg(inner, COLOR_PAPER)
    ratio = min(current / maximum, 1.0) if maximum > 0 else 0.0
    if ratio > 0:
        fill = BoxLayout(size_hint_x=ratio)
        _set_bg(fill, COLOR_INK)
        inner.add_widget(fill)
    remainder = max(0.0, 1.0 - ratio)
    if remainder > 0:
        space = BoxLayout(size_hint_x=remainder)
        _set_bg(space, COLOR_PAPER)
        inner.add_widget(space)
    outer.add_widget(inner)
    return outer


def _nav_bar(screen, current):
    """Bottom nav bar: white background, black top border, active tab inverted."""
    wrapper = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(56))
    _set_bg(wrapper, COLOR_PAPER)
    wrapper.add_widget(_separator())

    bar = BoxLayout(orientation="horizontal")
    _set_bg(bar, COLOR_PAPER)

    screens = [
        ("Home",         "home"),
        ("Getränke",     "drinks"),
        ("Statistik",    "stats"),
        ("Achievements", "achievements"),
    ]
    for i, (lbl_text, name) in enumerate(screens):
        if name == current:
            btn = _button(lbl_text, bg=COLOR_INK, text_color=COLOR_PAPER,
                          font_size=dp(12))
        else:
            btn = _button(lbl_text, bg=COLOR_PAPER, text_color=COLOR_INK,
                          font_size=dp(12))
        btn.screen_name = name

        def _go(instance, s=screen):
            if s.manager:
                s.manager.current = instance.screen_name

        btn.bind(on_press=_go)
        bar.add_widget(btn)

        if i < len(screens) - 1:
            vsep = BoxLayout(size_hint_x=None, width=dp(1))
            _set_bg(vsep, COLOR_INK)
            bar.add_widget(vsep)

    wrapper.add_widget(bar)
    return wrapper


def _show_achievement_popup(key):
    defn = ACHIEVEMENT_DEFINITIONS.get(key, {})
    name = defn.get("name", key)
    desc = defn.get("desc", "")

    content = BoxLayout(orientation="vertical", padding=0, spacing=0)
    _set_bg(content, COLOR_PAPER)
    content.add_widget(_title_bar("[*] Achievement freigeschaltet!"))

    body = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))
    _set_bg(body, COLOR_PAPER)
    body.add_widget(_label(name, font_size=dp(20), bold=True, color=COLOR_INK))
    body.add_widget(_separator())
    body.add_widget(_label(desc, font_size=dp(14), color=COLOR_INK))
    body.add_widget(BoxLayout())  # spacer

    ok_btn = _button("OK", bg=COLOR_INK, text_color=COLOR_PAPER,
                     size_hint_y=None, height=dp(40))
    body.add_widget(ok_btn)
    content.add_widget(body)

    popup = Popup(
        title="",
        content=content,
        size_hint=(0.88, 0.52),
        background_color=COLOR_PAPER,
        separator_height=0,
        title_size=0,
    )
    ok_btn.bind(on_press=lambda *_: popup.dismiss())
    popup.open()
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
        root = BoxLayout(orientation="vertical", spacing=0)
        _set_bg(root, COLOR_PAPER)

        # Black title bar (full width, white text) – Badger2040 style
        root.add_widget(_title_bar("beanOS", date.today().strftime("%d.%m.%y")))

        # ── Landscape main area ──────────────────────────────────────────────
        # Left column: three bordered counter boxes + info strip
        # Right column: two large quick-add buttons (portrait buttons side-by-side)
        body = BoxLayout(orientation="horizontal", spacing=0)
        _set_bg(body, COLOR_PAPER)

        # Left column: counters + streak/caffeine
        left_column = BoxLayout(orientation="vertical", spacing=0,
                                size_hint_x=0.6)
        _set_bg(left_column, COLOR_PAPER)

        counter_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=0.6,
            spacing=dp(6),
            padding=(dp(6), dp(6)),
        )
        _set_bg(counter_row, COLOR_PAPER)
        for attr, caption in (
            ("espresso_lbl", "ESPRESSO"),
            ("cappuccino_lbl", "CAPPUCCINO"),
            ("total_lbl", "GESAMT"),
        ):
            outer, inner = _bordered_box()
            count_lbl = _label("0", font_size=dp(28), bold=True, color=COLOR_INK)
            name_lbl = _label(caption, font_size=dp(9), color=COLOR_INK)
            inner.add_widget(count_lbl)
            inner.add_widget(name_lbl)
            counter_row.add_widget(outer)
            setattr(self, attr, count_lbl)
        left_column.add_widget(counter_row)
        left_column.add_widget(_separator())

        info_box = BoxLayout(
            orientation="horizontal",
            size_hint_y=0.4,
            padding=(dp(10), dp(4)),
            spacing=dp(16),
        )
        _set_bg(info_box, COLOR_PAPER)
        self.streak_label = _label("Streak: 0 Tage", font_size=dp(13),
                                   color=COLOR_INK, halign="left")
        self.caffeine_label = _label("Koffein: ~0 mg", font_size=dp(12),
                                     color=COLOR_INK_DIM, halign="right")
        info_box.add_widget(self.streak_label)
        info_box.add_widget(self.caffeine_label)
        left_column.add_widget(info_box)

        body.add_widget(left_column)

        # Vertical separator between columns
        vsep = BoxLayout(size_hint_x=None, width=dp(1))
        _set_bg(vsep, COLOR_INK)
        body.add_widget(vsep)

        # Right column: two large quick-add buttons stacked vertically
        quick_add_column = BoxLayout(orientation="vertical", spacing=0,
                                     size_hint_x=0.4)
        _set_bg(quick_add_column, COLOR_PAPER)
        for i, drink in enumerate(("Espresso", "Cappuccino")):
            btn = _button(
                f"+ {drink.upper()}",
                on_press=lambda _, d=drink: self._add(d),
                bg=COLOR_INK,
                text_color=COLOR_PAPER,
                font_size=dp(16),
            )
            quick_add_column.add_widget(btn)
            if i == 0:
                quick_add_column.add_widget(_separator())
        body.add_widget(quick_add_column)

        root.add_widget(body)
        root.add_widget(_nav_bar(self, "home"))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        data = self.app.data
        t = today_counts(data)
        streak = calculate_streak(data)

        self.espresso_lbl.text = str(t.get("Espresso", 0))
        self.cappuccino_lbl.text = str(t.get("Cappuccino", 0))
        self.total_lbl.text = str(sum(t.values()))
        self.streak_label.text = f"Streak: {streak} Tage"
        caffeine = sum(CAFFEINE_MG.get(d, 63) * c for d, c in t.items())
        self.caffeine_label.text = f"Koffein heute: ~{caffeine} mg"

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
        root = BoxLayout(orientation="vertical", spacing=0)
        _set_bg(root, COLOR_PAPER)
        root.add_widget(_title_bar("GETRÄNKE", date.today().strftime("%d.%m.%y")))

        scroll = ScrollView()
        container = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
        container.bind(minimum_height=container.setter("height"))
        _set_bg(container, COLOR_PAPER)

        self.count_labels = {}
        for drink in DRINKS:
            d = drink
            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(52),
                padding=(dp(12), dp(8)),
                spacing=dp(8),
            )
            _set_bg(row, COLOR_PAPER)
            row.add_widget(_label(d, font_size=dp(15), color=COLOR_INK,
                                  halign="left"))
            count_lbl = _label("0", font_size=dp(15), bold=True, color=COLOR_INK,
                               size_hint_x=None, width=dp(36))
            row.add_widget(count_lbl)
            self.count_labels[d] = count_lbl

            add_btn = _button(
                "+",
                on_press=lambda _, drink=d: self._add(drink),
                bg=COLOR_INK,
                text_color=COLOR_PAPER,
                font_size=dp(20),
                size_hint_x=None,
                width=dp(44),
            )
            row.add_widget(add_btn)
            container.add_widget(row)
            container.add_widget(_separator())

        scroll.add_widget(container)
        root.add_widget(scroll)
        root.add_widget(_nav_bar(self, "drinks"))
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
        root = BoxLayout(orientation="vertical", spacing=0)
        _set_bg(root, COLOR_PAPER)
        root.add_widget(_title_bar("STATISTIKEN", date.today().strftime("%d.%m.%y")))

        scroll = ScrollView()
        self.stats_layout = BoxLayout(orientation="vertical", size_hint_y=None,
                                      spacing=0)
        self.stats_layout.bind(minimum_height=self.stats_layout.setter("height"))
        _set_bg(self.stats_layout, COLOR_PAPER)
        scroll.add_widget(self.stats_layout)
        root.add_widget(scroll)
        root.add_widget(_nav_bar(self, "stats"))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        self.stats_layout.clear_widgets()
        data = self.app.data
        t_counts = today_counts(data)
        tot_counts = total_counts(data)
        streak = calculate_streak(data)
        total_days = len(data["log"])
        tc_total = total_coffee(data)

        def _row(text, value, dim=False):
            box = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40),
                padding=(dp(12), dp(6)),
            )
            _set_bg(box, COLOR_PAPER)
            c = COLOR_INK_DIM if dim else COLOR_INK
            box.add_widget(_label(text, font_size=dp(14), color=c, halign="left"))
            box.add_widget(_label(str(value), font_size=dp(14), bold=True,
                                  color=c, halign="right"))
            return box

        self.stats_layout.add_widget(_section_header("HEUTE"))
        for drink in DRINKS:
            c = t_counts.get(drink, 0)
            self.stats_layout.add_widget(_row(drink, c if c else "-", dim=(c == 0)))
            self.stats_layout.add_widget(_separator())

        today_total = sum(t_counts.values())
        caffeine_today = sum(CAFFEINE_MG.get(d, 63) * c for d, c in t_counts.items())
        beans_today = sum(BEAN_GRAMS.get(d, 7) * c for d, c in t_counts.items())
        self.stats_layout.add_widget(_row("GESAMT HEUTE", today_total))
        self.stats_layout.add_widget(_separator())
        self.stats_layout.add_widget(_row("Koffein", f"~{caffeine_today} mg"))
        self.stats_layout.add_widget(_separator())
        self.stats_layout.add_widget(_row("Bohnen heute", f"~{beans_today} g"))
        self.stats_layout.add_widget(_separator())

        self.stats_layout.add_widget(_section_header("GESAMT"))
        self.stats_layout.add_widget(_row("Alle Kaffees", tc_total))
        self.stats_layout.add_widget(_separator())
        self.stats_layout.add_widget(_row("Tage erfasst", total_days))
        self.stats_layout.add_widget(_separator())
        self.stats_layout.add_widget(_row("Aktueller Streak", f"{streak} Tage"))
        self.stats_layout.add_widget(_separator())

        total_beans = sum(BEAN_GRAMS.get(d, 7) * c for d, c in tot_counts.items())
        bean_packs = total_beans / 250
        self.stats_layout.add_widget(_row("Bohnen gesamt", f"~{total_beans} g"))
        self.stats_layout.add_widget(_separator())
        self.stats_layout.add_widget(_row("Bohnenpakete (250g)", f"~{bean_packs:.1f}"))
        self.stats_layout.add_widget(_separator())

        # E-Ink style streak progress bar
        next_milestone = 7 if streak < 7 else 30 if streak < 30 else None
        if next_milestone:
            self.stats_layout.add_widget(
                _section_header(f"STREAK ZIEL: {next_milestone} TAGE")
            )
            pb_row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(26),
                padding=(dp(8), dp(4)),
                spacing=dp(6),
            )
            _set_bg(pb_row, COLOR_PAPER)
            pb_row.add_widget(_eink_progress_bar(streak, next_milestone))
            pb_row.add_widget(
                _label(f"{streak}/{next_milestone}", font_size=dp(12),
                       color=COLOR_INK, size_hint_x=None, width=dp(52))
            )
            self.stats_layout.add_widget(pb_row)


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
        self.ach_layout = BoxLayout(orientation="vertical", size_hint_y=None,
                                    spacing=0)
        self.ach_layout.bind(minimum_height=self.ach_layout.setter("height"))
        _set_bg(self.ach_layout, COLOR_PAPER)
        scroll.add_widget(self.ach_layout)
        root.add_widget(scroll)
        root.add_widget(_nav_bar(self, "achievements"))
        self.add_widget(root)

    def on_pre_enter(self, *_):
        self._refresh()

    def _refresh(self):
        self.ach_layout.clear_widgets()
        data = self.app.data
        unlocked = data["achievements"]
        total = len(ACHIEVEMENT_DEFINITIONS)
        done = len(unlocked)

        summary = BoxLayout(size_hint_y=None, height=dp(30), padding=(dp(8), dp(6)))
        _set_bg(summary, COLOR_PAPER)
        summary.add_widget(
            _label(f"{done}/{total} freigeschaltet", font_size=dp(13),
                   color=COLOR_INK)
        )
        self.ach_layout.add_widget(summary)

        pb_row = BoxLayout(size_hint_y=None, height=dp(22), padding=(dp(8), dp(3)))
        _set_bg(pb_row, COLOR_PAPER)
        pb_row.add_widget(_eink_progress_bar(done, total))
        self.ach_layout.add_widget(pb_row)
        self.ach_layout.add_widget(_separator())

        categories = {}
        for key, defn in ACHIEVEMENT_DEFINITIONS.items():
            categories.setdefault(defn["category"], []).append(key)

        for cat, keys in categories.items():
            self.ach_layout.add_widget(_section_header(cat.upper()))
            for key in keys:
                defn = ACHIEVEMENT_DEFINITIONS[key]
                is_unlocked = key in unlocked

                row = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(44),
                    padding=(dp(8), dp(6)),
                    spacing=dp(6),
                )
                _set_bg(row, COLOR_PAPER)

                icon_text = "[*]" if is_unlocked else "[ ]"
                color = COLOR_INK if is_unlocked else COLOR_INK_DIM
                row.add_widget(
                    _label(icon_text, font_size=dp(12), color=color,
                           size_hint_x=None, width=dp(30))
                )
                row.add_widget(
                    _label(defn["name"], font_size=dp(14), bold=is_unlocked,
                           color=color, halign="left")
                )
                right = unlocked[key] if is_unlocked else defn["desc"]
                row.add_widget(
                    _label(right, font_size=dp(11), color=COLOR_INK_DIM,
                           halign="right")
                )
                self.ach_layout.add_widget(row)
                self.ach_layout.add_widget(_separator())


# ---------------------------------------------------------------------------
# App entry point
# ---------------------------------------------------------------------------

class BeanOSApp(App):
    def build(self):
        self.title = "beanOS"
        self.data = load_data()
        Window.clearcolor = COLOR_PAPER

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
