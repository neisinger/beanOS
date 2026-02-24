[app]

# App metadata
title = beanOS
package.name = beanos
package.domain = org.beanos

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# App version
version = 1.0.0

# Android requirements
requirements = python3,kivy==2.3.0

# Icon / splash (replace with real assets if available)
# icon.filename = %(source.dir)s/data/icon.png
# presplash.filename = %(source.dir)s/data/presplash.png

# Android orientation
orientation = landscape

# Permissions (none needed for local-only data storage)
android.permissions =

# Minimum Android API level
android.minapi = 21

# Target Android API level
android.api = 33

# NDK version (leave blank to let buildozer choose)
# android.ndk =

# Architecture
android.archs = arm64-v8a, armeabi-v7a

# Allow backup
android.allow_backup = True

[buildozer]

# Log level (0 = error, 1 = info, 2 = debug)
log_level = 2

# Warn when running as root
warn_on_root = 1
