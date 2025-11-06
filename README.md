# beanOS

beanOS is a Micropython application designed for the Badger2040 device. It tracks and logs your coffee consumption with gamification features, providing a simple interface to view statistics, reset counts, and unlock achievements.

This code must not be used by fascists! No code for the AfD or Musk or Trump!

## Features

### ☕ Coffee Tracking
- Track espresso, cappuccino, and 6 additional drink types
- Daily, weekly, and total statistics
- Bean consumption analytics
- Automatic data logging to CSV

### 🏆 Achievement System
- **Milestone Achievements**: Unlock rewards for 1, 10, 50, 100, 500, and 1000 coffees
- **Streak Achievements**: Keep your coffee habit going for 7 or 30 days straight
- **Special Drink Achievements**: Try new drinks like iced latte, affogato, or shakerato
- **Maintenance Achievements**: Keep your machine in perfect condition
- **Experimental Achievements**: Become a true barista by trying all drink types
- **Progress Tracking**: Visual progress bars for streak achievements
- **Achievement Notifications**: Full-screen celebrations when you unlock new achievements
- **Achievement Icon**: Daily star (★) in the title bar when you unlock achievements

### 🔧 Smart Maintenance System
- Automatic maintenance reminders based on time and usage
- 5 different maintenance types with custom intervals
- Visual warnings and quick completion logging
- Maintenance history tracking

## Installation

To install beanOS on your Badger2040:

### Prerequisites
- Pimoroni Badger2040 with MicroPython firmware
- Thonny IDE or similar MicroPython development environment
- USB cable for device connection

### Installation Steps
1. Connect your Badger2040 to your computer via USB
2. Open Thonny IDE and ensure the device is detected
3. Copy the `main.py` file content into Thonny's editor
4. Save the file to your Badger2040 as `main.py`
5. Copy the `maintenance_config.json` file to your Badger2040 root directory
6. Disconnect and restart the device

### Required Files
- **main.py** - Main application code
- **maintenance_config.json** - Maintenance task configuration

### Auto-Generated Files
The following files will be created automatically during use:
- **kaffee_log.csv** - Coffee consumption data log
- **achievements.json** - Achievement progress tracking
- **maintenance_status.json** - Maintenance completion tracking
- **current_date.txt** - Current date persistence
- **current_counts.txt** - Daily counter backup

## Technical Architecture

### Code Structure
The application is organized into the following main sections:
- **Hardware Initialization** - Display, buttons, LED setup
- **File Management** - Data persistence and configuration
- **Menu System** - Navigation and user interface
- **Achievement Engine** - Gamification and progress tracking
- **Maintenance System** - Automated reminders and logging
- **Statistics Engine** - Data analysis and reporting
- **Notification System** - User alerts and celebrations

### Data Flow
1. **Input**: Button presses → `button_pressed()` function
2. **Processing**: Update counters → Check achievements → Check maintenance
3. **Storage**: Save to CSV log and JSON status files
4. **Display**: Update screen via `update_display()` function

### Memory Management
- Minimal RAM usage for embedded environment
- Efficient file I/O operations
- Smart display update strategies (TURBO vs NORMAL modes)

## Usage

### Main screen
![main screen](images/beanOS_screen-6.jpg)
#### Buttons
- **a:**
Increments the espresso count
- **b:**
Increments the cappuccino count
- **c:**
Opens the additional drink menu
- **UP:**
Opens the main menu
- **DOWN:**
Switches to the next day and resets the daily counts

### Drink menu
![drink menu screen](images/beanOS_screen-5.jpg)
#### Buttons
- **a:**
Chooses the selected drink
- **c:**
Closes the menu
- **UP** & **DOWN:**
Navigate the menu

### Main menu
![main menu screen](images/beanOS_screen-4.jpg)
#### Buttons
- **a:**
Chooses the selected optoin
- **c:**
Closes the menu
- **UP** & **DOWN:**
Navigate the menu


#### Menu Options

- **Bohnen**: Opens the additional drink menu (same as Button C)
- **Statistiken anzeigen**: Displays total counts of espresso, cappuccino, and other drinks. Also shows bean consumption (grams per day, days per pack) and average coffee per day.
- **Tagesstatistiken zurücksetzen**: Resets the daily counts for espresso, cappuccino, and other drinks.
- **Datum ändern**: Allows you to change the current date.
- **Wartungshistorie**: View and manually log maintenance tasks. Select a task and press Button A to mark it as completed for today.
- **Achievements**: View your unlocked achievements organized by category. Navigate through your coffee accomplishments and see progress bars for incomplete streak achievements.
- **Information**: Displays version information and credits.

### Achievement Categories
![achievements screen](images/beanOS_achievements.jpg)

#### 🏅 Meilensteine (Milestones)
Unlock achievements for reaching coffee consumption milestones:
- **[1] Erster Kaffee**: Your very first coffee!
- **[10] Kaffee-Starter**: 10 coffees consumed
- **[50] Kaffee-Fan**: 50 coffees consumed  
- **[100] Kaffee-Liebhaber**: 100 coffees consumed
- **[500] Kaffee-Experte**: 500 coffees consumed
- **[1K] Kaffee-Meister**: 1000 coffees consumed

#### ⚡ Streaks
Maintain consistent coffee consumption:
- **[7d] Wochenentkämpfer**: 7 days in a row with coffee
- **[30d] Monatsmarathon**: 30 days in a row with coffee
- *Progress bars show your current streak progress for incomplete achievements*

#### 🍹 Spezialgetränke (Special Drinks)
Try different coffee varieties:
- **[IC] Stay Cool**: First iced latte consumed
- **[AF] Dessert**: First affogato consumed
- **[SH] Shake it!**: First shakerato consumed

#### 🔧 Wartung (Maintenance)
Keep your machine in perfect condition:
- **[CL] Saubere Maschine**: First maintenance completed
- **[WM] Wartungsmeister**: All maintenance tasks completed on time

#### 🧪 Experimentell (Experimental)
Master the art of coffee:
- **[BA] Barista**: All drink types tried
- **[HB] Happy Bean Day**: 10 coffees in a single day

### Bean Packs
You can select the current pack size in the menu. The statistics will show how many days a pack lasts and your average bean consumption per day.

### Maintenance Reminders
beanOS includes an intelligent maintenance reminder system that helps you keep your coffee machine in optimal condition.

#### Features:
- **Automatic Warnings**: The system automatically shows full-screen warnings when maintenance tasks are due
- **Smart Icon**: When you dismiss a warning with Button C, a small "!" icon appears next to the date as a subtle reminder
- **Quick Action**: Press Button A on a maintenance warning to mark the current task as completed
- **Menu Integration**: Use the "Wartungshistorie" menu to manually log maintenance tasks
- **Auto-Reset**: The warning icon automatically disappears when you log a maintenance task through the menu

#### Maintenance Tasks:
- **Cleaning** (every 7 days)
- **Descaling** (every 28 days) 
- **Brew Group Cleaning** (every 42 days OR after 150 drinks)
- **Grinder Cleaning** (every 56 days)
- **Deep Cleaning** (every 365 days)

#### Button Controls for Maintenance:
- **Button A**: Mark the current maintenance task as completed
- **Button C**: Hide the warning and show the small reminder icon instead

## Changelog

## Development & Customization

### Adding New Achievements
1. Add achievement definition to `get_achievement_definitions()`
2. Implement check logic in `check_achievements()`
3. Test with achievement notification system

### Modifying Maintenance Tasks
Edit `maintenance_config.json`:
```json
{
  "tasks": [
    {"name": "cleaning", "interval": 7},
    {"name": "brew_group_cleaning", "interval": 42, "drink_limit": 150}
  ]
}
```

### Configuration Options
- **Display Update Modes**: TURBO (fast) vs NORMAL (full refresh)
- **Achievement Categories**: Milestones, Streaks, Special, Maintenance, Experimental
- **Button Debouncing**: 0.2 second default debounce time
- **Auto-Sleep**: 15 seconds of inactivity

### Debug Features
- Console output for achievement debugging
- Error display system for configuration issues
- Achievement progress logging

### Performance Considerations
- Use TURBO display updates for frequent refreshes
- Minimize file I/O operations during active use
- Efficient CSV parsing for large log files
- Smart achievement checking (only when needed)

## Troubleshooting

### Common Issues
1. **"maintenance_config.json nicht gefunden"**
   - Ensure the file exists in the root directory
   - Check JSON syntax validity

2. **Achievements not unlocking**
   - Check console output for debug information
   - Verify achievement logic in `check_achievements()`

3. **Display not updating**
   - Force full refresh with `update_display(True)`
   - Check display update speed settings

4. **Data loss on restart**
   - Verify file write permissions
   - Check for corrupted JSON files

### File Recovery
If data files become corrupted:
1. Delete corrupted `.json` files (they will be recreated)
2. Backup `kaffee_log.csv` before any major changes
3. Use debug console to verify data integrity

## Changelog

### v2.3.3 (Current)
- 📝 **Documentation**: Comprehensive code documentation and comments
- 🏗️ **Architecture**: Improved code structure and organization  
- 📖 **README**: Extended technical documentation for developers
- 🔧 **Code Quality**: Added docstrings and inline comments throughout

### v2.3.2
- 📝 **Achievement Renaming**
- ✅ "Wochenentkämpfer" → "Consistency Expert" (7-day streak)
- ✅ "Monatsmarathon" → "Consistency Master" (30-day streak)

### v2.3.1
- 🐛 **Fixed**: Button B now correctly increments cappuccino count
- 🏆 **Improved**: Achievement checking for cappuccino button restored

### v2.3.0 
- 🏆 **New**: Complete achievement system with 20+ achievements
- 🔧 **New**: Smart maintenance reminders with visual warnings
- 📊 **Improved**: Enhanced statistics and tracking

## License

This project is licensed under the GNU GPLv3 License. See the LICENSE file for details.

## Author

Joao Neisinger
