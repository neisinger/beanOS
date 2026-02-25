# beanOS Android

> **Smart Coffee Consumption Tracker – Android Companion App**

A [Kivy](https://kivy.org/)-based Android app that brings the full beanOS coffee-tracking experience to your smartphone. It shares the same data model and achievement system as the [Badger2040 E-Ink version](../README.md).

---

## ✨ Features

| Feature | Details |
|---------|---------|
| ☕ **8 drink types** | Espresso, Cappuccino, Lungo, Iced Latte, Affogato, Shakerato, Espresso Tonic, Other |
| 🏆 **15 Achievements** | Identical to the Badger2040 version |
| 📊 **Statistics** | Today, totals, streaks, caffeine & bean consumption |
| 🔥 **Streak tracking** | Consecutive-day counter with progress bar |
| 💾 **Local storage** | Data saved to `beanos_data.json` on-device |

---

## 🚀 Quick Start (Desktop / Testing)

```bash
pip install kivy
cd android
python main.py
```

---

## 📱 Build for Android

### Prerequisites

```bash
# Install buildozer and dependencies
pip install buildozer cython

# On Debian/Ubuntu also install:
sudo apt install -y \
    git zip unzip openjdk-17-jdk python3-pip \
    autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 \
    cmake libffi-dev libssl-dev
```

### Build

```bash
cd android
buildozer android debug
```

The signed debug APK will be written to `android/bin/beanos-1.0.0-debug.apk`.

### Deploy directly to a connected device

```bash
buildozer android debug deploy run
```

> **Note:** The first build downloads the Android NDK/SDK and can take 20–40 minutes depending on your connection speed.

---

## 📂 File Layout

```
android/
├── main.py          # Kivy app (all logic + UI)
├── buildozer.spec   # Android build configuration
└── README.md        # This file
```

App data is written to the app's private storage directory on Android as `beanos_data.json`.

---

## 🔗 Related

- [Badger2040 E-Ink version](../README.md) – the original MicroPython hardware app
- [ROADMAP](../ROADMAP.md) – project roadmap and future ideas

---

## 📄 License

GNU GPLv3 – see [LICENSE](../LICENSE)

This code must not be used by fascists! No code for the AfD, Musk or Trump!
